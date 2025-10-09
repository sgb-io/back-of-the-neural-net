# TODO: Outstanding Features Compared to Modern Football Manager

This document tracks features that are missing from Back of the Neural Net when compared to modern Football Manager games. Features are categorized and marked with their current status.

**Legend:**
- ✅ Implemented
- 🚧 Partially Implemented
- ❌ Not Implemented
- 🚫 Out of Scope (v1)

---

## 1. Match & Competition System

### Match Simulation
- ✅ Basic match simulation with deterministic events
- ✅ Goals, yellow cards, red cards, substitutions
- ✅ Injuries during matches
- ✅ Match minute progression (90 minutes)
- ✅ Live event streaming
- ✅ Match statistics (possession, shots, corners tracked)
- ✅ Possession tracking
- ✅ Shot statistics (on target, off target)
- ✅ Corner kicks
- ✅ Free kicks (direct and indirect)
- ✅ Penalty kicks
- ✅ Offsides
- ✅ Fouls and foul statistics
- ✅ Match commentary/text ticker
- ❌ Extra time and penalty shootouts
- ✅ Weather conditions affecting match
- ❌ Pitch conditions
- ✅ Crowd attendance and atmosphere
- 🚫 2D/3D match visualization

### Competition Structure
- ✅ League system (2 leagues: Premier Fantasy, La Fantasia)
- ✅ League tables with points, goals, position
- ✅ Fixture scheduling
- ✅ Season progression via matchdays
- ❌ Multiple divisions with promotion/relegation
- ❌ Cup competitions (FA Cup, League Cup equivalent)
- ❌ European competitions (Champions League, Europa League)
- ❌ Super Cup / Community Shield
- ❌ Pre-season friendlies
- ❌ Mid-season breaks
- ❌ Playoff systems
- 🚫 International tournaments
- 🚫 National team competitions

---

## 2. Squad Management

### Player Information
- ✅ Player attributes (pace, shooting, passing, defending, physicality)
- ✅ Player positions
- ✅ Player age and peak age
- ✅ Player form and morale (LLM-driven)
- ✅ Player fitness/sharpness
- ✅ Player injuries
- ✅ Player contracts (years remaining, salary)
- ✅ Player market value
- ✅ Player reputation
- 🚧 Player development (limited)
- ❌ Detailed player roles (ball-winning midfielder, target man, etc.)
- ✅ Preferred foot
- ✅ Weak foot rating
- ✅ Skill moves rating
- ✅ Work rate (attacking/defensive)
- ✅ Player traits and specialties
- ✅ Hidden attributes (consistency, big match temperament, etc.)
- ✅ Detailed injury history
- ❌ Player media handling rating
- ✅ Player potential rating (for youth development)
- ❌ International caps and goals
- ✅ Career statistics (goals, assists, appearances by season)
- ✅ Player awards and achievements
- ❌ Preferred positions and versatility ratings

### Squad Operations
- ✅ Squad rosters (~25+ players per team)
- ✅ Starting lineups (11 players)
- ✅ Substitutes bench
- ✅ Automatic substitutions during matches
- ❌ Manual team selection (user control)
- ❌ Formation changes
- ❌ Custom tactics and instructions
- ❌ Individual player instructions
- ❌ Training schedules
- ❌ Training focus areas (attacking, defending, fitness)
- ❌ Player tutoring/mentoring
- ❌ Squad rotation policies
- ❌ Player roles assignment
- ❌ Captaincy and vice-captaincy
- ❌ Player rest management
- ❌ Player happiness with playing time
- ❌ Squad cohesion and dynamics

---

## 3. Transfer System & Contracts

### Transfers
- ❌ Transfer market/window
- ❌ Player scouting and search
- ❌ Transfer offers and negotiations
- ❌ Loan system (season-long, short-term)
- ❌ Buy-back clauses
- ❌ Sell-on clauses
- ❌ Release clauses
- ❌ Free transfers
- ❌ Contract expiry and Bosman rules
- ❌ Transfer budgets
- ❌ Transfer deadline day
- ❌ Agent fees
- 🚧 Player agents (entities exist but not active in transfers)
- 🚫 Real-world data import

### Contract Negotiations
- ✅ Contract years remaining tracked
- ✅ Player salaries tracked
- 🚧 Agent negotiations (events defined but not implemented)
- ❌ Contract renewal negotiations
- ❌ Contract demands (wages, bonuses, clauses)
- ❌ Signing bonuses
- ❌ Performance bonuses
- ❌ Appearance bonuses
- ❌ Contract rebel/disputes
- ❌ Player demands (playing time, ambition, etc.)

---

## 4. Staff & Management

