package main

import (
	"encoding/json"
	"fmt"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"

	"github.com/go-chi/chi/v5"
)

func TestCryptoEndpoints_Authentication(t *testing.T) {
	apiKey := "test-secret-key"
	r := chi.NewRouter()
	r.Use(PQCMiddleware)

	r.Group(func(r chi.Router) {
		r.Use(AuthMiddleware(apiKey))

		r.Post("/gateway/rotate-crypto", func(w http.ResponseWriter, r *http.Request) {
			_ = globalRegistry.Rotate()
			w.WriteHeader(http.StatusOK)
		})

		r.Get("/gateway/crypto/status", func(w http.ResponseWriter, r *http.Request) {
			w.WriteHeader(http.StatusOK)
		})
	})

	// 1. Missing API key
	reqStatus := httptest.NewRequest("GET", "/gateway/crypto/status", nil)
	wStatus := httptest.NewRecorder()
	r.ServeHTTP(wStatus, reqStatus)
	if wStatus.Code != http.StatusUnauthorized {
		t.Errorf("Expected status 401 Unauthorized for missing API key, got %d", wStatus.Code)
	}

	reqRotate := httptest.NewRequest("POST", "/gateway/rotate-crypto", nil)
	wRotate := httptest.NewRecorder()
	r.ServeHTTP(wRotate, reqRotate)
	if wRotate.Code != http.StatusUnauthorized {
		t.Errorf("Expected status 401 Unauthorized for missing API key, got %d", wRotate.Code)
	}

	// 2. Incorrect API key
	reqStatusWrong := httptest.NewRequest("GET", "/gateway/crypto/status", nil)
	reqStatusWrong.Header.Set("X-API-KEY", "wrong-key")
	wStatusWrong := httptest.NewRecorder()
	r.ServeHTTP(wStatusWrong, reqStatusWrong)
	if wStatusWrong.Code != http.StatusUnauthorized {
		t.Errorf("Expected status 401 Unauthorized for wrong API key, got %d", wStatusWrong.Code)
	}

	// 3. Correct API key
	reqStatusCorrect := httptest.NewRequest("GET", "/gateway/crypto/status", nil)
	reqStatusCorrect.Header.Set("X-API-KEY", apiKey)
	wStatusCorrect := httptest.NewRecorder()
	r.ServeHTTP(wStatusCorrect, reqStatusCorrect)
	if wStatusCorrect.Code != http.StatusOK {
		t.Errorf("Expected status 200 OK for correct API key, got %d", wStatusCorrect.Code)
	}
}

func TestCryptoEndpoints_RotationAndTelemetry(t *testing.T) {
	apiKey := "test-secret-key"
	r := chi.NewRouter()
	r.Use(PQCMiddleware)

	r.Group(func(r chi.Router) {
		r.Use(AuthMiddleware(apiKey))

		r.Post("/gateway/rotate-crypto", func(w http.ResponseWriter, r *http.Request) {
			if err := globalRegistry.Rotate(); err != nil {
				http.Error(w, err.Error(), http.StatusInternalServerError)
				return
			}
			w.WriteHeader(http.StatusOK)
		})

		r.Get("/gateway/crypto/status", func(w http.ResponseWriter, r *http.Request) {
			globalRegistry.mu.RLock()
			activeKey := globalRegistry.ActiveKey
			graceCount := len(globalRegistry.GraceKeys)
			lastRotated := globalRegistry.LastRotated.Format(time.RFC3339)
			globalRegistry.mu.RUnlock()

			w.Header().Set("Content-Type", "application/json")
			json.NewEncoder(w).Encode(map[string]interface{}{
				"active_algorithm": "ML-KEM-768",
				"key_version":      activeKey.Version,
				"last_rotated":     lastRotated,
				"grace_keys_count": graceCount,
			})
		})
	})

	// Get initial status
	reqStatus := httptest.NewRequest("GET", "/gateway/crypto/status", nil)
	reqStatus.Header.Set("X-API-KEY", apiKey)
	wStatus := httptest.NewRecorder()
	r.ServeHTTP(wStatus, reqStatus)

	var initialStatus map[string]interface{}
	if err := json.Unmarshal(wStatus.Body.Bytes(), &initialStatus); err != nil {
		t.Fatalf("Failed to parse status response: %v", err)
	}

	initialVersion, ok := initialStatus["key_version"].(string)
	if !ok || initialVersion == "" {
		t.Fatalf("Invalid initial key version: %v", initialStatus["key_version"])
	}

	// Trigger rotation
	reqRotate := httptest.NewRequest("POST", "/gateway/rotate-crypto", nil)
	reqRotate.Header.Set("X-API-KEY", apiKey)
	wRotate := httptest.NewRecorder()
	r.ServeHTTP(wRotate, reqRotate)
	if wRotate.Code != http.StatusOK {
		t.Fatalf("Failed to rotate keys: %d", wRotate.Code)
	}

	// Get status again
	wStatus2 := httptest.NewRecorder()
	r.ServeHTTP(wStatus2, reqStatus)

	var newStatus map[string]interface{}
	if err := json.Unmarshal(wStatus2.Body.Bytes(), &newStatus); err != nil {
		t.Fatalf("Failed to parse new status response: %v", err)
	}

	newVersion := newStatus["key_version"].(string)
	if newVersion == initialVersion {
		t.Errorf("Expected key version to change after rotation, but got same: %s", newVersion)
	}

	graceCount := int(newStatus["grace_keys_count"].(float64))
	if graceCount < 1 {
		t.Errorf("Expected at least 1 grace key, got %d", graceCount)
	}
}

