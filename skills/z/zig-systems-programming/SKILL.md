---
name: zig-systems-programming
description: Comprehensive engineering skill for Zig systems programming, covering explicit memory allocation, Comptime metaprogramming, C interop, and memory safety.
language: zig
category: programming-languages
quality_score: 100
tier: official
triggers:
  - zig
  - comptime
  - allocator
  - systems
  - c interop
  - embedded
  - build.zig
---
# Zig Systems Programming, Explicit Allocators & Comptime

Architectural guidelines for writing safe, performant, and transparent systems software in Zig.

## 1. Explicit Memory Management
* **No Hidden Allocations**: All functions requiring memory allocation must accept an explicit `std.mem.Allocator` parameter.
* **GeneralPurposeAllocator Hygiene**: Always run debug builds with `std.heap.GeneralPurposeAllocator` to detect memory leaks and use-after-free errors at exit.
  ```zig
  const std = @import("std");

  pub fn fetchRecord(allocator: std.mem.Allocator, id: u64) ![]u8 {
      const buffer = try allocator.alloc(u8, 1024);
      errdefer allocator.free(buffer);
      
      // Perform population
      return buffer;
  }
  ```

## 2. Comptime Metaprogramming
* **Type-Level Computations**: Use `comptime` for generic data structures, compile-time format string validation, and zero-runtime-overhead abstractions.
* **C Interoperability**: Directly `@cImport` existing C headers without writing boilerplate binding code.
