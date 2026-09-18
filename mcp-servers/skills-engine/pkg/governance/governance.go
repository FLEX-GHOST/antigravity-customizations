package governance

import (
	"fmt"
	"regexp"
	"strings"
)

var SycophanticOpeners = []string{
	"great question", "you are absolutely right", "certainly", "i would be happy to help",
	"excellent point", "of course, i can help with that",
	"طبعا من عيوني", "تدلل", "امرك يا غالي", "تفضل عيني", "حاضر وتحت امرك", "بالتأكيد عزيزي", "على راسي",
}

func AuditAntiSycophancy(text string) map[string]any {
	lower := strings.ToLower(text)
	var violations []map[string]any

	for _, opener := range SycophanticOpeners {
		if strings.Contains(lower, opener) {
			violations = append(violations, map[string]any{
				"rule":     "honest_engineering",
				"severity": "CRITICAL",
				"pattern":  opener,
				"message":  fmt.Sprintf("Sycophantic / servile pattern detected: '%s'. Lead with technical verdict directly.", opener),
			})
		}
	}

	status := "PASSED"
	if len(violations) > 0 {
		status = "FAILED"
	}

	return map[string]any{
		"status":           status,
		"violations_count": len(violations),
		"violations":       violations,
		"remediation":      "Remove flattery. State technical facts, trade-offs, and diffs directly.",
	}
}

var BannedGradients = []string{"#7c3aed", "#8b5cf6", "#6366f1", "rgb(124, 58, 237)", "rgb(139, 92, 246)"}

func AuditUIDesign(content string) map[string]any {
	var violations []map[string]any

	for _, g := range BannedGradients {
		if strings.Contains(strings.ToLower(content), g) {
			violations = append(violations, map[string]any{
				"rule":     "anti_ai_design",
				"severity": "HIGH",
				"detail":   fmt.Sprintf("Banned AI-purple gradient/color detected: '%s'. Use semantic ramps and brand colors.", g),
			})
		}
	}

	if strings.Contains(content, "filter: blur(") && strings.Contains(content, "radial-gradient") {
		violations = append(violations, map[string]any{
			"rule":     "anti_ai_design",
			"severity": "MEDIUM",
			"detail":   "Glowing amorphous blur blob background pattern detected. Use structured depth or clean surfaces.",
		})
	}

	// Check raw emojis in buttons
	emojiRegex := regexp.MustCompile(`[\x{1F300}-\x{1F5FF}\x{1F600}-\x{1F64F}\x{1F680}-\x{1F6FF}\x{2600}-\x{26FF}\x{2700}-\x{27BF}]`)
	if strings.Contains(content, "<button") || strings.Contains(content, "InlineKeyboardButton") {
		if emojiRegex.MatchString(content) {
			violations = append(violations, map[string]any{
				"rule":     "anti_ai_design",
				"severity": "CRITICAL",
				"detail":   "Raw emoji detected in button or badge. Use scalable vector SVGs or Telegram custom emoji IDs.",
			})
		}
	}

	status := "PASSED"
	if len(violations) > 0 {
		status = "FAILED"
	}

	return map[string]any{
		"status":           status,
		"violations_count": len(violations),
		"violations":       violations,
	}
}

func GetCoreRules() map[string]any {
	return map[string]any{
		"rules": []map[string]string{
			{
				"id":          "anti_ai_design",
				"title":       "Anti-AI UI Slop & Color Discipline",
				"description": "Forbids purple gradients, amorphous glowing blur blobs, and raw emojis in buttons. Mandates 6 interactive states.",
			},
			{
				"id":          "honest_engineering",
				"title":       "Honest Engineering & Anti-Sycophancy",
				"description": "Forbids servile pleasantries and flattery. Mandates leading with the verdict and surfacing trade-offs.",
			},
			{
				"id":          "strict_comment_discipline",
				"title":       "Strict Comment Discipline & Zero AI Narration",
				"description": "Prohibits echo comments, tutorial commentary, and lazy TODO placeholders. Allows only 'Why, Not What'.",
			},
			{
				"id":          "rust_standards",
				"title":       "Rust Production Systems Engineering",
				"description": "Bans unwrap in handlers, enforces Zero-RAM idle, jemallocator, and Tokio cancellation safety.",
			},
		},
		"enforcement": "MANDATORY_SOVEREIGN",
	}
}
