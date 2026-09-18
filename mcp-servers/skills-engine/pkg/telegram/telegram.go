package telegram

import (
	"encoding/json"
	"fmt"
	"strings"
	"time"
)

type MethodSpec struct {
	Name        string           `json:"name"`
	Description string           `json:"description"`
	Returns     []string         `json:"returns"`
	Fields      []ParameterField `json:"fields"`
}

type ParameterField struct {
	Name        string   `json:"name"`
	Types       []string `json:"types"`
	Required    bool     `json:"required"`
	Description string   `json:"description"`
}

type TypeSpec struct {
	Name        string           `json:"name"`
	Description string           `json:"description"`
	Fields      []ParameterField `json:"fields"`
}

type VersionInfo struct {
	Version      string `json:"version"`
	TotalMethods int    `json:"total_methods"`
	TotalTypes   int    `json:"total_types"`
	ReleaseDate  string `json:"release_date"`
}

var (
	MethodsMap    = make(map[string]MethodSpec)
	TypesMap      = make(map[string]TypeSpec)
	ActiveVersion = VersionInfo{
		Version:      "10.3",
		TotalMethods: 185,
		TotalTypes:   400,
	}
)

func LoadSpecs(methodsJSON, typesJSON, versionJSON []byte) error {
	var methods []MethodSpec
	if err := json.Unmarshal(methodsJSON, &methods); err == nil {
		for _, m := range methods {
			MethodsMap[strings.ToLower(m.Name)] = m
		}
	}

	var types []TypeSpec
	if err := json.Unmarshal(typesJSON, &types); err == nil {
		for _, t := range types {
			TypesMap[strings.ToLower(t.Name)] = t
		}
	}
	if len(versionJSON) > 0 {
		_ = json.Unmarshal(versionJSON, &ActiveVersion)
	}
	if ActiveVersion.TotalMethods == 0 {
		ActiveVersion.TotalMethods = len(MethodsMap)
	}
	if ActiveVersion.TotalTypes == 0 {
		ActiveVersion.TotalTypes = len(TypesMap)
	}
	return nil
}

func GetSpec(query string) map[string]any {
	q := strings.TrimSpace(strings.ToLower(query))
	t0 := time.Now()

	if m, ok := MethodsMap[q]; ok {
		var reqFields, optFields []map[string]any
		for _, f := range m.Fields {
			fMap := map[string]any{
				"name":        f.Name,
				"types":       f.Types,
				"required":    f.Required,
				"description": f.Description,
			}
			if f.Required {
				reqFields = append(reqFields, fMap)
			} else {
				optFields = append(optFields, fMap)
			}
		}

		return map[string]any{
			"query":                  query,
			"resolved_name":          m.Name,
			"kind":                   "method",
			"bot_api_version":        "10.3",
			"description":            m.Description,
			"returns":                m.Returns,
			"required_parameters":    reqFields,
			"optional_parameters":    optFields,
			"rust_execution_pattern": GenerateRustCall(m.Name, reqFields),
			"duration_ms":            float64(time.Since(t0).Microseconds()) / 1000.0,
		}
	}

	if t, ok := TypesMap[q]; ok {
		var fields []map[string]any
		for _, f := range t.Fields {
			fields = append(fields, map[string]any{
				"name":        f.Name,
				"types":       f.Types,
				"required":    f.Required,
				"description": f.Description,
			})
		}
		return map[string]any{
			"query":                  query,
			"resolved_name":          t.Name,
			"kind":                   "type",
			"bot_api_version":        "10.3",
			"description":            t.Description,
			"fields":                 fields,
			"rust_execution_pattern": GenerateRustStruct(t.Name, fields),
			"duration_ms":            float64(time.Since(t0).Microseconds()) / 1000.0,
		}
	}

	return map[string]any{
		"query":           query,
		"status":          "NOT_FOUND",
		"message":         fmt.Sprintf("Telegram entity '%s' not found in Bot API 10.3 spec.", query),
		"bot_api_version": "10.3",
		"duration_ms":     float64(time.Since(t0).Microseconds()) / 1000.0,
	}
}

func GenerateRustCall(methodName string, reqFields []map[string]any) string {
	pascal := strings.ToUpper(methodName[:1]) + methodName[1:]
	return fmt.Sprintf("// Bot API 10.3 execution pattern\nlet req = %sRequest::new(chat_id);\nlet res = bot.execute(req).await?;", pascal)
}

func GenerateRustStruct(typeName string, fields []map[string]any) string {
	var lines []string
	lines = append(lines, "// Conforming to Telegram Bot API 10.3 / 9.4+ button styling standards")
	lines = append(lines, "#[derive(Debug, Clone, Serialize, Deserialize)]")
	lines = append(lines, fmt.Sprintf("pub struct %s {", typeName))
	for _, f := range fields {
		name := f["name"].(string)
		lines = append(lines, fmt.Sprintf("    pub %s: Option<String>,", name))
	}
	lines = append(lines, "}")
	return strings.Join(lines, "\n")
}

