package ipc

import (
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os"
	"strings"

	"skills-engine/pkg/mock"
	"skills-engine/pkg/telegram"
)

func StartServer(port int, unixPath string) {
	// 1. HTTP loopback
	mux := http.NewServeMux()
	mux.HandleFunc("/", func(w http.ResponseWriter, r *http.Request) {
		path := r.URL.Path

		if path == "/api/health" {
			w.Header().Set("Content-Type", "application/json")
			_ = json.NewEncoder(w).Encode(map[string]any{
				"status":  "HEALTHY",
				"service": "skills-engine",
				"version": "2.5-go",
			})
			return
		}

		if strings.HasPrefix(path, "/api/spec/") {
			query := strings.TrimPrefix(path, "/api/spec/")
			query = strings.Split(query, "?")[0]
			spec := telegram.GetSpec(query)
			w.Header().Set("Content-Type", "application/json; charset=utf-8")
			_ = json.NewEncoder(w).Encode(spec)
			return
		}

		// Check mock server
		if mock.HandleTelegramMock(w, r) {
			return
		}

		http.NotFound(w, r)
	})

	go func() {
		addr := fmt.Sprintf("127.0.0.1:%d", port)
		server := &http.Server{
			Addr:    addr,
			Handler: mux,
		}
		_ = server.ListenAndServe()
	}()

	// 2. UNIX domain socket
	go func() {
		_ = os.Remove(unixPath)
		listener, err := net.Listen("unix", unixPath)
		if err != nil {
			return
		}
		defer listener.Close()

		for {
			conn, err := listener.Accept()
			if err != nil {
				continue
			}
			go handleUnixConn(conn)
		}
	}()
}

func handleUnixConn(conn net.Conn) {
	defer conn.Close()
	buf := make([]byte, 2048)
	n, err := conn.Read(buf)
	if err != nil {
		return
	}
	raw := strings.TrimSpace(string(buf[:n]))

	var resp []byte
	if raw == "health" {
		resp, _ = json.Marshal(map[string]any{
			"status":  "HEALTHY",
			"service": "skills-engine",
			"ipc":     "unix",
			"lang":    "go",
		})
	} else if strings.HasPrefix(raw, "spec:") {
		q := strings.TrimSpace(strings.TrimPrefix(raw, "spec:"))
		spec := telegram.GetSpec(q)
		resp, _ = json.Marshal(spec)
	} else {
		resp, _ = json.Marshal(map[string]any{"error": "unknown command"})
	}

	_, _ = conn.Write(resp)
}
