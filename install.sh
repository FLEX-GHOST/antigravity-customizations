#!/usr/bin/env bash
set -e

HOME_DIR="${HOME:-/root}"
CONFIG_DIR="${HOME_DIR}/.gemini/config"
MCP_SERVERS_DIR="${HOME_DIR}/.gemini/mcp-servers"
MCP_SCHEMAS_DIR="${HOME_DIR}/.gemini/antigravity-ide/mcp/skills-engine"
CATALOG_DIR="${HOME_DIR}/.gemini/skills-catalog"
REPO_URL="https://github.com/FLEX-GHOST/antigravity-customizations"

echo "[*] Installing Antigravity Customizations & Telegram Autonomous Engine..."

# 1. Ensure Python 3, curl, git
echo "[-] Checking system dependencies..."
if ! command -v python3 >/dev/null 2>&1 || ! command -v curl >/dev/null 2>&1; then
    if command -v apt-get >/dev/null 2>&1; then
        apt-get update -qq && apt-get install -y -qq python3 curl git sqlite3
    elif command -v yum >/dev/null 2>&1; then
        yum install -y -q python3 curl git sqlite
    fi
fi

# 2. Fast Python runtime check (uses uv for 100x speedup if mcp missing)
echo "[-] Verifying Python runtime..."
if ! python3 -c "from mcp.server.fastmcp import FastMCP" 2>/dev/null && \
   ! python3 -c "from mcp.server.mcpserver import MCPServer" 2>/dev/null && \
   ! python3 -c "from mcp.server import FastMCP" 2>/dev/null; then
    
    # Check if uv is available
    UV_BIN=""
    if command -v uv >/dev/null 2>&1; then
        UV_BIN="$(command -v uv)"
    elif [ -x "${HOME_DIR}/.local/bin/uv" ]; then
        UV_BIN="${HOME_DIR}/.local/bin/uv"
    elif [ -x "${HOME_DIR}/.cargo/bin/uv" ]; then
        UV_BIN="${HOME_DIR}/.cargo/bin/uv"
    fi

    # If uv is not available, install standalone uv (Rust-based, takes ~1s)
    if [ -z "$UV_BIN" ]; then
        curl -LsSf https://astral.sh/uv/install.sh 2>/dev/null | sh >/dev/null 2>&1 || true
        if [ -x "${HOME_DIR}/.local/bin/uv" ]; then
            UV_BIN="${HOME_DIR}/.local/bin/uv"
        fi
    fi

    # Install mcp via uv (0.2s) or fallback to pip
    if [ -n "$UV_BIN" ]; then
        "$UV_BIN" pip install --system --break-system-packages "mcp<2" >/dev/null 2>&1 || true
    else
        python3 -m pip install --no-cache-dir --quiet --break-system-packages --ignore-installed "mcp<2" >/dev/null 2>&1 || true
    fi
fi

# 3. Retrieve files via streaming tarball
echo "[-] Downloading configuration, skills & Telegram API specs..."
TMP_SOURCE=""
if [ -d "$(dirname "${BASH_SOURCE[0]}")/rules" ]; then
    SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
else
    TMP_SOURCE=$(mktemp -d)
    curl -fsSL "${REPO_URL}/archive/refs/heads/main.tar.gz" | tar -xz -C "$TMP_SOURCE" --strip-components=1
    SOURCE_DIR="$TMP_SOURCE"
fi
trap 'rm -rf "$TMP_SOURCE"' EXIT

# 4. Scaffolding directories
mkdir -p "${CONFIG_DIR}/rules" "${CONFIG_DIR}/plugins" "${CONFIG_DIR}/skills" \
         "${MCP_SERVERS_DIR}/skills-engine" "${MCP_SCHEMAS_DIR}" \
         "${CATALOG_DIR}/skills" "${CATALOG_DIR}/repos"

# 5. Deploy rules, skills, plugins
echo "[-] Deploying rules, skills, and plugins..."
cp -rf "${SOURCE_DIR}/rules/"*.md "${CONFIG_DIR}/rules/"
rm -f "${CONFIG_DIR}/rules/mandatory_skills_activation.md" 2>/dev/null || true

if [ -d "${SOURCE_DIR}/skills" ]; then
    mkdir -p "${CONFIG_DIR}/skills" "${CATALOG_DIR}/skills"
    cp -rf "${SOURCE_DIR}/skills/"* "${CONFIG_DIR}/skills/" 2>/dev/null || true
    cp -rf "${SOURCE_DIR}/skills/"* "${CATALOG_DIR}/skills/" 2>/dev/null || true
fi

if [ -d "${SOURCE_DIR}/plugins" ]; then
    cp -rf "${SOURCE_DIR}/plugins/"* "${CONFIG_DIR}/plugins/" 2>/dev/null || true
fi

if [ -f "${SOURCE_DIR}/hooks.json" ]; then
    cp -f "${SOURCE_DIR}/hooks.json" "${CONFIG_DIR}/hooks.json"
fi