var Diagnostics = map[string]map[string]any{
	"BUTTON_TYPE_INVALID": {
		"code":            400,
		"cause":           "Inline button configuration violates Telegram Bot API 9.4+ schema. Often caused by mixing url with callback_data or invalid style property.",
		"fix_explanation": "Ensure button has either 'url' OR 'callback_data' (never both). Use valid style: 'primary' | 'success' | 'danger'.",
		"rust_fix":        "InlineKeyboardButton {\n    text: \"Submit\".into(),\n    callback_data: Some(\"submit\".into()),\n    style: Some(\"primary\".into()),\n    ..Default::default()\n}",
	},
	"BUTTON_USER_PRIVACY_RESTRICTED": {
		"code":            400,
		"cause":           "Target user privacy settings prevent adding them via button or link.",
		"fix_explanation": "Provide fallback text with t.me deep link instead of direct user selection button.",
		"rust_fix":        "// Handle privacy restriction gracefully\nlet url = format!(\"https://t.me/share/url?url={}&text={}\", link, text);",
	},
	"message is not modified": {
		"code":            400,
		"cause":           "Attempted to call editMessageText or editMessageReplyMarkup with identical content.",
		"fix_explanation": "Check current message content in local state before issuing edit call, or ignore error 400 matching 'message is not modified'.",
		"rust_fix":        "if let Err(e) = client.edit_message_text(...).await {\n    if !e.to_string().contains(\"message is not modified\") {\n        return Err(e.into());\n    }\n}",
	},
	"bot was blocked by the user": {
		"code":            403,
		"cause":           "The private user blocked the bot or deleted their Telegram account.",
		"fix_explanation": "Deactivate user record in PostgreSQL/SQLite and cease outgoing messages to prevent FloodWait penalties.",
		"rust_fix":        "sqlx::query!(\"UPDATE users SET is_active = false WHERE telegram_id = $1\", user_id).execute(&pool).await?;",
	},
	"Too Many Requests: retry after": {
		"code":            429,
		"cause":           "Exceeded Telegram Bot API rate limits (FloodWait).",
		"fix_explanation": "Extract retry_after seconds, apply tokio sleep with random jitter (100ms..1000ms), and retry.",
		"rust_fix":        "let wait = retry_after_secs + rand::thread_rng().gen_range(1..=3);\ntokio::time::sleep(tokio::time::Duration::from_secs(wait)).await;",
	},
}

func DiagnoseError(errorMessage string, errorCode int) map[string]any {
	msg := strings.ToLower(errorMessage)
	for k, v := range Diagnostics {
		if strings.Contains(msg, strings.ToLower(k)) {
			return map[string]any{
				"status":               "DIAGNOSED",
				"error_pattern":        k,
				"http_status":          v["code"],
				"root_cause":           v["cause"],
				"remediation_guidance": v["fix_explanation"],
				"rust_healing_snippet": v["rust_fix"],
			}
		}
	}

	status := errorCode
	if status == 0 {
		if strings.Contains(msg, "bad request") {
			status = 400
		} else if strings.Contains(msg, "forbidden") {
			status = 403
		} else {
			status = 500
		}
	}

	return map[string]any{
		"status":               "GENERAL_DIAGNOSIS",
		"raw_error":            errorMessage,
		"inferred_status":      status,
		"root_cause":           "Uncataloged Telegram API error. Inspect parameters and chat_id formatting.",
		"remediation_guidance": "Verify that private chat IDs are positive numbers and channels use the -100 prefix.",
		"rust_healing_snippet": "// Check chat_id format\nlet chat_id_str = if is_channel { format!(\"-100{}\", bare_id) } else { bare_id.to_string() };",
	}
}

var WorkflowMap = map[string]map[string]any{
	"sendMessage": {
		"related_types":       []string{"InlineKeyboardMarkup", "InlineKeyboardButton", "Message", "MessageEntity"},
		"next_steps":          []string{"editMessageText", "deleteMessage", "pinChatMessage"},
		"callbacks_handled":   []string{"answerCallbackQuery"},
		"recommendation":      "When implementing sendMessage, design handlers for: editMessageText, deleteMessage, pinChatMessage",
	},
	"sendPhoto": {
		"related_types":       []string{"InlineKeyboardMarkup", "InputFile", "Message"},
		"next_steps":          []string{"editMessageCaption", "deleteMessage"},
		"callbacks_handled":   []string{"answerCallbackQuery"},
		"recommendation":      "When implementing sendPhoto, design handlers for: editMessageCaption, deleteMessage",
	},
	"sendPaidMedia": {
		"related_types":       []string{"PaidMedia", "PaidMediaPurchased", "StarTransaction"},
		"next_steps":          []string{"getStarTransactions", "refundStarPayment"},
		"callbacks_handled":   []string{},
		"recommendation":      "When implementing sendPaidMedia, design handlers for: getStarTransactions, refundStarPayment",
	},
	"sendGift": {
		"related_types":       []string{"Gift", "Gifts", "StarTransaction"},
		"next_steps":          []string{"getAvailableGifts", "verifyUser", "verifyChat"},
		"callbacks_handled":   []string{},
		"recommendation":      "When implementing sendGift, design handlers for: getAvailableGifts, verifyUser, verifyChat",
	},
	"setWebhook": {
		"related_types":       []string{"WebhookInfo", "Update"},
		"next_steps":          []string{"getWebhookInfo", "deleteWebhook"},
		"callbacks_handled":   []string{},
		"recommendation":      "When implementing setWebhook, design handlers for: getWebhookInfo, deleteWebhook",
	},
	"InlineKeyboardButton": {
		"related_types":       []string{"InlineKeyboardMarkup", "CallbackQuery"},
		"next_steps":          []string{"answerCallbackQuery", "editMessageReplyMarkup", "editMessageText"},
		"callbacks_handled":   []string{"answerCallbackQuery"},
		"recommendation":      "When implementing InlineKeyboardButton, design handlers for: answerCallbackQuery, editMessageReplyMarkup, editMessageText",
	},
}

