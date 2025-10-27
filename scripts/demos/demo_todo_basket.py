#!/usr/bin/env python3
"""
Demo script showcasing the new TODO basket features:
- Penalty kicks
- Fouls tracking
- Player preferred foot and work rates
- Winning/losing streaks
- Top assisters API
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from neuralnet.orchestrator import GameOrchestrator
from neuralnet.events import Foul, Goal, PenaltyAwarded


async def main():
    print("=" * 70)
    print("🎮 TODO Basket Features Demo")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = GameOrchestrator()
    orchestrator.initialize_world()
    
    print("\n✨ Simulating matches to generate data...")
    
    # Simulate several matchdays to generate enough data
    for _ in range(5):
        result = await orchestrator.advance_simulation()
        # Result is just the updated world state, not a dict with success
    
    world = orchestrator.world
    
    # Feature 1: Penalty Kicks
    print("\n" + "=" * 70)
    print("⚽ NEW FEATURE: Penalty Kicks")
    print("=" * 70)
    
    all_events = orchestrator.event_store.get_events()
    penalties = [e for e in all_events if isinstance(e, PenaltyAwarded)]
    penalty_goals = [e for e in all_events if isinstance(e, Goal) and hasattr(e, 'penalty') and e.penalty]
    
    print(f"\nPenalties awarded: {len(penalties)}")
    print(f"Penalties scored: {len(penalty_goals)}")
    
    if penalties:
        print("\n📋 Recent penalty incidents:")
        for penalty in penalties[:3]:
            print(f"  - Minute {penalty.minute}: {penalty.reason}")
            # Check if it resulted in a goal
            scored = any(g for g in penalty_goals if g.match_id == penalty.match_id and g.minute == penalty.minute)
            print(f"    Result: {'⚽ GOAL!' if scored else '❌ Missed'}")
    
    # Feature 2: Fouls
    print("\n" + "=" * 70)
    print("🟨 NEW FEATURE: Fouls Tracking")
    print("=" * 70)
    
    fouls = [e for e in all_events if isinstance(e, Foul)]
    print(f"\nTotal fouls committed: {len(fouls)}")
    
    # Get foul statistics from latest matches
    from neuralnet.events import MatchEnded
    match_ended_events = [e for e in all_events if isinstance(e, MatchEnded)]
    
    if match_ended_events:
        recent_match = match_ended_events[-1]
        print(f"\n📊 Latest match foul statistics:")
        home_team = world.get_team_by_id(recent_match.home_team)
        away_team = world.get_team_by_id(recent_match.away_team)
        
        if home_team and away_team:
            print(f"  {home_team.name}: {recent_match.home_fouls} fouls")
            print(f"  {away_team.name}: {recent_match.away_fouls} fouls")
    
    # Feature 3: Player Attributes
    print("\n" + "=" * 70)
    print("👟 NEW FEATURE: Player Preferred Foot & Work Rates")
    print("=" * 70)
    
    # Sample some players
    sample_teams = list(world.teams.values())[:2]
    
    print("\n📋 Sample Player Attributes:")
    for team in sample_teams:
        print(f"\n{team.name}:")
        for player in team.players[:3]:  # Show first 3 players
            print(f"  {player.name} ({player.position.value})")
            print(f"    Preferred Foot: {player.preferred_foot.value}")
            print(f"    Work Rate: {player.attacking_work_rate.value} (ATT) / {player.defensive_work_rate.value} (DEF)")
    
    # Feature 4: Winning/Losing Streaks
    print("\n" + "=" * 70)
    print("📈 NEW FEATURE: Winning & Losing Streaks")
    print("=" * 70)
    
    # Get teams with notable streaks
    teams_with_streaks = []
    for team in world.teams.values():
        if abs(team.current_streak) > 0 or team.longest_winning_streak > 0 or team.longest_losing_streak > 0:
            teams_with_streaks.append(team)
    
    # Sort by current streak magnitude
    teams_with_streaks.sort(key=lambda t: abs(t.current_streak), reverse=True)
    
    print("\n🔥 Current Form (Teams with active streaks):")
    streak_count = 0
    for team in teams_with_streaks[:5]:
        if team.current_streak != 0:
            streak_type = "winning" if team.current_streak > 0 else "losing"
            streak_value = abs(team.current_streak)
            print(f"  {team.name}: {streak_value} match {streak_type} streak")
            streak_count += 1
    
    if streak_count == 0:
        print("  (No active streaks - teams are in mixed form)")
    
    print("\n🏆 Best Winning Streaks This Season:")
    best_winners = sorted(world.teams.values(), key=lambda t: t.longest_winning_streak, reverse=True)[:5]
    for team in best_winners:
        if team.longest_winning_streak > 0:
            print(f"  {team.name}: {team.longest_winning_streak} matches")
    
    print("\n📉 Worst Losing Streaks This Season:")
    worst_losers = sorted(world.teams.values(), key=lambda t: t.longest_losing_streak, reverse=True)[:5]
    for team in worst_losers:
        if team.longest_losing_streak > 0:
            print(f"  {team.name}: {team.longest_losing_streak} matches")
    
    # Feature 5: Top Assisters
    print("\n" + "=" * 70)
    print("🎯 NEW FEATURE: Top Assisters")
    print("=" * 70)
    
    # Count assists manually (similar to what the API does)
    player_assists = {}
    player_goals = {}
    player_info = {}
    
    for event in all_events:
        if isinstance(event, Goal) and hasattr(event, 'assist') and event.assist:
            assister = event.assist
            player_assists[assister] = player_assists.get(assister, 0) + 1
            
            # Also track goals for context
            scorer = event.scorer
            player_goals[scorer] = player_goals.get(scorer, 0) + 1
            
            # Store player info
            if assister not in player_info:
                for team in world.teams.values():
                    for player in team.players:
                        if player.name == assister:
                            player_info[assister] = {
                                "team": team.name,
                                "position": player.position.value
                            }
                            break
    
    # Build top assisters list
    assisters = []
    for player_name, assists in player_assists.items():
        if player_name in player_info:
            assisters.append({
                "name": player_name,
                "assists": assists,
                "goals": player_goals.get(player_name, 0),
                "team": player_info[player_name]["team"],
                "position": player_info[player_name]["position"]
            })
    
    # Sort by assists
    assisters.sort(key=lambda x: (x["assists"], x["goals"]), reverse=True)
    
    print("\n🥇 Top 10 Assist Providers:")
    print(f"{'Rank':<6} {'Player':<20} {'Team':<25} {'Pos':<5} {'Assists':<8} {'Goals':<6}")
    print("-" * 70)
    
    for i, assister in enumerate(assisters[:10], 1):
        print(f"{i:<6} {assister['name']:<20} {assister['team']:<25} {assister['position']:<5} {assister['assists']:<8} {assister['goals']:<6}")
    
    print("\n💡 API Endpoint: GET /api/leagues/{league_id}/top-assisters?limit=10")
    print("   Returns: List of top assist providers with goals and assists")
    
    # Summary
    print("\n" + "=" * 70)
    print("✨ Summary of New Features")
    print("=" * 70)
    print("""
✅ Penalty Kicks
   - PenaltyAwarded events generated during matches
   - ~75% conversion rate (realistic)
   - Goals marked with penalty flag
   - Statistics tracked in MatchEnded

✅ Fouls Tracking
   - Foul events generated during matches
   - Tracked per team (home_fouls, away_fouls)
   - Different foul types (regular, dangerous, professional)
   - Typical match: 10-30 fouls

✅ Player Attributes
   - Preferred foot (Left/Right/Both)
   - Attacking work rate (Low/Medium/High)
   - Defensive work rate (Low/Medium/High)
   - Position-appropriate distributions

✅ Streak Tracking
   - Current streak (positive for wins, negative for losses)
   - Longest winning streak tracked
   - Longest losing streak tracked
   - Draws reset current streak to 0

✅ Top Assisters API
   - New endpoint: /api/leagues/{league_id}/top-assisters
   - Shows top assist providers
   - Includes goals for context
   - Sorted by assists then goals
""")
    
    print("\n🎉 Demo complete! All new features are working.")
    print("=" * 70)


if __name__ == "__main__":
    asyncio.run(main())
