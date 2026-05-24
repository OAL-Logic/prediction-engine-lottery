package main

import (
	"net/http"
	"net/http/httptest"
	"testing"
)

func BenchmarkPQCMiddleware(b *testing.B) {
	handler := PQCMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))

	req := httptest.NewRequest("GET", "/", nil)
	req.Header.Set("X-Lottery-Version", "11.0")

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		w := httptest.NewRecorder()
		handler.ServeHTTP(w, req)
	}
}

func TestPQCMiddleware_HeaderPropagation(t *testing.T) {
	handler := PQCMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		if r.Header.Get("X-PQC-Active") != "true" {
			t.Errorf("Expected X-PQC-Active header to be set")
		}
		w.WriteHeader(http.StatusOK)
	}))

	req := httptest.NewRequest("GET", "/", nil)
	req.Header.Set("X-Lottery-Version", "11.0")
	w := httptest.NewRecorder()

	handler.ServeHTTP(w, req)

	if w.Code != http.StatusOK {
		t.Errorf("Expected status OK, got %v", w.Code)
	}
}

func TestPQCMiddleware_Rotation(t *testing.T) {
	handler := PQCMiddleware(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		w.WriteHeader(http.StatusOK)
	}))

	// 1. Get initial key version
	req1 := httptest.NewRequest("GET", "/", nil)
	req1.Header.Set("X-Lottery-Version", "11.0")
	w1 := httptest.NewRecorder()
	handler.ServeHTTP(w1, req1)
	
	v1 := w1.Header().Get("X-PQC-Key-Version")
	if v1 == "" {
		t.Fatal("Expected key version in response")
	}

	// 2. Rotate
	if err := globalRegistry.Rotate(); err != nil {
		t.Fatalf("Rotation failed: %v", err)
	}

	// 3. Verify old key still works (within grace period)
	req2 := httptest.NewRequest("GET", "/", nil)
	req2.Header.Set("X-Lottery-Version", "11.0")
	req2.Header.Set("X-PQC-Key-Version", v1)
	w2 := httptest.NewRecorder()
	handler.ServeHTTP(w2, req2)

	if w2.Code != http.StatusOK {
		t.Errorf("Expected old key to work in grace period, got %v", w2.Code)
	}

	// 4. Verify new key works
	req3 := httptest.NewRequest("GET", "/", nil)
	req3.Header.Set("X-Lottery-Version", "11.0")
	w3 := httptest.NewRecorder()
	handler.ServeHTTP(w3, req3)

	v2 := w3.Header().Get("X-PQC-Key-Version")
	if v2 == v1 {
		t.Errorf("Expected new key version, got same as old: %v", v2)
	}
}