func ExploreWorkflow(entrypoint string) map[string]any {
	q := strings.TrimSpace(entrypoint)
	for k, v := range WorkflowMap {
		if strings.EqualFold(k, q) {
			return map[string]any{
				"status":                      "FOUND",
				"entrypoint":                  k,
				"related_types":               v["related_types"],
				"downstream_methods":          v["next_steps"],
				"expected_callbacks":          v["callbacks_handled"],
				"architecture_recommendation": v["recommendation"],
			}
		}
	}

	var nodes []string
	for k := range WorkflowMap {
		nodes = append(nodes, k)
	}

	return map[string]any{
		"status":                "NOT_IN_GRAPH",
		"entrypoint":            entrypoint,
		"available_graph_nodes": nodes,
		"recommendation":        "Use get_telegram_bot_api_spec for direct method specification.",
	}
}

func ValidatePayload(method string, payloadJSON string) map[string]any {
	var data map[string]any
	if err := json.Unmarshal([]byte(payloadJSON), &data); err != nil {
		return map[string]any{
			"status": "INVALID_JSON",
			"error":  err.Error(),
		}
	}

	var violations []string
	m := strings.TrimSpace(method)

	if txt, ok := data["text"].(string); ok {
		if len(txt) > 4096 {
			violations = append(violations, fmt.Sprintf("Text length (%d) exceeds Telegram 4096 character limit.", len(txt)))
		}
	}

	if capTxt, ok := data["caption"].(string); ok {
		if len(capTxt) > 1024 {
			violations = append(violations, fmt.Sprintf("Caption length (%d) exceeds Telegram 1024 character limit.", len(capTxt)))
		}
	}

	if cidVal, ok := data["chat_id"]; ok {
		cid := strings.TrimSpace(fmt.Sprintf("%v", cidVal))
		if strings.HasPrefix(cid, "-") && !strings.HasPrefix(cid, "-100") && len(cid) > 10 {
			violations = append(violations, fmt.Sprintf("Suspicious chat_id format '%s'. Supergroups and channels must have '-100' prefix.", cid))
		}
	}

	if markup, ok := data["reply_markup"].(map[string]any); ok {
		if ikb, ok := markup["inline_keyboard"].([]any); ok {
			if len(ikb) > 100 {
				violations = append(violations, fmt.Sprintf("Inline keyboard row count (%d) exceeds Telegram 100 row limit.", len(ikb)))
			}
			for rIdx, rowVal := range ikb {
				if row, ok := rowVal.([]any); ok {
					if len(row) > 8 {
						violations = append(violations, fmt.Sprintf("Row %d contains %d buttons, exceeding Telegram maximum of 8 buttons per row.", rIdx, len(row)))
					}
					for bIdx, btnVal := range row {
						if btn, ok := btnVal.(map[string]any); ok {
							if cb, ok := btn["callback_data"].(string); ok {
								if len([]byte(cb)) > 64 {
									violations = append(violations, fmt.Sprintf("Button [%d][%d] callback_data exceeds 64 bytes (%d bytes).", rIdx, bIdx, len([]byte(cb))))
								}
							}
							if style, ok := btn["style"].(string); ok {
								if style != "primary" && style != "success" && style != "danger" {
									violations = append(violations, fmt.Sprintf("Button [%d][%d] invalid style '%s'. Must be 'primary', 'success', or 'danger'.", rIdx, bIdx, style))
								}
							}
						}
					}
				}
			}
		}
	}

	if m == "sendPaidMedia" {
		if starCount, ok := data["star_count"]; !ok || fmt.Sprintf("%v", starCount) == "0" {
			violations = append(violations, "sendPaidMedia requires 'star_count' > 0.")
		}
	}

	status := "PASS"
	if len(violations) > 0 {
		status = "VIOLATIONS_FOUND"
	}

	return map[string]any{
		"status":                    status,
		"method":                    m,
		"violation_count":           len(violations),
		"violations":                violations,
		"is_bot_api_10_3_compliant": len(violations) == 0,
	}
}
