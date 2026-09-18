package main

import (
	"bufio"
	"embed"
	"encoding/json"
	"flag"
	"fmt"
	"io"
	"os"

	"skills-engine/pkg/ipc"
	"skills-engine/pkg/server"
	"skills-engine/pkg/types"
)

//go:embed data/schemas/*.json
var schemaFS embed.FS

//go:embed data/telegram/*.json
var telegramFS embed.FS

func main() {
	transport := flag.String("transport", "stdio", "Transport protocol (stdio, http)")
	port := flag.Int("port", 14993, "Port for HTTP loopback and mock server")
	unixPath := flag.String("socket", "/tmp/skills-engine.sock", "Path for UNIX domain socket")
	flag.Parse()

	// 1. Initialize core MCP server
	srv, err := server.NewServer(schemaFS, telegramFS)
	if err != nil {
		fmt.Fprintf(os.Stderr, "[!] Failed to initialize skills-engine server: %v\n", err)
		os.Exit(1)
	}

	// 2. Start high-performance IPC & Telegram Mock Server in background
	ipc.StartServer(*port, *unixPath)

	if *transport != "stdio" {
		fmt.Fprintf(os.Stderr, "[*] skills-engine running HTTP on port %d...\n", *port)
		select {} // Block forever
	}

	// 3. Main stdio JSON-RPC 2.0 protocol loop
	reader := bufio.NewReader(os.Stdin)
	for {
		line, err := reader.ReadBytes('\n')
		if err != nil {
			if err == io.EOF {
				break
			}
			continue
		}

		if len(line) == 0 || string(line) == "\n" {
			continue
		}

		var req types.JSONRPCRequest
		if err := json.Unmarshal(line, &req); err != nil {
			continue
		}

		handleRequest(srv, req)
	}
}

func handleRequest(srv *server.Server, req types.JSONRPCRequest) {
	switch req.Method {
	case "initialize":
		resp := types.JSONRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Result: types.InitializeResult{
				ProtocolVersion: "2024-11-05",
				Capabilities: types.ServerCapabilities{
					Tools: &types.ToolsCapability{ListChanged: false},
				},
				ServerInfo: types.ServerInfo{
					Name:    "skills-engine",
					Version: "2.5-go",
				},
			},
		}
		writeResponse(resp)

	case "notifications/initialized":
		// No-op acknowledgment as per MCP spec

	case "ping":
		writeResponse(types.JSONRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Result:  map[string]any{},
		})

	case "tools/list":
		tools := srv.ListTools()
		writeResponse(types.JSONRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Result: types.ToolsListResult{
				Tools: tools,
			},
		})

	case "tools/call":
		var params types.CallToolParams
		if err := json.Unmarshal(req.Params, &params); err != nil {
			writeResponse(types.JSONRPCResponse{
				JSONRPC: "2.0",
				ID:      req.ID,
				Error: &types.JSONRPCError{
					Code:    -32602,
					Message: "Invalid params: " + err.Error(),
				},
			})
			return
		}

		callRes, err := srv.CallTool(params.Name, params.Arguments)
		if err != nil {
			writeResponse(types.JSONRPCResponse{
				JSONRPC: "2.0",
				ID:      req.ID,
				Error: &types.JSONRPCError{
					Code:    -32603,
					Message: "Internal error: " + err.Error(),
				},
			})
			return
		}

		writeResponse(types.JSONRPCResponse{
			JSONRPC: "2.0",
			ID:      req.ID,
			Result:  callRes,
		})

	default:
		if req.ID != nil {
			writeResponse(types.JSONRPCResponse{
				JSONRPC: "2.0",
				ID:      req.ID,
				Error: &types.JSONRPCError{
					Code:    -32601,
					Message: fmt.Sprintf("Method '%s' not found", req.Method),
				},
			})
		}
	}
}

func writeResponse(resp types.JSONRPCResponse) {
	data, err := json.Marshal(resp)
	if err != nil {
		return
	}
	data = append(data, '\n')
	_, _ = os.Stdout.Write(data)
}