### Manager/Staff
- ❌ Manager appointment
- ❌ Manager reputation and history
- ❌ Manager contracts
- ❌ Manager tactics and philosophy
- ❌ Press conferences
- ❌ Board expectations and objectives
- ❌ Manager pressure and job security
- 🚧 Staff members (entities exist: coaches, scouts, physios)
- ❌ Staff assignments and roles
- ❌ Staff attributes (coaching, judging ability, etc.)
- ❌ Staff development
- 🚫 Manager mode with tactical decisions (future enhancement)

### Scouting
- ❌ Scouting network
- ❌ Scout assignments
- ❌ Scouting reports
- ❌ Player recommendations
- ❌ Youth scouting
- ❌ Opposition scouting

---

## 5. Club Management

### Financial Management
- ✅ Club owners with wealth tracking
- ✅ Basic finances (contracts tracked, prize money, TV rights)
- ❌ Transfer budgets
- ❌ Wage budgets
- ✅ Ticket sales revenue (matchday revenue calculated)
- ❌ Merchandise revenue
- ✅ Prize money (based on league position)
- ✅ TV rights revenue (based on league position and stadium)
- ❌ Sponsorship deals
- ❌ Stadium naming rights
- ❌ Financial fair play rules
- ❌ Debt management
- ❌ Bank loans

### Infrastructure
- ✅ Stadium information (capacity, facilities tracked)
- ❌ Stadium expansion/renovation
- ✅ Training ground facilities (quality tracked)
- ❌ Youth academy facilities
- ❌ Medical facilities
- ❌ Facility upgrades and costs

### Board & Ownership
- ✅ Club owner entities
- ✅ Owner statements and reactions
- 🚧 Owner satisfaction (tracked but limited interaction)
- ❌ Board meetings
- ❌ Board expectations and deadlines
- ❌ Takeover bids
- ❌ Financial backing levels
- ❌ Board confidence voting

---

## 6. Player Development & Youth

### Youth System
- ❌ Youth academy
- ❌ Youth intake (new players joining)
- ❌ Youth player development
- ❌ Youth team matches
- ❌ Youth team coaching
- ❌ Promising youngsters identification
- 🚫 U21/U18 squads (out of scope)

### Player Growth
- 🚧 Basic player development
- ❌ Training affecting attributes
- ❌ Match experience improving players
- ❌ Age-related decline
- ❌ Player potential realization
- ❌ Breakthrough seasons
- ❌ Wonderkids

---

## 7. Media & Narrative

### Media System
- ✅ Media outlets entities
- ✅ Media stories published (events)
- 🚧 LLM-driven narratives (basic implementation)
- ❌ Press conferences (pre/post match)
- ❌ Media interviews
- ❌ Media reaction to results
- ❌ Transfer rumors
- ❌ Injury news
- ❌ Contract sagas
- ❌ Controversies and scandals
- ❌ Manager quotes
- ❌ Player quotes
- ❌ Social media simulation
- ❌ Fan forums/reactions

### Relationships & Dynamics
- ✅ Player morale (LLM-driven)
- ✅ Team morale
- 🚧 Relationships (framework exists)
- ❌ Player-player relationships
- ❌ Player-manager relationships
- ❌ Team chemistry
- ❌ Dressing room atmosphere
- ❌ Team leaders and troublemakers
- ❌ Player rivalries
- ❌ Team rivalries (entities exist but not dynamic)
- ❌ Local derbies

---

## 8. Tactical System

### Tactics & Formations
- ❌ Formation selection (4-4-2, 4-3-3, etc.)
- ❌ Tactical styles (possession, counter-attack, etc.)
- ❌ Team instructions (pressing, tempo, width)
- ❌ Individual player roles
- ❌ Set piece routines
- ❌ Opposition instructions
- ❌ Team shape (defensive, balanced, attacking)
- ❌ Tactical familiarity
- ❌ In-match tactical changes
- ❌ Player suitability for tactics

### Match Preparation
- ❌ Team talks
- ❌ Training focus before matches
- ❌ Opposition analysis
- ❌ Match preparation rating
- ❌ Team cohesion building

---

## 9. User Interface & Experience

### Current UI
- ✅ Basic React/Next.js UI
- ✅ "Advance" button to progress simulation
- ✅ League tables display
- ✅ Match events display
- ✅ World state visualization

### Missing UI Features
- ❌ Team selection screen
- ❌ Tactics screen
- ❌ Squad screen with player details
- ❌ Transfer market screen
- ❌ Contract negotiation screens
- ❌ Training schedule screen
- ❌ Match preparation screen
- ❌ Scouting center
- ❌ Staff management screen
- ❌ Financial overview
- ❌ Club information screen
- ❌ News/inbox system
- ❌ Calendar/schedule view
- ❌ Player comparison tools
- ❌ Statistics and records
- ❌ Save/load game functionality
- ❌ Multiple save slots
- ❌ Game speed controls
- ❌ Customizable dashboard
- 🚫 Advanced visualizations (more sophisticated UI planned)

---

## 10. Statistics & Records

