#!/usr/bin/env bash
set -e

TARGET="${HOME}/.gemini/config"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

echo "=== Installing Antigravity Global Rules & Skills ==="
mkdir -p "${TARGET}/rules" "${TARGET}/skills" "${TARGET}/plugins"

cp -rf "${SCRIPT_DIR}/rules/"* "${TARGET}/rules/"
cp -rf "${SCRIPT_DIR}/skills/"* "${TARGET}/skills/"
if [ -d "${SCRIPT_DIR}/plugins" ]; then
    cp -rf "${SCRIPT_DIR}/plugins/"* "${TARGET}/plugins/"
fi

echo "=== Done! All 27 rules and 95 skills installed into ${TARGET} ==="
