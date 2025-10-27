# Back of the Neural Net

A football management simulation that combines deterministic match simulation with LLM-driven player psychology and narratives.

## Architecture

- **Event-sourced**: All game state changes are recorded as events in SQLite
- **Hard vs Soft State**: Match simulation is deterministic; player psychology is LLM-driven
- **Python Core**: Core simulation engine with FastAPI REST API
- **TypeScript + Next.js UI**: Modern web interface with "Advance" button to progress simulation

### Design Philosophy

**Hard vs. Soft State:**
- **Hard (deterministic)**: Match events, physics, injuries, finances. Reproducible via seeds.
- **Soft (LLM-derived)**: Form, morale, relationships, media narratives, player psychology.

**Event-Sourced World:**
- Append-only event log in SQLite (portable, easy to query)
- Everything is an event: fixtures, substitutions, goals, post-match updates
- Enables replays, diffs, and deterministic rollback

**Execution Model (per matchday):**
1. Pre-match: LLM proposes soft adjustments → validated → events written
2. Match simulation: Deterministic engine runs with seed → emits event stream
3. Post-match: LLM analyzes events → proposes updates (form/morale) → validated → events written

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+ (for UI)

### LLM Configuration

The game supports multiple LLM providers. By default, it uses a mock LLM for testing.

**For Local AI (LM Studio):**
```bash
# Install LM Studio from https://lmstudio.ai/, load a model, start server
export LLM_PROVIDER=lmstudio
export LMSTUDIO_MODEL="your-model-name"
python main.py server
```

**Using .env file (recommended):**
```bash
# Create .env file in project root
LLM_PROVIDER=lmstudio
LMSTUDIO_MODEL=llama-2-7b-chat
LMSTUDIO_BASE_URL=http://localhost:1234/v1
```

### Installation

1. **Install Python dependencies:**
```bash
pip install -e .
```

2. **Install UI dependencies:**
```bash
cd ui
npm install
```

### Running

1. **Start the API server:**
```bash
python main.py server
```

2. **Start the Next.js UI (in a separate terminal):**
```bash
cd ui
npm run dev
```

3. **Open your browser:**
   - UI: http://localhost:3000
   - API: http://localhost:8000

## CLI Usage

```bash
# Start server (uses configured LLM provider)
python main.py server

# Run headless simulation
python main.py simulate

# Run basic tests
python main.py test

# With custom LLM configuration
LLM_PROVIDER=lmstudio LMSTUDIO_MODEL=llama-2-7b-chat python main.py server
```

### Database Reset

To start fresh or for testing:

```bash
python main.py server --reset  # Clean database
RESET_DB=true python main.py server  # Or via environment variable
```

## Features

### League System
- **Two Fantasy Leagues**: Premier Fantasy League and La Fantasia League with fantasy teams & players
- **League Tables**: Live updating standings with points, goals, position, form, and streaks
- **Fixture Scheduling**: Automated matchday scheduling with home/away rotation
- **Season Progression**: Calendar system with date tracking (weekly advancement)

### Match Simulation
- **Deterministic Events**: Goals, yellow/red cards, substitutions, injuries with seed-based reproducibility
- **Match Statistics**: Possession, shots (total/on target), corners, fouls, offsides tracking
- **Set Pieces**: Penalty kicks, corner kicks, free kicks (direct/indirect)
- **Match Atmosphere**: Weather conditions (sunny, rainy, snowy, etc.) and pitch quality
- **Live Event Streams**: Real-time match events via SSE (Server-Sent Events)
- **Player Performance**: Individual player ratings (1.0-10.0) per match with history tracking

### Player System
- **Comprehensive Attributes**: Pace, shooting, passing, defending, physicality, form, fitness
- **Player Details**: Age, position, preferred foot, weak foot rating (1-5★), skill moves (1-5★)
- **Work Rate**: Attacking/defensive work rate tracking
- **Career Statistics**: Goals, assists, appearances, average rating, yellow/red cards
- **Player Development**: Form, morale, fitness, and injury tracking
- **Contracts**: Years remaining, salary, market value

### Team Management
- **Squad Rosters**: ~25+ players per team with realistic squad depth
- **Captains**: Designated team captain and vice-captain (experience-based selection)
- **Team Statistics**: Clean sheets, home/away records, winning/losing streaks, form guide
- **Financial System**: Prize money, TV rights revenue, ticket sales, owner wealth
- **Stadium & Facilities**: Capacity, quality ratings, training ground facilities