### Player Statistics
- 🚧 Basic match performance tracking
- ❌ Season statistics (goals, assists, appearances)
- ❌ Career statistics
- ❌ Records (most goals in season, etc.)
- ✅ Player ratings per match
- ❌ Average ratings
- ❌ Form guide (last 5/10 games)
- ✅ Head-to-head statistics

### Team Statistics
- ✅ League position
- ✅ Points, wins, draws, losses
- ✅ Goals for/against
- ✅ Basic team stats
- ✅ Home/away records (tracked with separate home/away W/D/L)
- ✅ Winning/losing streaks
- ✅ Clean sheets
- ✅ Form guide (last 5 matches)
- ✅ Head-to-head records
- ✅ Historical records

### League Statistics
- ✅ League tables
- ✅ Top scorers (API endpoint added)
- ✅ Top assisters
- ✅ Most clean sheets
- ✅ Disciplinary records
- ✅ Best/worst defense
- ✅ Historical champions

---

## 11. Game Modes & Features

### Core Gameplay
- ✅ Simulation mode (advance matchday)
- ✅ Event-sourced world state
- ✅ Deterministic match simulation
- ✅ LLM-driven soft state
- ❌ Interactive manager mode
- ❌ Career mode with progression
- ❌ Challenge mode (specific scenarios)
- ❌ Sandbox mode
- ❌ Tutorial/onboarding
- ❌ Achievement system
- ❌ Multiple seasons support
- ❌ Historical season playback

### Data & Customization
- 🚧 Fantasy team names (placeholder system)
- ❌ Custom team import via CSV
- ❌ Custom league creation
- ❌ Editor mode
- ❌ Database editing
- ❌ Logo customization
- ❌ Kit customization
- 🚫 Real-world data import (future)

---

## 12. Advanced Features

### AI & Intelligence
- ✅ LLM-driven player psychology
- ✅ LLM-driven morale updates
- ✅ Basic AI narrative generation
- ❌ Advanced tactical AI
- ❌ Transfer AI (clubs buying/selling)
- ❌ Managerial AI (other managers)
- ❌ Player personality AI
- ❌ Agent AI behavior
- ❌ Dynamic world events

### Social & Community
- ❌ Achievements/trophies
- ❌ Leaderboards
- ❌ Challenge sharing
- ❌ Online leagues
- ❌ Multiplayer support
- ❌ Cloud saves

### Technical Features
- ✅ SQLite event store
- ✅ Event sourcing architecture
- ✅ REST API with FastAPI
- ✅ Live event streaming (SSE)
- ✅ Deterministic simulation with seeds
- ✅ LLM provider abstraction
- ✅ Offline/cached LLM mode
- ❌ Replay system
- ❌ Save state snapshots
- ❌ Undo/redo functionality
- ❌ Performance optimization for large datasets
- ❌ Parallel match simulation
- ❌ Database migration system

---

## 13. Known Issues & Improvements

### Match Engine
- ❌ More realistic goal probabilities
- ❌ Dynamic match momentum
- ❌ Home advantage implementation
- ❌ Player fatigue affecting performance
- ❌ Red card impact on team performance
- ❌ Substitution strategy intelligence
- ❌ Time-wasting tactics
- ❌ Injury-time events

### LLM Integration
- ✅ Basic LLM integration (LM Studio, mock)
- ❌ Advanced prompt engineering for narratives
- ❌ Context-aware story generation
- ❌ Multi-turn dialogue for press conferences
- ❌ LLM caching optimization
- ❌ Fallback strategies for LLM failures

### Performance
- ❌ Large-scale league simulation
- ❌ Historical data querying optimization
- ❌ Event store pruning/archiving
- ❌ Memory usage optimization

---

## Priority Roadmap (Suggested)

### Phase 1: Enhanced Match Experience
1. Match statistics (possession, shots, corners)
2. Set pieces (corners, free kicks, penalties)
3. Match commentary/ticker
4. Better match visualization in UI

### Phase 2: Manager Mode Foundation
1. Manager appointment and profile
2. Team selection interface
3. Basic tactical system (formations)
4. Squad management UI

### Phase 3: Transfer System
1. Transfer market infrastructure
2. Player scouting
3. Contract negotiations
4. Transfer windows

### Phase 4: Career Progression
1. Multiple seasons
2. Career statistics
3. Achievement system
4. Financial management

### Phase 5: Advanced Features
1. Cup competitions
2. Improved AI and narrative generation
3. Training and player development
4. Advanced tactics and analysis

---

## Notes

- This project intentionally excludes some features like real-world data, national teams, youth squads (U21/U18), and 2D/3D visualization in v1
- The focus is on combining deterministic simulation with LLM-driven narratives
- Many "soft" features (morale, relationships, narratives) are handled by LLM rather than traditional logic
- The architecture is designed for extensibility and gradual feature addition

---

**Last Updated:** 2024
**Project:** Back of the Neural Net
**Comparison Baseline:** Football Manager 2024
