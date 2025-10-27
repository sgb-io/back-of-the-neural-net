"""Demo script to showcase the basic game architecture."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

async def run_demo():
    """Run a demonstration of the game features."""
    print("🎮 Back of the Neural Net - Demo")
    print("================================")
    
    try:
        from neuralnet.orchestrator import GameOrchestrator
        from neuralnet.events import EventStore
        
        print("\n1. Initializing game world...")
        orchestrator = GameOrchestrator(EventStore(":memory:"))
        orchestrator.initialize_world()
        
        print(f"✓ Created world with {len(orchestrator.world.leagues)} leagues")
        print(f"✓ Generated {len(orchestrator.world.teams)} teams")
        print(f"✓ Created {len(orchestrator.world.players)} players")
        print(f"✓ Scheduled {len(orchestrator.world.matches)} matches")
        
        # Show leagues
        print("\n2. League Information:")
        for league_id, league in orchestrator.world.leagues.items():
            print(f"   {league.name}: {len(league.teams)} teams")
            print(f"   Current matchday: {league.current_matchday}")
        
        # Show some team names
        print("\n3. Sample Teams:")
        team_names = list(orchestrator.world.teams.values())[:6]
        for i, team in enumerate(team_names):
            print(f"   {team.name} ({team.league})")
        
        # Show some player names
        print("\n4. Sample Players:")
        player_names = list(orchestrator.world.players.values())[:8]
        for player in player_names:
            print(f"   {player.name} ({player.position}) - {player.age} years")
        
        # Simulate first matchday
        print("\n5. Simulating first matchday...")
        fixtures = orchestrator.get_current_matchday_fixtures()
        print(f"   Found {len(fixtures)} fixtures for matchday 1")
        
        result = await orchestrator.advance_simulation()
        print(f"   Status: {result['status']}")
        print(f"   Matches played: {result['matches_played']}")
        
        # Show some match events
        if result.get('events'):
            print("\n6. Sample Match Events:")
            for event in result['events'][:10]:  # Show first 10 events
                if event.get('event_type') == 'Goal':
                    print(f"   ⚽ {event['minute']}' GOAL! {event['scorer']} ({event['team']})")
                elif event.get('event_type') == 'YellowCard':
                    print(f"   🟨 {event['minute']}' Yellow card: {event['player']}")
                elif event.get('event_type') == 'MatchEnded':
                    print(f"   🏁 Full time: {event['home_team']} {event['home_score']}-{event['away_score']} {event['away_team']}")
        
        # Show league table
        print("\n7. Premier Fantasy League Table (Top 5):")
        world_state = orchestrator.get_world_state()
        premier_table = world_state['leagues']['premier_fantasy']['table'][:5]
        print("   Pos  Team                  P  W  D  L  GF GA  Pts")
        print("   " + "-" * 50)
        for team in premier_table:
            print(f"   {team['position']:2d}   {team['team']:<18} {team['played']:2d} {team['won']:2d} {team['drawn']:2d} {team['lost']:2d} {team['goals_for']:2d} {team['goals_against']:2d}  {team['points']:3d}")
        
        print("\n🎉 Demo completed successfully!")
        print("\nTo start the full application:")
        print("1. Install dependencies: pip install pydantic fastapi uvicorn sse-starlette")
        print("2. Start API server: python main.py server")
        print("3. Install UI deps: cd ui && npm install")
        print("4. Start React UI: cd ui && npm start")
        print("5. Open browser: http://localhost:3000")
        
    except ImportError as e:
        print(f"❌ Missing dependencies: {e}")
        print("Run: pip install pydantic fastapi uvicorn sse-starlette")
        print("Then try the demo again!")
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(run_demo())