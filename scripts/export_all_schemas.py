import sys
import json
from pathlib import Path

sys.path.insert(0, "/root/antigravity-customizations/mcp-servers/skills-engine")
import server

def main():
    tools = server.mcp._tool_manager._tools
    schema_dirs = [
        Path("/root/antigravity-customizations/mcp-schemas/skills-engine"),
        Path("/root/.gemini/antigravity-ide/mcp/skills-engine"),
        Path("/root/.gemini/antigravity-cli/mcp/skills-engine")
    ]

    for d in schema_dirs:
        d.mkdir(parents=True, exist_ok=True)
        for old_file in d.glob("*.json"):
            old_file.unlink()

    print(f"Exporting schemas for all {len(tools)} tools...")
    for tool_name, tool in tools.items():
        schema = {
            "name": tool.name,
            "description": tool.description,
            "inputSchema": tool.parameters
        }
        for d in schema_dirs:
            p = d / f"{tool_name}.json"
            p.write_text(json.dumps(schema, indent=2, ensure_ascii=False), encoding="utf-8")

    print(f"[✓] Schema export complete: {len(tools)} tools exported across all target directories.")

if __name__ == "__main__":
    main()