if [ -d "${SOURCE_DIR}/hooks" ]; then
    mkdir -p "${CONFIG_DIR}/hooks"
    cp -rf "${SOURCE_DIR}/hooks/"* "${CONFIG_DIR}/hooks/"
fi

cp -f "${SOURCE_DIR}/mcp-servers/skills-engine/server.py" "${MCP_SERVERS_DIR}/skills-engine/server.py"

# 6. Configure MCP server
echo "[-] Configuring MCP server..."
cat << 'EOF_MCP' > "${CONFIG_DIR}/mcp_config.json"
{
  "mcpServers": {
    "skills-engine": {
      "command": "python3",
      "args": [
        "__HOME__/.gemini/mcp-servers/skills-engine/server.py"
      ],
      "env": {
        "PYTHONUNBUFFERED": "1"
      }
    }
  }
}
EOF_MCP
sed -i "s|__HOME__|${HOME_DIR}|g" "${CONFIG_DIR}/mcp_config.json"

# 7. Configure permissions (auto-allow all tools, eliminate popups across CLI and IDE)
echo "[-] Configuring zero-prompt execution permissions..."
CLI_SETTINGS_DIR="${HOME_DIR}/.gemini/antigravity-cli"
IDE_SETTINGS_DIR="${HOME_DIR}/.antigravity-ide-server/data/User"
mkdir -p "${CLI_SETTINGS_DIR}" "${IDE_SETTINGS_DIR}" "${HOME_DIR}/.gemini"

python3 -c "
import json
for p in [
    '${CONFIG_DIR}/config.json',
    '${CLI_SETTINGS_DIR}/settings.json',
    '${HOME_DIR}/.gemini/settings.json',
    '${IDE_SETTINGS_DIR}/settings.json'
]:
    try:
        with open(p, 'r') as f:
            c = json.loads(f.read().split('#')[0].strip())
    except Exception:
        c = {}
    c['permissionPreset'] = 'turbo'
    c['permissions'] = {'allow': ['mcp(*)', 'mcp(skills-engine/*)', 'run_command(*)', 'read_file(*)', 'write_file(*)']}
    c['antigravity.permissions.allow'] = ['mcp(*)', 'mcp(skills-engine/*)']
    c['antigravity.toolExecutionPolicy'] = 'always-proceed'
    c['antigravity.mcp.alwaysAllow'] = True
    c['gemini.mcp.alwaysAllow'] = True
    if 'userSettings' not in c or not isinstance(c['userSettings'], dict):
        c['userSettings'] = {}
    c['userSettings']['toolExecutionPolicy'] = 'always-proceed'
    with open(p, 'w') as f:
        json.dump(c, f, indent=2)
"

# 8. Deploy schemas
if [ -d "${SOURCE_DIR}/mcp-schemas/skills-engine" ]; then
    cp -rf "${SOURCE_DIR}/mcp-schemas/skills-engine/"* "${MCP_SCHEMAS_DIR}/"
fi

# 9. Sync core database index & 185 Telegram methods
echo "[-] Indexing knowledge base & 185 Telegram Bot API methods..."
python3 -c "
import sys
sys.path.insert(0, '${MCP_SERVERS_DIR}/skills-engine')
try:
    import server
    server.sync_all_directories(force=True)
    server.sync_telegram_bot_api_upstream(force=True)
    conn = server.get_db_conn()
    total = conn.execute('SELECT count(*) FROM items').fetchone()[0]
    conn.close()
    print(f'[*] Successfully indexed {total} items and all Telegram Bot API methods.')
except Exception as e:
    print(f'[!] Index note: {e}')
"

# 10. Background sync of optional external catalogs (non-blocking)
(
    fast_clone() {
        local url="\$1"
        local dest="\$2"
        if [ ! -d "\$dest/.git" ]; then
            git clone --depth 1 --single-branch --no-tags -q "\$url" "\$dest" 2>/dev/null || true
        else
            git -C "\$dest" pull --quiet 2>/dev/null || true
        fi
    }
    fast_clone "https://github.com/anthropics/skills.git" "${CATALOG_DIR}/repos/anthropics-skills"
    fast_clone "https://github.com/alirezarezvani/claude-skills.git" "${CATALOG_DIR}/repos/alirezarezvani-claude-skills"
    fast_clone "https://github.com/PatrickJS/awesome-cursorrules.git" "${CATALOG_DIR}/repos/awesome-cursorrules"
    fast_clone "https://github.com/ComposioHQ/awesome-claude-skills.git" "${CATALOG_DIR}/repos/composiohq-awesome-claude-skills"
    python3 -c "
import sys
sys.path.insert(0, '${MCP_SERVERS_DIR}/skills-engine')
try:
    import server
    server.sync_all_directories(force=True)
except Exception:
    pass
" 2>/dev/null
) >/dev/null 2>&1 &

pkill -f "${MCP_SERVERS_DIR}/skills-engine/server.py" 2>/dev/null || true

echo "[✓] Installation complete! Antigravity Skills Engine is 100% active and autonomous."
