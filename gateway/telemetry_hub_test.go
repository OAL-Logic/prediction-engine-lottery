package main

import (
	"context"
	"encoding/json"
	"net"
	"net/http"
	"net/http/httptest"
	"testing"
	"time"

	"nhooyr.io/websocket"
)

func testUDPToWebSocket(t *testing.T) {
	hub := NewTelemetryHub()
	
	// Start UDP Listener on a random port
	port := 9123
	go hub.StartUDPListener(port)
	time.Sleep(100 * time.Millisecond)

	// Create test server
	s := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		hub.Subscribe(r.Context(), w, r)
	}))
	defer s.Close()

	// Connect WebSocket client
	ctx, cancel := context.WithTimeout(context.Background(), 5*time.Second)
	defer cancel()

	wsURL := "ws" + s.URL[4:]
	c, _, err := websocket.Dial(ctx, wsURL, nil)
	if err != nil {
		t.Fatalf("Failed to connect to WS: %v", err)
	}
	defer c.Close(websocket.StatusInternalError, "closing")

	// Emit UDP pulse
	msg := TelemetryMessage{
		Source:    "test",
		Level:     "INFO",
		Message:   "hello world",
		Timestamp: time.Now(),
	}
	data, _ := json.Marshal(msg)
	
	conn, err := net.Dial("udp", "127.0.0.1:9123")
	if err != nil {
		t.Fatalf("Failed to dial UDP: %v", err)
	}
	conn.Write(data)
	conn.Close()

	// Read from WebSocket
	_, received, err := c.Read(ctx)
	if err != nil {
		t.Fatalf("Failed to read from WS: %v", err)
	}

	var tm TelemetryMessage
	json.Unmarshal(received, &tm)
	if tm.Message != "hello world" {
		t.Errorf("Expected 'hello world', got '%s'", tm.Message)
	}
}

func TestTelemetryHub(t *testing.T) {
	t.Run("UDPtoWS", testUDPToWebSocket)
}
