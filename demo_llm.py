#!/usr/bin/env python3
"""Demonstration script showing LLM provider configuration."""

import os
import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from neuralnet.config import get_config, validate_llm_config
from neuralnet.orchestrator import GameOrchestrator


async def demonstrate_llm_providers():
    """Demonstrate different LLM provider configurations."""
    
    print("🎯 Back of the Neural Net - LLM Provider Demo")
    print("=" * 50)
    
    # Show current configuration
    config = get_config()
    print(f"\n📋 Current Configuration:")
    print(f"   LLM Provider: {config.llm.provider}")
    print(f"   Use Tools: {config.use_tools}")
    
    if config.llm.provider == "lmstudio":
        print(f"   LM Studio Model: {config.llm.lmstudio_model}")
        print(f"   LM Studio URL: {config.llm.lmstudio_base_url}")
        print(f"   Temperature: {config.llm.temperature}")
    
    print(f"\n🚀 Initializing game world...")
    
    try:
        # Validate configuration
        validate_llm_config(config)
        
        # Create orchestrator with current config
        orchestrator = GameOrchestrator(config=config)
        orchestrator.initialize_world()
        
        print(f"✓ World initialized successfully!")
        print(f"   Teams: {len(orchestrator.world.teams)}")
        print(f"   Players: {len(orchestrator.world.players)}")
        print(f"   Leagues: {list(orchestrator.world.leagues.keys())}")
        
        # Run one simulation step
        print(f"\n⚽ Running match simulation...")
        result = await orchestrator.advance_simulation()
        
        print(f"✓ Simulation completed!")
        print(f"   Status: {result['status']}")
        print(f"   Matches played: {result.get('matches_played', 0)}")
        print(f"   LLM updates: {result.get('llm_updates_applied', 0)}")
        
        # Show league standings
        print(f"\n🏆 Current League Standings:")
        world_state = orchestrator.get_world_state()
        
        for league_id, league in world_state['leagues'].items():
            print(f"\n   {league['name']}:")
            for i, team in enumerate(league['table'][:3]):  # Top 3
                print(f"     {i+1}. {team['team']} - {team['points']} pts")
        
        print(f"\n✨ Demo completed successfully!")
        
        if config.llm.provider == "mock":
            print(f"\n💡 To use LM Studio:")
            print(f"   1. Install LM Studio from https://lmstudio.ai/")
            print(f"   2. Load a model and start the server")
            print(f"   3. Set environment variables:")
            print(f"      export LLM_PROVIDER=lmstudio")
            print(f"      export LMSTUDIO_MODEL=your-model-name")
            print(f"   4. Run this demo again!")
        
    except Exception as e:
        print(f"❌ Demo failed: {e}")
        
        if "LM Studio model must be specified" in str(e):
            print(f"\n💡 LM Studio Setup Required:")
            print(f"   Set LMSTUDIO_MODEL environment variable")
            print(f"   Example: export LMSTUDIO_MODEL=llama-2-7b-chat")
        
        return 1
    
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(demonstrate_llm_providers()))