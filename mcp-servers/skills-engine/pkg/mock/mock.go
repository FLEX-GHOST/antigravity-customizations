package mock

import (
	"encoding/json"
	"net/http"
	"strings"
	"sync"
	"time"
)

type MockState struct {
	mu         sync.RWMutex
	Messages   []map[string]any `json:"messages"`
	WebhookURL string           `json:"webhook_url"`
}

var State = &MockState{
	Messages: make([]map[string]any, 0),
}

func (s *MockState) Reset() {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.Messages = make([]map[string]any, 0)
	s.WebhookURL = ""
}

func (s *MockState) AddMessage(msg map[string]any) {
	s.mu.Lock()
	defer s.mu.Unlock()
	s.Messages = append(s.Messages, msg)
}

func (s *MockState) EditMessage(msgID int64, newText string, replyMarkup any) map[string]any {
	s.mu.Lock()
	defer s.mu.Unlock()
	for _, m := range s.Messages {
		if id, ok := m["message_id"].(int64); ok && id == msgID {
			m["text"] = newText
			if replyMarkup != nil {
				m["reply_markup"] = replyMarkup
			}
			return m
		}
	}
	return map[string]any{"message_id": msgID, "text": newText, "date": time.Now().Unix()}
}

func (s *MockState) GetMessages() []map[string]any {
	s.mu.RLock()
	defer s.mu.RUnlock()
	copied := make([]map[string]any, len(s.Messages))
	copy(copied, s.Messages)
	return copied
}

func HandleTelegramMock(w http.ResponseWriter, r *http.Request) bool {
	path := r.URL.Path

	// GET handlers
	if r.Method == http.MethodGet {
		if strings.Contains(path, "/getMe") {
			writeJSON(w, http.StatusOK, map[string]any{
				"ok": true,
				"result": map[string]any{
					"id":                          999999999,
					"is_bot":                      true,
					"first_name":                  "SkillsEngineMockBot",
					"username":                    "skills_engine_mock_bot",
					"can_join_groups":             true,
					"can_read_all_group_messages": false,
					"supports_inline_queries":     true,
				},
			})
			return true
		}
		if path == "/mock/messages" {
			msgs := State.GetMessages()
			writeJSON(w, http.StatusOK, map[string]any{
				"ok":       true,
				"count":    len(msgs),
				"messages": msgs,
			})
			return true
		}
		if path == "/mock/health" {
			msgs := State.GetMessages()
			writeJSON(w, http.StatusOK, map[string]any{
				"status":            "HEALTHY",
				"sandbox":           "telegram-mock",
				"messages_recorded": len(msgs),
				"webhook_url":       State.WebhookURL,
			})
			return true
		}
	}

	// POST handlers
	if r.Method == http.MethodPost {
		var body map[string]any
		_ = json.NewDecoder(r.Body).Decode(&body)

		if strings.HasSuffix(path, "/sendMessage") {
			msgs := State.GetMessages()
			msgID := int64(len(msgs) + 1001)
			record := map[string]any{
				"message_id":   msgID,
				"date":         time.Now().Unix(),
				"chat":         map[string]any{"id": body["chat_id"], "type": "private"},
				"text":         body["text"],
				"reply_markup": body["reply_markup"],
			}
			State.AddMessage(record)
			writeJSON(w, http.StatusOK, map[string]any{"ok": true, "result": record})
			return true
		}

		if strings.HasSuffix(path, "/editMessageText") {
			var msgID int64 = 1001
			if midVal, ok := body["message_id"]; ok {
				if f, ok := midVal.(float64); ok {
					msgID = int64(f)
				}
			}
			txt, _ := body["text"].(string)
			res := State.EditMessage(msgID, txt, body["reply_markup"])
			writeJSON(w, http.StatusOK, map[string]any{"ok": true, "result": res})
			return true
		}

		if strings.HasSuffix(path, "/deleteMessage") {
			writeJSON(w, http.StatusOK, map[string]any{"ok": true, "result": true})
			return true
		}

		if strings.HasSuffix(path, "/sendPhoto") {
			msgs := State.GetMessages()
			msgID := int64(len(msgs) + 1001)
			record := map[string]any{
				"message_id": msgID,
				"date":       time.Now().Unix(),
				"chat":       map[string]any{"id": body["chat_id"], "type": "private"},
				"caption":    body["caption"],
				"photo": []map[string]any{
					{"file_id": "mock_photo_id", "width": 800, "height": 600},
				},
			}
			State.AddMessage(record)
			writeJSON(w, http.StatusOK, map[string]any{"ok": true, "result": record})
			return true
		}

		if strings.HasSuffix(path, "/setWebhook") {
			if u, ok := body["url"].(string); ok {
				State.mu.Lock()
				State.WebhookURL = u
				State.mu.Unlock()
			}
			writeJSON(w, http.StatusOK, map[string]any{
				"ok":          true,
				"result":      true,
				"description": "Webhook was set successfully in Mock Engine",
			})
			return true
		}

		if path == "/mock/reset" {
			State.Reset()
			writeJSON(w, http.StatusOK, map[string]any{"ok": true, "cleared": true})
			return true
		}

		// Generic fallback for any Telegram Bot API method
		if strings.Contains(path, "/bot") {
			parts := strings.Split(path, "/")
			methodName := parts[len(parts)-1]
			writeJSON(w, http.StatusOK, map[string]any{
				"ok":               true,
				"result":           true,
				"mock_method":      methodName,
				"received_payload": body,
			})
			return true
		}
	}

	return false
}

func writeJSON(w http.ResponseWriter, status int, data any) {
	w.Header().Set("Content-Type", "application/json; charset=utf-8")
	w.WriteHeader(status)
	_ = json.NewEncoder(w).Encode(data)
}
