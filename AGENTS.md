# What is Back of the Neural Net?

The rough idea with this project is to write my own FM engine that combines logic + RNG with LLMs to produce a dynamic experience. For instance, matches would take the players and tactics as input and use a logical simulation with some RNG and chance-based algorithms to generate match simulations. But an LLM would be used to update a player's fitness, form, perception to others, perception of others, world views according to other world events, etc. Historically this latter part would require a huge cumbersome logic engine (I imagine most of the guts of FM is very ugly with millions of conditionals etc), but with LLMs, this can be made (a) much more dynamic, interesting and realistic and (b) much simpler.

# Initial Design

Note that the actual implementations could potentially differ from what is described here. What is described here is the initial design used to get the project underway (without the benefit of hindsight or knowledge of what worked well or did not). As a rule, treat the code as the source of truth.

### Goals and Non-Goals

Goals

- Deterministic, fast match simulation (text event stream).
- LLM-driven soft state (morale, relationships, narratives) behind a provider-agnostic interface.
- Portable: Python 3.11+, SQLite; no system services required.
- Parallel simulation of rounds; reproducible via seeds; offline/cached LLM mode.
- Minimal React UI consumes a small HTTP API (SSE/WebSocket for live events).

Non-Goals (for v1)

- No 2D/3D match renderer (text ticker only).
- No real-world IP (use fantasy packs).
- No complex distributed infra (keep single-host friendly; optional adapters later).

### Features and Scope

For now, the player just presses an 'Advance' button to trigger the next step in the simulaton, and can see the events and state of the game. The player does not pick a team or control any aspect of the simulation. These kinds of inputs will be added later (so this should be kept in mind when adding features and making changes).

We should avoid using real team or player names in the code (including tests) and use dummy/parody names instead. The game should allow the user to provide team names locally in some way (e.g. supplying a CSV). The world could be restricted to just 2 leagues for now (the top english and spanish divisons, with no cup competitions).

This means there is no concept of manager responsibilities.
There should also be no concept of player transfers, player loans, U21 or U18 squads, or national teams.

### Core principles

1. Hard vs. soft state

- Hard (deterministic): match ticks, physics-lite events, injuries occurring in match, contracts math, finances. Lives in Rust engine. Reproducible via seeds.
- Soft (LLM-derived): form, morale, relationships, media narratives, “player world views”, scouting blurbs. Computed by brains; validated & clamped by rules before writing back.

2. Event-sourced world

- Append-only event log (SQLite by default; easy, portable). Snapshots every N events.
- Everything (fixtures, substitutions, post-match updates) is an event. Enables replays, diffs, and deterministic rollback.

3. Strict contracts, loose creativity

- All cross-process IO is structured JSON validated against JSON Schema.
- LLM outputs must conform to schemas (use function-calling / JSON mode) and are post-validated (range checks, invariants).

### Execution model (per matchday)

- Pre-match brains propose soft adjustments → validator clamps → write SoftStateUpdated events.
- Engine runs match with seed → emits MatchEvent* stream + MatchResult.
- Post-match brains read match events + context → propose updates (form/morale/relations/media) → validate → events.
- Snapshot world every N matches; keep seeds & prompt hashes for reproducibility.

### Determinism & speed

- Deterministic core: all probabilities seeded; same inputs → same events.
- LLM nondeterminism: freeze via cache; include model, temperature, and local seed in key. Provide --offline mode to replay from cache.
- Parallelism: Rayon in Rust for match batches; multi-process brains (Python) using concurrent.futures.ProcessPoolExecutor or Ray (optional).
- Zero-pain deps: SQLite bundled; no system services required. Optional extras (Redis/NATS/Ray) gated behind feature flags.

### Technology Choices

- Core simulation engine in Python
- The player interacts with the game using a basic React UI
