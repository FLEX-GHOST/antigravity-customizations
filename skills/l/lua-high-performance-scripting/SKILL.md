---
name: lua-high-performance-scripting
description: Master engineering guide for Lua 5.4 and LuaJIT covering table memory layouts, FFI bindings, Neovim plugin architecture, and atomic Redis scripting.
language: lua
category: programming-languages
quality_score: 100
tier: official
triggers:
  - lua
  - luajit
  - neovim
  - redis
  - ffi
  - scripting
  - openresty
---
# Lua 5.4 & LuaJIT High-Performance Scripting Architecture

Engineering standards for high-speed scripting, Redis atomic procedures, and LuaJIT systems.

## 1. Table Optimization & Memory Hygiene
* **Array vs Hash Parts**: Initialize tables intended as arrays with sequential numeric keys to ensure Lua stores them in its contiguous array part, reducing memory overhead by up to 50%.
* **Local Caching of Globals**: Always cache frequently called global functions (`local math_floor = math.floor`) inside module scope to bypass table lookup overhead.
  ```lua
  local M = {}
  local table_insert = table.insert

  function M.filter_records(records, threshold)
      local valid = {}
      for i = 1, #records do
          local rec = records[i]
          if rec.score >= threshold then
              table_insert(valid, rec)
          end
      end
      return valid
  end

  return M
  ```

## 2. LuaJIT FFI & Redis Atomic Scripts
* **Zero-Overhead C Calls**: Use `require("ffi")` to bind directly to native C libraries without compiling C extensions.
* **Redis Scripting**: Ensure all Redis Lua scripts are strictly deterministic, avoiding global state mutation and non-reproducible random calls.
