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

### LLM Configuration

The game supports multiple LLM providers for enhanced AI-driven gameplay. Configure once and the entire application will use your preferred provider.

#### Option 1: Mock LLM (Default)
No configuration needed. Uses simple rule-based updates for testing and development.

```bash
# This is the default - no environment variables needed
python main.py server
```

#### Option 2: LM Studio (Recommended for Local AI)
[LM Studio](https://lmstudio.ai/) provides local LLM inference with an OpenAI-compatible API.

**Setup Steps:**

1. **Download and install LM Studio** from https://lmstudio.ai/
2. **Load a model** in LM Studio (e.g., a 7B or 13B parameter model)
3. **Start the local server** in LM Studio (usually runs on port 1234)
4. **Configure environment variables:**

```bash
export LLM_PROVIDER=lmstudio
export LMSTUDIO_MODEL="your-model-name"  # e.g., "llama-2-7b-chat"
export LMSTUDIO_BASE_URL="http://localhost:1234/v1"  # default LM Studio URL
```

5. **Start the game server:**
```bash
python main.py server
```

The server will validate your LLM configuration on startup and provide helpful error messages if misconfigured.

#### Option 3: Environment File (Recommended)
Create a `.env` file in the project root for persistent configuration:

```bash
# .env file
LLM_PROVIDER=lmstudio
LMSTUDIO_MODEL=llama-2-7b-chat
LMSTUDIO_BASE_URL=http://localhost:1234/v1
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=1000
```

#### Verify Configuration
Check your LLM configuration at any time:
```bash
curl http://localhost:8000/api/config
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

### Database Reset (Fresh Start)

The game uses a persistent SQLite database (`game.db`) to store all events and game state. For testing or to start fresh:

```bash
# Start server with clean database
python main.py server --reset

# Or via environment variable
RESET_DB=true python main.py server

# Also works with other commands
python main.py test --reset
python main.py simulate --reset

# Custom database location
DB_PATH=/path/to/my/game.db python main.py server
```

**When to use `--reset`:**
- First time setup
- Testing or development
- When you see old data from previous runs
- To start a completely fresh season

**Note:** Resetting deletes all match history, reports, and progress. Use with caution in production saves.

## Features

- **Two Fantasy Leagues**: Premier Fantasy League and La Fantasia League
- **Fantasy Teams & Players**: No real-world IP, all fantasy names
- **Match Simulation**: Deterministic events (goals, cards, substitutions)
- **AI-Driven Psychology**: Choose between mock LLM or local LM Studio for dynamic player/team morale and form updates
- **Local AI Support**: Easy integration with LM Studio for private, local LLM inference
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
