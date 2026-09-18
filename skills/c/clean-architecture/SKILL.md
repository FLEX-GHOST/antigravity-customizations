---
name: clean-architecture
description: 'Design decoupled, testable, and maintainable software systems following Clean Architecture, the Dependency Rule, SOLID principles, and hexagonal patterns. Covers entity modeling, use case interactors, input/output ports, interface adapters, boundary crossing, the Humble Object pattern, and component cohesion/coupling.'
license: MIT
metadata:
  author: wondelai
  version: "2.0.0"
---

# Clean Architecture: Master Architectural Engineering Guide

A comprehensive architectural standard for building decoupled, testable, and maintainable systems where business logic remains independent of frameworks, databases, and UI delivery mechanisms. Based on Robert C. Martin's *Clean Architecture*.

---

## 1. The Dependency Rule: Concentric Circles

> [!CRITICAL]
> **Source code dependencies must point only inward**, toward higher-level policies. Nothing in an inner circle can know anything about an outer circle.
> - Inner circles must never mention names, functions, classes, database schemas, or wire formats declared in outer circles.
> - Data crossing boundaries must be in the format most convenient for the inner circle (plain DTOs or primitives).

```
   +-----------------------------------------------------------+
   |                  Frameworks & Drivers                     |
   |   (Web, DB, Devices, UI, External APIs, CLI, Telegram)     |
   |   +---------------------------------------------------+   |
   |   |               Interface Adapters                  |   |
   |   |      (Controllers, Gateways, Presenters, DTOs)     |   |
   |   |   +-------------------------------------------+   |   |
   |   |   |             Application Use Cases         |   |   |
   |   |   |      (Interactors, Input & Output Ports)   |   |   |
   |   |   |   +-----------------------------------+   |   |   |
   |   |   |   |             Entities              |   |   |   |
   |   |   |   |     (Enterprise Business Rules)   |   |   |   |
   |   |   |   +-----------------------------------+   |   |   |
   |   |   +-------------------------------------------+   |   |
   |   +---------------------------------------------------+   |
   +-----------------------------------------------------------+
               Dependency Direction: ALL ARROWS POINT INWARD
```

### Layer Breakdown

| Layer | Circle | Primary Responsibility | Allowed Dependencies |
|---|---|---|---|
| **Entities** | Innermost (1) | Core business models and enterprise validation invariants | None (Pure domain) |
| **Use Cases** | Inner (2) | Orchestrates domain entities to execute user goals (interactors) | Entities only |
| **Interface Adapters** | Middle (3) | Converts data between use cases and external mechanisms | Use Cases & Entities |
| **Frameworks & Drivers**| Outermost (4)| Database drivers, HTTP servers, Telegram SDK, CLI runtimes | Adapters & Inward |

---

## 2. Boundary Anatomy & Port Architecture

Boundaries protect high-level business policies from low-level implementation details through dependency inversion (polymorphism).

### Complete Boundary Crossing Anatomy

```
[ Outer Delivery Mechanism ]         |       [ Inner Application Core ]
                                    |
HTTP / Telegram Controller           |
       |                            |
       | calls                      |
       v                            |
[ Input Port (Interface) ] <--------+------ implemented by:
                                    |       [ Use Case Interactor ]
                                    |               |
                                    |               | executes domain logic
                                    |               v
                                    |       [ Domain Entity ]
                                    |               |
                                    |               | calls
                                    |               v
[ Output Port / Gateway Interface ] +<------+-------+
       ^                            |
       | implemented by             |
[ SQL Database / External Client ]  |
```

### Input & Output DTOs
- Never pass database ORM models, HTTP request bodies, or Telegram update objects directly into the Use Case.
- Define pure, plain **Input DTOs** and **Output DTOs** owned by the Use Case layer.

---

## 3. The Humble Object Pattern

The Humble Object pattern separates behaviors that are difficult to test (such as GUI layouts, async web sockets, or Telegram webhooks) from behaviors that are trivial to unit test:

1. **The Humble Component (Outer)**: Contains minimal or zero logic. Receives the raw event or update, extracts primitives, calls the Interactor, and passes the output to the Presenter.
2. **The Testable Interactor (Inner)**: Contains all business calculations, authorization checks, and workflow decisions. Runs purely in-memory with zero mock frameworks required.

---

## 4. SOLID Principles in System Design

| Principle | Architectural Impact | Clean Implementation |
|---|---|---|
| **Single Responsibility (SRP)** | A module should have one, and only one, reason to change (one actor). | Separate financial calculation from report generation and database storage. |
| **Open/Closed (OCP)** | Software artifacts should be open for extension, closed for modification. | Add new bot payment methods by implementing a new Gateway adapter without altering core checkout use cases. |
| **Liskov Substitution (LSP)** | Subtypes must be substitutable for their base types without altering correctness. | Any implementation of `UserRepository` must satisfy the exact contract of the interface. |
| **Interface Segregation (ISP)** | Clients should not depend on methods they do not use. | Prefer small, focused role interfaces (`UserReader`, `UserWriter`) over giant monolithic repositories. |
| **Dependency Inversion (DIP)** | High-level policies should not depend on low-level details. Both depend on abstractions. | Use cases define the repository interface; the SQL database module implements it. |

---

## 5. Component Cohesion & Coupling Principles

When partitioning a growing codebase into crates, packages, or vertical features:

### Principles of Component Cohesion
1. **REP (Reuse/Release Equivalence Principle)**: The granule of reuse is the granule of release. Code bundled together must be tracked and versioned together.
2. **CCP (Common Closure Principle)**: Gather into components those classes that change for the same reasons and at the same times. Minimize the blast radius of changes.
3. **CRP (Common Reuse Principle)**: Do not force users of a component to depend on things they don't need.

### Principles of Component Coupling
1. **ADP (Acyclic Dependencies Principle)**: The dependency graph of components must contain no directed cycles. If Component A depends on B, B must never depend on A.
2. **SDP (Stable Dependencies Principle)**: Depend in the direction of stability. Stable components (depended upon by many) should have zero or few outgoing dependencies.
3. **SAP (Stable Abstractions Principle)**: A component should be as abstract as it is stable. Highly stable components should consist primarily of interfaces and abstract policies.

---

## 6. The Main Component as the Ultimate Plugin

`main.rs` (or `index.ts`) is the dirtiest component in the system. It is the composition root:
- It knows about every database, framework, secret, and concrete adapter.
- It instantiates concrete database pools, builds HTTP listeners, injects gateways into use cases, and registers event handlers.
- Treat `Main` as a plugin to the architecture. The entire system can be instantiated with mock gateways for end-to-end testing simply by replacing `Main`.

---

## 7. Architectural Anti-Patterns & Pragmatic Boundaries

- **Database-Driven Design**: Designing database schemas first and forcing domain entities to mirror relational foreign keys. *Entities represent domain invariants, not SQL rows.*
- **Framework Bleed**: Adding framework annotations (`@Entity`, `#[derive(Serialize)]`, or HTTP decorators) directly onto core enterprise business models. Keep domain entities framework-free.
- **Anemic Domain Model**: Modeling entities as dumb data bags with public getters/setters, while scattering business rules across procedural service scripts. Put behavior inside entities.
- **Premature Microservices**: Splitting a small application into 10 network services before establishing clean in-process modular boundaries. *Clean Architecture provides modularity in a monolith without the operational tax of distributed systems.*