func TestPQCMiddleware_ZeroDowntimeGraceAndExpiry(t *testing.T) {
	// Reset registry to ensure clean slate
	globalRegistry = &CryptoRegistry{}
	_ = globalRegistry.Rotate()

	handler := PQCMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))

	// 1. Get initial active key version
	globalRegistry.mu.RLock()
	v1 := globalRegistry.ActiveKey.Version
	globalRegistry.mu.RUnlock()

	// 2. Request with active key should succeed
	req1 := httptest.NewRequest("GET", "/", nil)
	req1.Header.Set("X-Lottery-Version", "11.0")
	req1.Header.Set("X-PQC-Key-Version", v1)
	w1 := httptest.NewRecorder()
	handler.ServeHTTP(w1, req1)
	if w1.Code != http.StatusOK {
		t.Errorf("Expected OK for active key, got %d", w1.Code)
	}

	// 3. Rotate key
	if err := globalRegistry.Rotate(); err != nil {
		t.Fatalf("Failed to rotate: %v", err)
	}

	// v1 is now a grace key
	globalRegistry.mu.RLock()
	v2 := globalRegistry.ActiveKey.Version
	globalRegistry.mu.RUnlock()

	if v1 == v2 {
		t.Fatalf("Expected key version to change")
	}

	// 4. Request with v1 (now grace key) should still succeed
	req2 := httptest.NewRequest("GET", "/", nil)
	req2.Header.Set("X-Lottery-Version", "11.0")
	req2.Header.Set("X-PQC-Key-Version", v1)
	w2 := httptest.NewRecorder()
	handler.ServeHTTP(w2, req2)
	if w2.Code != http.StatusOK {
		t.Errorf("Expected OK for grace key during grace period, got %d", w2.Code)
	}

	// 5. Wait 5.1 seconds for grace period to expire
	time.Sleep(5100 * time.Millisecond)

	// 6. Request with v1 should now fail (expired)
	req3 := httptest.NewRequest("GET", "/", nil)
	req3.Header.Set("X-Lottery-Version", "11.0")
	req3.Header.Set("X-PQC-Key-Version", v1)
	w3 := httptest.NewRecorder()
	handler.ServeHTTP(w3, req3)
	if w3.Code != http.StatusBadRequest {
		t.Errorf("Expected status 400 Bad Request for expired grace key, got %d", w3.Code)
	}

	// 7. Request with v2 (current active key) should still succeed
	req4 := httptest.NewRequest("GET", "/", nil)
	req4.Header.Set("X-Lottery-Version", "11.0")
	req4.Header.Set("X-PQC-Key-Version", v2)
	w4 := httptest.NewRecorder()
	handler.ServeHTTP(w4, req4)
	if w4.Code != http.StatusOK {
		t.Errorf("Expected OK for active key, got %d", w4.Code)
	}
}

func TestPQCMiddleware_ConcurrentStress(t *testing.T) {
	handler := PQCMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))

	var wg sync.WaitGroup
	workers := 20
	iterations := 50

	for i := 0; i < workers; i++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for j := 0; j < iterations; j++ {
				// Perform rotation periodically
				if j%10 == 0 {
					_ = globalRegistry.Rotate()
				}

				globalRegistry.mu.RLock()
				activeV := globalRegistry.ActiveKey.Version
				globalRegistry.mu.RUnlock()

				req := httptest.NewRequest("GET", "/", nil)
				req.Header.Set("X-Lottery-Version", "11.0")
				// Mix of requesting active key, old version, and empty version
				if j%3 == 0 {
					req.Header.Set("X-PQC-Key-Version", activeV)
				} else if j%3 == 1 {
					req.Header.Set("X-PQC-Key-Version", fmt.Sprintf("invalid_version_%d", j))
				}

				w := httptest.NewRecorder()
				handler.ServeHTTP(w, req)

				// Status code should either be 200 OK or 400 Bad Request (for invalid version), but absolutely no race or panic!
				if w.Code != http.StatusOK && w.Code != http.StatusBadRequest {
					t.Errorf("Unexpected status code: %d", w.Code)
				}
			}
		}(i)
	}

	wg.Wait()
}
