---
name: elixir-phoenix-otp
description: Definitive skill for building massively concurrent, fault-tolerant applications using Elixir, Erlang BEAM, GenServer, Supervision Trees, and Phoenix LiveView.
language: elixir
category: programming-languages
quality_score: 100
tier: official
triggers:
  - elixir
  - phoenix
  - liveview
  - otp
  - beam
  - genserver
  - erlang
  - mix
---
# Elixir, Phoenix LiveView & Fault-Tolerant OTP Systems

Architectural principles for high-concurrency, zero-downtime distributed systems on the Erlang BEAM VM.

## 1. Fault Tolerance & OTP Supervision
* **Let It Crash Philosophy**: Do not defensively wrap every operation in try/rescue. Allow worker processes to crash and let supervisors restore them to a clean state.
* **Supervision Tree Design**: Structure processes into hierarchical supervisor trees with appropriate restart strategies (`:one_for_one`, `:one_for_all`, `:rest_for_one`).
  ```elixir
  defmodule MyApp.SessionWorker do
    use GenServer, restart: :transient

    def start_link(session_id) do
      GenServer.start_link(__MODULE__, session_id, name: via_tuple(session_id))
    end

    @impl true
    def init(session_id) do
      {:ok, %{session_id: session_id, count: 0}}
    end

    @impl true
    def handle_call(:increment, _from, state) do
      new_state = %{state | count: state.count + 1}
      {:reply, new_state.count, new_state}
    end
  end
  ```

## 2. Phoenix LiveView Real-Time Architecture
* **Server-Driven UIs**: Handle real-time user interaction over WebSockets with minimal latency and zero heavy client-side state frameworks.
* **Presence & PubSub**: Broadcast state mutations efficiently across distributed cluster nodes using `Phoenix.PubSub`.
