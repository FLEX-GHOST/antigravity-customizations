---
name: dart-flutter-architecture
description: Definitive skill for Dart 3 and Flutter cross-platform architecture, covering Riverpod, BLoC, Isolate concurrency, and 60/120 FPS rendering.
language: dart
category: programming-languages
quality_score: 100
tier: official
triggers:
  - dart
  - flutter
  - riverpod
  - bloc
  - isolates
  - mobile
  - cross-platform
  - widget
---
# Dart 3 & Flutter Enterprise Clean Architecture

Comprehensive guidelines for architecting clean, maintainable, and high-frame-rate mobile and desktop Flutter apps.

## 1. Dart 3 Features & Type Safety
* **Records & Pattern Matching**: Eliminate boilerplate tuple classes and use native records with destructuring.
  ```dart
  (double lat, double lon) parseCoordinates(Map<String, dynamic> json) {
    if (json case {'lat': double lat, 'lon': double lon}) {
      return (lat, lon);
    }
    throw FormatException('Invalid coordinates');
  }
  ```
* **Class Modifiers**: Use `sealed`, `base`, and `interface` to enforce strict domain hierarchies and exhaustive switch statements.

## 2. Flutter Performance & State Architecture
* **Concentric Rebuild Optimization**: Split UI into small `const` widgets to ensure only modified subtrees re-render.
* **Heavy Processing in Isolates**: Offload JSON parsing, crypto operations, and image manipulation to background isolates (`compute()` or `Isolate.run()`).
* **Clean State Management**: Enforce separation between View, Presentation Controller (Riverpod / BLoC), and Domain Repositories.
