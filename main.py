#!/usr/bin/env python3
"""Command-line interface for Back of the Neural Net."""

import asyncio
import os
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from neuralnet.orchestrator import GameOrchestrator
from neuralnet.server import app
import uvicorn


async def main() -> None:
    """Main CLI entry point."""
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        # Check for --reset flag in any position
        reset_requested = "--reset" in sys.argv
        if reset_requested:
            os.environ["RESET_DB"] = "true"
            print("🗑️  Database reset requested")
        
        if command == "simulate":
            print("Running headless simulation...")
            orchestrator = GameOrchestrator()
            orchestrator.initialize_world()
            for i in range(5):  # Simulate 5 matchdays
                print(f"\n--- Advancing to matchday {i+1} ---")
                result = await orchestrator.advance_simulation()
                print(f"Status: {result['status']}")
                print(f"Matches played: {result['matches_played']}")
                # Show league tables
                world_state = orchestrator.get_world_state()
                for league_id, league in world_state['leagues'].items():
                    print(f"\n{league['name']} - Top 5:")
                    for team in league['table'][:5]:
                        print(f"  {team['position']}. {team['team']} - {team['points']} pts")
        elif command == "test":
            print("Running basic test...")
            orchestrator = GameOrchestrator()
            orchestrator.initialize_world()
            print("World initialized successfully!")
            print(f"Leagues: {list(orchestrator.world.leagues.keys())}")
            print(f"Teams: {len(orchestrator.world.teams)}")
            print(f"Players: {len(orchestrator.world.players)}")
            # Test one simulation step
            result = await orchestrator.advance_simulation()
            print(f"Simulation step completed: {result['status']}")
        elif command == "server":
            # This is handled below in the main block, but we should recognize it here too
            pass
        else:
            print(f"Unknown command: {command}")
            print_usage()
    else:
        print_usage()


def print_usage() -> None:
    """Print usage information."""
    print("Back of the Neural Net CLI")
    print("\nUsage:")
    print("  python main.py server [--reset]    - Start the API server")
    print("  python main.py simulate [--reset]  - Run headless simulation")
    print("  python main.py test [--reset]      - Run basic test")
    print("\nFlags:")
    print("  --reset                            - Reset database for fresh start")


if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == "server":
        # Check for --reset flag for server command
        reset_requested = "--reset" in sys.argv
        if reset_requested:
            os.environ["RESET_DB"] = "true"
            print("🗑️  Database reset requested for server startup")
        
        print("Starting Back of the Neural Net server...")
        print("API will be available at http://127.0.0.1:8000")
        print("React UI should be started separately with: cd ui && npm start")
        uvicorn.run(app, host="127.0.0.1", port=8000)
    else:
        asyncio.run(main())