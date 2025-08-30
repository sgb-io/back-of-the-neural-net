#!/usr/bin/env python3
"""Test the MCP server implementation."""

import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from neuralnet.orchestrator import GameOrchestrator
from neuralnet.data import create_sample_world


async def test_game_tools():
    """Test game state tools functionality."""
    print("Testing game state tools integration...\n")
    
    # Create orchestrator with tools enabled
    orchestrator = GameOrchestrator(use_tools=True)
    orchestrator.initialize_world()
    
    # Get some team IDs for testing
    team_ids = list(orchestrator.world.teams.keys())[:2]
    if len(team_ids) < 2:
        print("❌ Need at least 2 teams for testing")
        return
    
    team1_id, team2_id = team_ids[0], team_ids[1]
    team1 = orchestrator.world.get_team_by_id(team1_id)
    team2 = orchestrator.world.get_team_by_id(team2_id)
    
    print(f"Testing with teams: {team1.name} vs {team2.name}")
    print(f"Available tools: {orchestrator.get_available_game_tools()}\n")
    
    # Test 1: Match predictions
    print("🎯 Testing match predictions...")
    try:
        predictions = await orchestrator.query_game_tool("get_match_predictions", 
            home_team_id=team1_id, away_team_id=team2_id)
        if "error" in predictions:
            print(f"❌ Match predictions failed: {predictions['error']}")
        else:
            print(f"✓ Match predictions: {predictions['home_team']} vs {predictions['away_team']}")
            print(f"  Win probabilities: {predictions['win_probabilities']}")
            print(f"  Predicted score: {predictions['predicted_score']}")
    except Exception as e:
        print(f"❌ Match predictions failed: {e}")
    
    # Test 2: Head-to-head
    print("\n📊 Testing head-to-head...")
    try:
        h2h = await orchestrator.query_game_tool("get_head_to_head", 
            team1_id=team1_id, team2_id=team2_id, limit=3)
        if "error" in h2h:
            print(f"❌ Head-to-head failed: {h2h['error']}")
        else:
            print(f"✓ Head-to-head: {h2h['team1']} vs {h2h['team2']}")
            print(f"  Record: {h2h['head_to_head_record']}")
            print(f"  Recent matches: {len(h2h['recent_matches'])}")
    except Exception as e:
        print(f"❌ Head-to-head failed: {e}")
    
    # Test 3: Media views
    print("\n📺 Testing media views...")
    try:
        media = await orchestrator.query_game_tool("get_media_views", 
            entity_type="team", entity_id=team1_id)
        if "error" in media:
            print(f"❌ Media views failed: {media['error']}")
        else:
            print(f"✓ Media views for {media['entity']['name']}")
            print(f"  Overall sentiment: {media['overall_sentiment']}")
            print(f"  Coverage from {len(media['media_coverage'])} outlets")
    except Exception as e:
        print(f"❌ Media views failed: {e}")
    
    # Test 4: Random generation
    print("\n🎲 Testing random generation...")
    try:
        random_result = await orchestrator.query_game_tool("generate_random",
            type="int", min_val=1, max_val=100, seed=42)
        if "error" in random_result:
            print(f"❌ Random generation failed: {random_result['error']}")
        else:
            print(f"✓ Random generation: {random_result}")
    except Exception as e:
        print(f"❌ Random generation failed: {e}")
    
    # Test 5: Reputation info
    print("\n💎 Testing reputation info...")
    try:
        # Get a club owner for this team
        club_owners = [owner for owner in orchestrator.world.club_owners.values() 
                      if owner.team_id == team1_id]
        if club_owners:
            owner = club_owners[0]
            reputation = await orchestrator.query_game_tool("get_reputation_info",
                entity_type="club_owner", entity_id=owner.id,
                relation_type="team", relation_id=team1_id)
            if "error" in reputation:
                print(f"❌ Reputation info failed: {reputation['error']}")
            else:
                print(f"✓ Reputation info between {reputation['entity']['name']} and {reputation['relation']['name']}")
                print(f"  Factors: {reputation['reputation_factors']}")
        else:
            print("⚠️ No club owner found for reputation test")
    except Exception as e:
        print(f"❌ Reputation info failed: {e}")


async def test_tools_llm_integration():
    """Test that the tools-based LLM provider works."""
    print("\n🧠 Testing tools-based LLM integration...")
    
    orchestrator = GameOrchestrator(use_tools=True)
    orchestrator.initialize_world()
    
    # Test season progress analysis
    try:
        updates = await orchestrator.brain_orchestrator.process_season_progress(orchestrator.world)
        print(f"✓ LLM generated {len(updates)} updates using game state tools")
        
        if updates:
            print(f"  Sample update: {updates[0].entity_type} {updates[0].entity_id}")
            print(f"  Reasoning: {updates[0].reasoning}")
            print(f"  Changes: {updates[0].updates}")
    except Exception as e:
        print(f"❌ Tools LLM integration failed: {e}")


async def test_match_simulation_with_tools():
    """Test match simulation with tools-enabled LLM analysis."""
    print("\n⚽ Testing match simulation with tools LLM...")
    
    orchestrator = GameOrchestrator(use_tools=True)
    orchestrator.initialize_world()
    
    try:
        # Advance simulation one step
        result = await orchestrator.advance_simulation()
        
        print(f"✓ Simulation advanced successfully")
        print(f"  Matches simulated: {result.get('matches_simulated', 0)}")
        print(f"  LLM updates applied: {result.get('llm_updates_applied', 0)}")
        
        if result.get('llm_updates_applied', 0) > 0:
            print("  ✓ Tools-powered LLM analysis integrated successfully")
        
    except Exception as e:
        print(f"❌ Match simulation with tools failed: {e}")


async def main():
    """Run all game tools tests."""
    print("Testing Game State Tools implementation for Back of the Neural Net\n")
    print("=" * 60)
    
    await test_game_tools()
    await test_tools_llm_integration()
    await test_match_simulation_with_tools()
    
    print("\n" + "=" * 60)
    print("🎉 Game state tools testing completed!")


if __name__ == "__main__":
    asyncio.run(main())