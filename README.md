# Back of the Neural Net

A football management simulation that combines deterministic match simulation with LLM-driven player psychology and narratives.

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

- **Two Fantasy Leagues**: Premier Fantasy League and La Fantasia League with fantasy teams & players
- **Match Simulation**: Deterministic events (goals, cards, substitutions) with live event streams
- **AI-Driven Psychology**: LLM-powered player/team morale, form, and narrative generation
- **Club Entities**: Owners, media outlets, player agents, and staff members with dynamic relationships
- **League Tables**: Live updating standings with simple one-button UI advancement

## Game Flow

1. Press "Advance Simulation" to progress one matchday
2. All matches for current matchday are simulated
3. LLM analyzes events and updates soft state (morale, form, owner satisfaction, staff rapport, etc.)
4. Media outlets and other entities react to results and generate narratives
5. League tables and fixtures update
6. Repeat until season completion

## Architecture Details

**Core Components:** Event-sourced design with SQLite storage. Key modules include `entities.py` (game models), `simulation.py` (match engine), `llm.py` (AI integration), and `server.py` (FastAPI REST API).

**API Endpoints:** `/api/world` (game state), `/api/advance` (simulation step), `/api/leagues/{id}/table`, `/api/fixtures`, `/api/events/stream` (live events).

## Testing

```bash
python main.py test        # Basic test
python tests/test_basic.py # Run specific tests
pytest tests/              # Full test suite
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

Built with ⚽ for the love of football simulation.
