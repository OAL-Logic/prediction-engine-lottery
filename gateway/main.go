package main

import (
	"fmt"
	"log"
	"net/http"
	"net/http/httputil"
	"net/url"
	"os"
	"sync/atomic"
	"time"

	"github.com/go-chi/chi/v5"
	"github.com/go-chi/chi/v5/middleware"
	"github.com/go-chi/httprate"
	"github.com/go-chi/render"
)

var telemetryHub *TelemetryHub

func main() {
	port := os.Getenv("PORT")
	if port == "" {
		port = "8080"
	}

	sidecarURL := os.Getenv("SIDECAR_URL")
	if sidecarURL == "" {
		sidecarURL = "http://127.0.0.1:8000"
	}

	apiKey := os.Getenv("API_KEY")
	if apiKey == "" {
		apiKey = "lottery-secret-key"
	}

	target, err := url.Parse(sidecarURL)
	if err != nil {
		log.Fatal(err)
	}

	r := chi.NewRouter()

	// Initialize Telemetry Hub (Story 5.5)
	telemetryHub = NewTelemetryHub()
	go telemetryHub.StartUDPListener(9000)

	// Middlewares
	r.Use(middleware.RequestID)
	r.Use(middleware.RealIP)
	r.Use(middleware.Logger)
	r.Use(middleware.Recoverer)
	r.Use(middleware.Timeout(60 * time.Second))

	// Rate Limiting: 100 requests per minute per IP
	r.Use(httprate.LimitByIP(100, 1*time.Minute))

	// STORY 1.1: Post-Quantum Middleware
	r.Use(PQCMiddleware)

	// Simple In-memory Cache for GET requests (10s TTL)
	r.Use(CacheMiddleware(10 * time.Second))

	r.Get("/health", func(w http.ResponseWriter, r *http.Request) {
		render.JSON(w, r, map[string]string{"status": "ok", "gateway": "active"})
	})

	// STORY 5.5: Telemetry Subscription
	r.Get("/telemetry", func(w http.ResponseWriter, r *http.Request) {
		err := telemetryHub.Subscribe(r.Context(), w, r)
		if err != nil {
			log.Printf("Telemetry subscribe error: %v", err)
		}
	})

	// Auth & Proxy
	r.Group(func(r chi.Router) {
		r.Use(AuthMiddleware(apiKey))

		r.Post("/gateway/rotate-crypto", func(w http.ResponseWriter, r *http.Request) {
			if err := globalRegistry.Rotate(); err != nil {
				http.Error(w, fmt.Sprintf("Failed to rotate crypto: %v", err), http.StatusInternalServerError)
				return
			}
			globalRegistry.mu.RLock()
			activeKey := globalRegistry.ActiveKey
			globalRegistry.mu.RUnlock()

			w.Header().Set("Content-Type", "application/json")
			render.JSON(w, r, map[string]interface{}{
				"status":       "rotated",
				"key_version":  activeKey.Version,
				"last_rotated": globalRegistry.LastRotated.Format(time.RFC3339),
			})
		})

		r.Get("/gateway/crypto/status", func(w http.ResponseWriter, r *http.Request) {
			globalRegistry.mu.RLock()
			activeKey := globalRegistry.ActiveKey
			graceCount := len(globalRegistry.GraceKeys)
			lastRotated := globalRegistry.LastRotated.Format(time.RFC3339)
			globalRegistry.mu.RUnlock()

			tunnelCount := atomic.LoadInt64(&globalRegistry.TunnelCount)

			versionStr := ""
			if activeKey != nil {
				versionStr = activeKey.Version
			}

			w.Header().Set("Content-Type", "application/json")
			render.JSON(w, r, map[string]interface{}{
				"active_algorithm":    "ML-KEM-768",
				"key_version":         versionStr,
				"last_rotated":        lastRotated,
				"active_tunnel_count": tunnelCount,
				"grace_keys_count":    graceCount,
			})
		})

		r.HandleFunc("/*", func(w http.ResponseWriter, r *http.Request) {
			proxy := httputil.NewSingleHostReverseProxy(target)
			
			// Update the headers to allow for SSL redirection and correct host
			r.URL.Host = target.Host
			r.URL.Scheme = target.Scheme
			r.Header.Set("X-Forwarded-Host", r.Header.Get("Host"))
			r.Host = target.Host

			// STORY 3.1: Propagate deadline if exists
			if deadline, ok := r.Context().Deadline(); ok {
				r.Header.Set("X-Request-Deadline", fmt.Sprintf("%d", deadline.Unix()))
			}

			proxy.ServeHTTP(w, r)
		})
	})

	log.Printf("Gateway starting on :%s proxying to %s", port, sidecarURL)
	log.Fatal(http.ListenAndServe(":"+port, r))
}

func AuthMiddleware(apiKey string) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			key := r.Header.Get("X-API-KEY")
			if key != apiKey {
				http.Error(w, "Unauthorized", http.StatusUnauthorized)
				return
			}
			next.ServeHTTP(w, r)
		})
	}
}

type cacheEntry struct {
	body      []byte
	expiresAt time.Time
	header    http.Header
}

var (
	cache = make(map[string]cacheEntry)
)

func CacheMiddleware(ttl time.Duration) func(http.Handler) http.Handler {
	return func(next http.Handler) http.Handler {
		return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
			if r.Method != http.MethodGet || r.URL.Path == "/health" {
				next.ServeHTTP(w, r)
				return
			}

			version := r.Header.Get("X-Lottery-Version")
			key := r.URL.String() + ":" + version
			entry, found := cache[key]
			if found && time.Now().Before(entry.expiresAt) {
				for k, v := range entry.header {
					w.Header()[k] = v
				}
				w.Header().Set("X-Cache", "HIT")
				w.Write(entry.body)
				return
			}

			// Capture the response
			rec := &responseRecorder{ResponseWriter: w, body: []byte{}, header: make(http.Header)}
			next.ServeHTTP(rec, r)

			if rec.status == http.StatusOK {
				cache[key] = cacheEntry{
					body:      rec.body,
					expiresAt: time.Now().Add(ttl),
					header:    rec.Header(),
				}
			}
		})
	}
}

type responseRecorder struct {
	http.ResponseWriter
	status int
	body   []byte
	header http.Header
}

func (r *responseRecorder) WriteHeader(status int) {
	r.status = status
	r.ResponseWriter.WriteHeader(status)
}

func (r *responseRecorder) Write(b []byte) (int, error) {
	r.body = append(r.body, b...)
	return r.ResponseWriter.Write(b)
}