### Club Ecosystem
- **Club Owners**: Individual owners with wealth, satisfaction tracking, and public statements
- **Media Outlets**: News organizations that publish stories and generate narratives
- **Player Agents**: Agent entities (foundation for future contract negotiations)
- **Staff Members**: Coaches, scouts, physios, and other club staff
- **Team Rivalries**: Historical rivals with tracked head-to-head records

### AI-Driven Features
- **LLM-Powered Psychology**: Player and team morale, form, relationships
- **Dynamic Narratives**: Media stories and reactions to match events
- **Soft State Management**: Owner satisfaction, staff rapport, fan sentiment (LLM-driven)
- **Provider Agnostic**: Supports multiple LLM providers (LM Studio, mock for testing)

## Game Flow

1. Press "Advance Simulation" to progress one matchday
2. All matches for current matchday are simulated
3. LLM analyzes events and updates soft state (morale, form, owner satisfaction, staff rapport, etc.)
4. Media outlets and other entities react to results and generate narratives
5. League tables and fixtures update
6. Repeat until season completion

## Architecture Details

**Core Components:** Event-sourced design with SQLite storage. Key modules include `entities.py` (game models), `simulation.py` (match engine), `llm.py` (AI integration), and `server.py` (FastAPI REST API).

**API Endpoints:** 
- `/api/world` - Complete game state
- `/api/advance` - Progress simulation by one matchday
- `/api/leagues/{id}/table` - League standings
- `/api/leagues/{id}/top-scorers` - Top goal scorers
- `/api/fixtures` - Match schedule
- `/api/matches/{id}/player-ratings` - Individual match player ratings
- `/api/events/stream` - Live event stream (SSE)

## Project Structure

```
back-of-the-neural-net/
├── src/neuralnet/          # Core simulation engine
│   ├── entities.py         # Game models (teams, players, leagues)
│   ├── simulation.py       # Match simulation engine
│   ├── events.py           # Event-sourced events
│   ├── llm.py              # LLM provider interface
│   ├── llm_lmstudio.py     # LM Studio integration
│   ├── orchestrator.py     # Game orchestration
│   ├── server.py           # FastAPI REST API
│   └── data.py             # Sample world creation
├── ui/                     # Next.js + TypeScript UI
│   ├── src/                # React components
│   └── public/             # Static assets
├── tests/                  # Test suite
├── scripts/demos/          # Demo and example scripts
├── docs/archive/           # Historical implementation docs
├── main.py                 # CLI entry point
└── README.md               # This file
```

## Testing

Run the test suite to validate the implementation:

```bash
# Run all tests with pytest
pip install -e ".[dev]"  # Install dev dependencies
pytest tests/            # Full test suite (160+ tests)

# Run specific test files
python tests/test_basic.py              # Core functionality
python tests/test_match_statistics.py   # Match stats
python tests/test_financial_and_stats.py # Financial system

# Run simple test without dependencies
python tests/simple_test.py

# Run main test command
python main.py test
```

### Demo Scripts

Explore features interactively with demo scripts:

```bash
# Basic demos
python scripts/demos/demo.py                # Basic simulation
python scripts/demos/demo_llm.py            # LLM integration demo
python scripts/demos/demo_tools.py          # Tools demonstration

# Feature-specific demos
python scripts/demos/demo_todo_features.py  # All implemented features
python scripts/demos/demo_todo_basket.py    # Feature basket showcase
```

## Future Enhancements

See [TODO.md](TODO.md) for a comprehensive list of features compared to modern Football Manager.

**High Priority:**
- Manager mode with tactical decisions and team selection
- Transfer system with agent negotiations
- Contract renewal and player demands
- Cup competitions (domestic and international)
- Training schedules and player development
- Advanced tactical system (formations, instructions)
- Press conferences and media interactions

**Scope Decisions (v1):**
- ❌ No 2D/3D match visualization (text ticker only)
- ❌ No real-world team/player names (fantasy names by design)
- ❌ No youth squads (U21/U18)
- ❌ No national teams or international tournaments
- ❌ No player transfers yet (coming in future versions)

## Documentation

- **[README.md](README.md)** - This file (getting started, features, architecture)
- **[TODO.md](TODO.md)** - Comprehensive feature comparison with FM
- **[AGENTS.md](AGENTS.md)** - Initial design philosophy and principles
- **[docs/archive/](docs/archive/)** - Historical implementation summaries

## Contributing

This project follows these principles:
- **Deterministic core**: All match simulation must be reproducible with seeds
- **Event-sourced**: State changes through append-only events
- **LLM for creativity**: Use LLMs for narratives, psychology, and soft state
- **Fantasy names**: No real-world team/player IP in code or tests
- **Minimal dependencies**: SQLite, Python 3.11+, no system services required

---

Built with ⚽ for the love of football simulation.
