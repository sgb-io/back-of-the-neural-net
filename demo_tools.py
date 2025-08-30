#!/usr/bin/env python3
"""Demonstrate the game state tools integration with LLM analysis."""

import sys
import asyncio
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from neuralnet.orchestrator import GameOrchestrator


async def demonstrate_tools_integration():
    """Demonstrate the full integration of game state tools with LLM analysis."""
    print("🏈 Back of the Neural Net - Game State Tools Integration Demo\n")
    print("=" * 60)
    
    # Create orchestrator with tools enabled
    orchestrator = GameOrchestrator(use_tools=True)
    orchestrator.initialize_world()
    
    # Show world state
    world_state = orchestrator.get_world_state()
    print(f"🌍 World initialized:")
    print(f"   Season: {world_state['season']}")
    print(f"   Leagues: {len(world_state['leagues'])}")
    print(f"   Teams: {sum(len(league['table']) for league in world_state['leagues'].values())}")
    print(f"   Entities: {world_state['entities_summary']}")
    
    # Get some teams for demonstration
    teams = []
    for league_data in world_state['leagues'].values():
        teams.extend([(team['team'], team['position']) for team in league_data['table'][:2]])
    
    team1_name, team1_pos = teams[0]
    team2_name, team2_pos = teams[1]
    
    print(f"\n🔍 Demonstrating tools with: {team1_name} (#{team1_pos}) vs {team2_name} (#{team2_pos})")
    
    # Find team IDs
    team1_id = None
    team2_id = None
    for team_id, team in orchestrator.world.teams.items():
        if team.name == team1_name:
            team1_id = team_id
        elif team.name == team2_name:
            team2_id = team_id
    
    print(f"\n📊 Available Game State Tools: {orchestrator.get_available_game_tools()}")
    
    # Demonstrate each tool
    print(f"\n🎯 1. Match Predictions")
    predictions = await orchestrator.query_game_tool("get_match_predictions", 
                                                   home_team_id=team1_id, away_team_id=team2_id)
    if "error" not in predictions:
        print(f"   {predictions['home_team']} vs {predictions['away_team']}")
        probs = predictions['win_probabilities']
        print(f"   Win Probabilities: Home {probs['home_win']}% | Draw {probs['draw']}% | Away {probs['away_win']}%")
        score = predictions['predicted_score']
        print(f"   Predicted Score: {score['home_goals']} - {score['away_goals']}")
    
    print(f"\n📺 2. Media Views")
    media_views = await orchestrator.query_game_tool("get_media_views", 
                                                    entity_type="team", entity_id=team1_id)
    if "error" not in media_views:
        print(f"   Media coverage for {media_views['entity']['name']}:")
        print(f"   Overall Sentiment: {media_views['overall_sentiment']}")
        print(f"   Coverage from {len(media_views['media_coverage'])} outlets")
        # Show sample coverage
        for outlet in media_views['media_coverage'][:2]:
            print(f"     - {outlet['outlet_name']}: {outlet['current_narrative']}")
    
    print(f"\n📊 3. Head-to-Head History")
    h2h = await orchestrator.query_game_tool("get_head_to_head", 
                                            team1_id=team1_id, team2_id=team2_id, limit=5)
    if "error" not in h2h:
        record = h2h['head_to_head_record']
        print(f"   {h2h['team1']} vs {h2h['team2']}")
        print(f"   Historical Record: {record[f'{team1_name}_wins']} - {record['draws']} - {record[f'{team2_name}_wins']}")
        print(f"   Total matches: {record['total_matches']}")
    
    print(f"\n🎲 4. Random Generation")
    random_result = await orchestrator.query_game_tool("generate_random", 
                                                      type="choice", 
                                                      choices=["Excellent", "Good", "Average", "Poor"])
    if "error" not in random_result:
        print(f"   Random match quality prediction: {random_result['value']}")
    
    print(f"\n💎 5. Reputation Analysis")
    # Get a club owner for reputation demo
    club_owners = [owner for owner in orchestrator.world.club_owners.values() 
                   if owner.team_id == team1_id]
    if club_owners:
        owner = club_owners[0]
        reputation = await orchestrator.query_game_tool("get_reputation_info",
                                                       entity_type="club_owner", entity_id=owner.id,
                                                       relation_type="team", relation_id=team1_id)
        if "error" not in reputation:
            print(f"   Reputation analysis: {reputation['entity']['name']} <-> {reputation['relation']['name']}")
            factors = reputation['reputation_factors']
            if 'satisfaction' in factors:
                print(f"   Owner satisfaction: {factors['satisfaction']}/100")
            if 'ambition' in factors:
                print(f"   Owner ambition: {factors['ambition']}/100")
    
    print(f"\n🧠 LLM Analysis Using Tools")
    print("   Running season progress analysis with tools-based LLM...")
    
    # Run LLM analysis that uses the tools
    updates = await orchestrator.brain_orchestrator.process_season_progress(orchestrator.world)
    
    print(f"   ✓ LLM generated {len(updates)} soft state updates using game tools")
    if updates:
        for i, update in enumerate(updates[:3]):  # Show first 3 updates
            print(f"   {i+1}. {update.entity_type} '{update.entity_id}':")
            print(f"      Changes: {update.updates}")
            print(f"      Reasoning: {update.reasoning}")
    
    print(f"\n⚽ Running Match Simulation with Tools-Enhanced LLM")
    
    # Advance simulation to trigger match events and LLM analysis
    result = await orchestrator.advance_simulation()
    
    print(f"   ✓ Simulation step completed:")
    print(f"     Matches simulated: {result.get('matches_simulated', 0)}")
    print(f"     LLM updates applied: {result.get('llm_updates_applied', 0)}")
    
    if result.get('match_results'):
        print(f"   📈 Match Results:")
        for match_result in result['match_results'][:2]:  # Show first 2 matches
            print(f"     {match_result['home_team']} {match_result['home_score']} - {match_result['away_score']} {match_result['away_team']}")
    
    print(f"\n" + "=" * 60)
    print("🎉 Game State Tools Integration Demo Complete!")
    print(f"\nThe LLM system now queries specific game state information using tools")
    print(f"instead of receiving the entire GameWorld object. This enables:")
    print(f"  • More targeted and efficient analysis")
    print(f"  • Better reasoning with relevant context")
    print(f"  • Reduced data transfer and processing overhead")
    print(f"  • More realistic soft state updates based on specific insights")


if __name__ == "__main__":
    asyncio.run(demonstrate_tools_integration())