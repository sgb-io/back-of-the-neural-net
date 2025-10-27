# Demo Scripts

This directory contains demonstration scripts that showcase various features and capabilities of Back of the Neural Net.

## Basic Demos

### demo.py
Basic game simulation demonstration showing:
- World initialization
- League and team information
- Player roster examples
- Simple simulation step

**Usage:**
```bash
python scripts/demos/demo.py
```

### demo_llm.py
LLM integration demonstration showing:
- LLM provider configuration
- Mock LLM behavior
- LM Studio integration examples
- Narrative generation

**Usage:**
```bash
python scripts/demos/demo_llm.py
```

### demo_tools.py
Demonstration of available tools and utilities:
- Event store operations
- World state queries
- Data manipulation examples

**Usage:**
```bash
python scripts/demos/demo_tools.py
```

## Feature Showcase Demos

### demo_todo_features.py
Comprehensive demonstration of all implemented features:
- Match statistics (possession, shots, corners)
- Financial system (prize money, TV revenue)
- Clean sheets and records
- Player attributes and ratings

**Usage:**
```bash
python scripts/demos/demo_todo_features.py
```

### demo_todo_basket.py
Original feature basket demonstration (Round 1):
- Penalty kicks
- Fouls tracking
- Team streaks
- Top assisters

**Usage:**
```bash
python scripts/demos/demo_todo_basket.py
```

### Feature Round Demos

- **demo_todo_basket_round4.py** - Weak foot ratings, match ratings, free kicks
- **demo_todo_basket_round5.py** - Skill moves, career stats, league history
- **demo_todo_basket_round6.py** - Weather, attendance, player development
- **demo_todo_basket_round7.py** - Pitch conditions, captains, average ratings

## Running Demos

All demos can be run directly from the project root:

```bash
# Run any demo
python scripts/demos/<demo_name>.py

# Examples
python scripts/demos/demo.py
python scripts/demos/demo_todo_features.py
python scripts/demos/demo_llm.py
```

## Purpose

These scripts serve multiple purposes:
- **Learning**: Understand how the system works
- **Testing**: Verify features work as expected
- **Documentation**: Examples of API usage
- **Development**: Quick experimentation with features
