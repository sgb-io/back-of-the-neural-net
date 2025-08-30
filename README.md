# Back of the Neural Net

Proper football. Artificial brains.

A football management simulation that combines deterministic match simulation with LLM-driven soft state management for player morale, relationships, and narratives.

## Architecture

- **Event-sourced**: All game state changes are recorded as events in SQLite
- **Hard vs Soft State**: Match simulation is deterministic; player psychology is LLM-driven
- **Python Core**: Core simulation engine with FastAPI REST API
- **TypeScript + Next.js UI**: Modern web interface with "Advance" button to progress simulation

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 16+ (for UI)

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
# Start server
python main.py server

# Run headless simulation
python main.py simulate

# Run basic tests
python main.py test
```

## Features

- **Two Fantasy Leagues**: Premier Fantasy League and La Fantasia League
- **Fantasy Teams & Players**: No real-world IP, all fantasy names
- **Match Simulation**: Deterministic events (goals, cards, substitutions)
- **LLM Integration**: Mock LLM updates player/team morale based on events
- **League Tables**: Live updating standings
- **Event Stream**: Real-time match events
- **Simple UI**: One-button advancement with live updates

### New Simulation Entities

- **Club Owners/Directors**: Each team has ownership with wealth, ambition, patience, and public approval ratings that change based on performance
- **Media Outlets**: Fantasy press entities that generate narratives and maintain biases toward different teams
- **Player Agents**: Professional representatives for ~70% of players with negotiation skills and industry reputation
- **Staff Members**: Coaches, physios, scouts, and other team personnel with morale and team rapport that affects performance

## Game Flow

1. Press "Advance Simulation" to progress one matchday
2. All matches for current matchday are simulated
3. LLM analyzes events and updates soft state (morale, form, owner satisfaction, staff rapport, etc.)
4. Media outlets and other entities react to results and generate narratives
5. League tables and fixtures update
6. Repeat until season completion

## Architecture Details

### Core Components

- **`entities.py`**: Game world models (Team, Player, Match, League)
- **`events.py`**: Event sourcing system with SQLite storage
- **`simulation.py`**: Deterministic match simulation engine
- **`llm.py`**: LLM integration for soft state updates
- **`orchestrator.py`**: Main game loop coordination
- **`server.py`**: FastAPI REST API
- **`data.py`**: Fantasy data generation

### API Endpoints

- `GET /api/world` - Get current world state
- `POST /api/advance` - Advance simulation one step
- `GET /api/leagues/{id}/table` - Get league table
- `GET /api/fixtures` - Get upcoming fixtures
- `GET /api/events/stream` - Server-sent events stream

## Testing

```bash
# Run basic tests
python tests/test_basic.py

# Or with pytest if available
pytest tests/

# Test new entities
python test_new_entities.py
```

## Future Enhancements

- Manager mode with tactical decisions
- Real-world data import options
- Advanced LLM prompting for narratives
- Cup competitions
- Transfer system with agent negotiations
- Player development
- Enhanced media simulation with story generation
- More sophisticated UI

---

Built with ⚽ and 🧠 for the love of football simulation.
