package main

import (
	"context"
	"encoding/json"
	"fmt"
	"log"
	"net"
	"net/http"
	"sync"
	"time"

	"nhooyr.io/websocket"
)

type TelemetryMessage struct {
	Source    string    `json:"source"`
	Level     string    `json:"level"`
	Message   string    `json:"message"`
	Timestamp time.Time `json:"timestamp"`
}

type TelemetryHub struct {
	subscribers map[*subscriber]struct{}
	mu          sync.Mutex
}

type subscriber struct {
	msgs chan []byte
}

func NewTelemetryHub() *TelemetryHub {
	return &TelemetryHub{
		subscribers: make(map[*subscriber]struct{}),
	}
}

func (h *TelemetryHub) Subscribe(ctx context.Context, w http.ResponseWriter, r *http.Request) error {
	c, err := websocket.Accept(w, r, &websocket.AcceptOptions{
		InsecureSkipVerify: true, // For dev convenience
	})
	if err != nil {
		return err
	}
	defer c.Close(websocket.StatusInternalError, "closing")

	s := &subscriber{
		msgs: make(chan []byte, 100),
	}
	h.addSubscriber(s)
	defer h.deleteSubscriber(s)

	for {
		select {
		case msg := <-s.msgs:
			err = c.Write(ctx, websocket.MessageText, msg)
			if err != nil {
				return err
			}
		case <-ctx.Done():
			return ctx.Err()
		}
	}
}

func (h *TelemetryHub) Broadcast(msg []byte) {
	h.mu.Lock()
	defer h.mu.Unlock()
	for s := range h.subscribers {
		select {
		case s.msgs <- msg:
		default:
			// Buffer full, drop message for this subscriber
		}
	}
}

func (h *TelemetryHub) addSubscriber(s *subscriber) {
	h.mu.Lock()
	h.subscribers[s] = struct{}{}
	h.mu.Unlock()
}

func (h *TelemetryHub) deleteSubscriber(s *subscriber) {
	h.mu.Lock()
	delete(h.subscribers, s)
	h.mu.Unlock()
}

// StartUDPListener listens for telemetry pulses from the Python engine
func (h *TelemetryHub) StartUDPListener(port int) {
	addr := net.UDPAddr{
		Port: port,
		IP:   net.ParseIP("127.0.0.1"),
	}
	conn, err := net.ListenUDP("udp", &addr)
	if err != nil {
		log.Fatalf("UDP Listener failed: %v", err)
	}
	defer conn.Close()

	fmt.Printf("Telemetry UDP Listener active on port %d\n", port)
	buf := make([]byte, 4096)
	for {
		n, _, err := conn.ReadFromUDP(buf)
		if err != nil {
			log.Printf("UDP Read error: %v", err)
			continue
		}

		// Validate JSON before broadcast
		var tm TelemetryMessage
		if err := json.Unmarshal(buf[:n], &tm); err != nil {
			log.Printf("Invalid Telemetry JSON: %v", err)
			continue
		}
		
		h.Broadcast(buf[:n])
	}
}
