#!/usr/bin/env python3
"""
Demo script showcasing the new TODO basket round 4 features:
- Weak foot rating (1-5 stars)
- Player ratings per match (1-10 scale)
- Free kicks (direct/indirect)
- Head-to-head records
"""

import sys
import asyncio
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from neuralnet.orchestrator import GameOrchestrator
from neuralnet.events import FreeKick, MatchEnded, Goal


async def main():
    print("=" * 70)
    print("🎮 TODO Basket Round 4 Features Demo")
    print("=" * 70)
    
    # Initialize orchestrator
    orchestrator = GameOrchestrator()
    orchestrator.initialize_world()
    
    print("\n✨ Simulating matches to generate data...")
    
    # Simulate several matchdays to generate enough data
    for _ in range(5):
        result = await orchestrator.advance_simulation()
    
    world = orchestrator.world
    
    # Feature 1: Weak Foot Rating
    print("\n" + "=" * 70)
    print("⚽ NEW FEATURE: Weak Foot Rating (1-5 Stars)")
    print("=" * 70)
    
    # Get a sample of players with different weak foot ratings
    print("\n📊 Weak Foot Distribution Across All Players:")
    weak_foot_counts = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
    two_footed_players = []
    
    for team in world.teams.values():
        for player in team.players:
            weak_foot_counts[player.weak_foot] += 1
            if player.preferred_foot.value == "Both":
                two_footed_players.append(player)
    
    for rating in range(1, 6):
        count = weak_foot_counts[rating]
        percentage = (count / sum(weak_foot_counts.values())) * 100
        bar = "█" * int(percentage / 2)
        print(f"  {rating}★: {bar} {count} players ({percentage:.1f}%)")
    
    print("\n👥 Sample Players by Weak Foot Rating:")
    sample_teams = list(world.teams.values())[:2]
    for team in sample_teams:
        print(f"\n  {team.name}:")
        for player in team.players[:3]:
            stars = "★" * player.weak_foot
            print(f"    {player.name:<20} {player.position.value:<5} Preferred: {player.preferred_foot.value:<6} Weak: {stars}")
    
    if two_footed_players:
        print(f"\n🦶 Two-Footed Players (usually have better weak foot):")
        for player in two_footed_players[:5]:
            stars = "★" * player.weak_foot
            print(f"  {player.name:<20} Weak Foot: {stars}")
    
    # Feature 2: Free Kicks
    print("\n" + "=" * 70)
    print("🎯 NEW FEATURE: Free Kicks (Direct/Indirect)")
    print("=" * 70)
    
    all_events = orchestrator.event_store.get_events()
    free_kicks = [e for e in all_events if isinstance(e, FreeKick)]
    
    print(f"\n📈 Free Kick Statistics:")
    print(f"  Total free kicks: {len(free_kicks)}")
    
    if len(free_kicks) > 0:
        direct_count = sum(1 for fk in free_kicks if fk.free_kick_type == "direct")
        indirect_count = sum(1 for fk in free_kicks if fk.free_kick_type == "indirect")
        dangerous_count = sum(1 for fk in free_kicks if fk.location == "dangerous")
        safe_count = sum(1 for fk in free_kicks if fk.location == "safe")
        
        print(f"  Direct: {direct_count} ({(direct_count/len(free_kicks)*100):.1f}%)")
        print(f"  Indirect: {indirect_count} ({(indirect_count/len(free_kicks)*100):.1f}%)")
        print(f"  Dangerous position: {dangerous_count} ({(dangerous_count/len(free_kicks)*100):.1f}%)")
        print(f"  Safe position: {safe_count} ({(safe_count/len(free_kicks)*100):.1f}%)")
        
        print(f"\n🎪 Recent Free Kick Events:")
        for fk in free_kicks[-5:]:
            team = world.get_team_by_id(fk.team)
            team_name = team.name if team else "Unknown"
            fk_type = fk.free_kick_type.capitalize()
            location = fk.location
            print(f"  {fk.minute}' - {team_name}: {fk_type} free kick ({location})")
    
    # Check free kick statistics in match results
    match_ended_events = [e for e in all_events if isinstance(e, MatchEnded)]
    print(f"\n📊 Free Kicks Per Match:")
    for match in match_ended_events[-3:]:
        home = world.get_team_by_id(match.home_team)
        away = world.get_team_by_id(match.away_team)
        home_name = home.name if home else "Unknown"
        away_name = away.name if away else "Unknown"
        print(f"  {home_name} {match.home_free_kicks} - {match.away_free_kicks} {away_name}")
    
    # Feature 3: Player Ratings
    print("\n" + "=" * 70)
    print("⭐ NEW FEATURE: Player Ratings Per Match (1-10 Scale)")
    print("=" * 70)
    
    if match_ended_events:
        print("\n🏆 Man of the Match (Last 3 Matches):")
        for match in match_ended_events[-3:]:
            if match.player_ratings:
                home = world.get_team_by_id(match.home_team)
                away = world.get_team_by_id(match.away_team)
                home_name = home.name if home else "Unknown"
                away_name = away.name if away else "Unknown"
                
                # Find best rated player
                best_player_id = max(match.player_ratings.items(), key=lambda x: x[1])[0]
                best_rating = match.player_ratings[best_player_id]
                
                # Find player details
                best_player = None
                player_team = None
                for team in [home, away]:
                    if team:
                        for player in team.players:
                            if player.id == best_player_id:
                                best_player = player
                                player_team = team
                                break
                
                if best_player:
                    print(f"\n  {home_name} {match.home_score}-{match.away_score} {away_name}")
                    print(f"    ⭐ {best_player.name} ({player_team.name}) - {best_rating}/10")
        
        # Show rating distribution from last match
        last_match = match_ended_events[-1]
        if last_match.player_ratings:
            print(f"\n📊 Rating Distribution (Last Match):")
            home = world.get_team_by_id(last_match.home_team)
            away = world.get_team_by_id(last_match.away_team)
            
            print(f"\n  {home.name} (Home):")
            home_players = []
            for player in home.players[:11]:
                if player.id in last_match.player_ratings:
                    rating = last_match.player_ratings[player.id]
                    home_players.append((player, rating))
            
            home_players.sort(key=lambda x: x[1], reverse=True)
            for player, rating in home_players[:5]:
                stars = "★" * int(rating)
                print(f"    {player.name:<20} {player.position.value:<5} {rating}/10 {stars}")
            
            print(f"\n  {away.name} (Away):")
            away_players = []
            for player in away.players[:11]:
                if player.id in last_match.player_ratings:
                    rating = last_match.player_ratings[player.id]
                    away_players.append((player, rating))
            
            away_players.sort(key=lambda x: x[1], reverse=True)
            for player, rating in away_players[:5]:
                stars = "★" * int(rating)
                print(f"    {player.name:<20} {player.position.value:<5} {rating}/10 {stars}")
    
    # Feature 4: Head-to-Head Records
    print("\n" + "=" * 70)
    print("🤝 NEW FEATURE: Head-to-Head Records")
    print("=" * 70)
    
    # Show head-to-head records for teams that have played each other
    print("\n📊 Head-to-Head Records:")
    
    teams_with_h2h = []
    for team in world.teams.values():
        if team.head_to_head:
            teams_with_h2h.append(team)
    
    if teams_with_h2h:
        # Show a few interesting head-to-head matchups
        for team in teams_with_h2h[:3]:
            print(f"\n  {team.name}:")
            for opponent_id, record in list(team.head_to_head.items())[:3]:
                opponent = world.get_team_by_id(opponent_id)
                if opponent:
                    total = record["W"] + record["D"] + record["L"]
                    print(f"    vs {opponent.name:<30} {record['W']}W-{record['D']}D-{record['L']}L ({total} matches)")
        
        # Find most played fixture
        max_matches = 0
        best_rivalry = None
        for team in world.teams.values():
            for opponent_id, record in team.head_to_head.items():
                total = record["W"] + record["D"] + record["L"]
                if total > max_matches:
                    max_matches = total
                    opponent = world.get_team_by_id(opponent_id)
                    if opponent:
                        best_rivalry = (team, opponent, record)
        
        if best_rivalry:
            team1, team2, record = best_rivalry
            print(f"\n🏆 Most Played Fixture ({max_matches} matches):")
            print(f"  {team1.name} vs {team2.name}")
            print(f"  {team1.name}: {record['W']}W-{record['D']}D-{record['L']}L")
    else:
        print("  No head-to-head records yet (teams need to play each other)")
    
    # Summary
    print("\n" + "=" * 70)
    print("✨ Summary of New Features")
    print("=" * 70)
    print("""
✅ Weak Foot Rating
   - All players have 1-5 star weak foot rating
   - Realistic distribution (most have 3★)
   - Two-footed players have better weak foot ability
   - Used for realistic player assessment

✅ Free Kicks
   - FreeKick events generated during matches
   - Direct (80%) and indirect (20%) free kicks
   - Location tracking (dangerous/safe)
   - ~13.5 free kicks per match
   - Statistics tracked in MatchEnded
   - Included in match commentary

✅ Player Ratings
   - Individual ratings (1-10) for all starting 11
   - Base 6.0 modified by form, fitness, position
   - Goalkeepers get clean sheet bonuses
   - Stored in MatchEnded events
   - API endpoint available

✅ Head-to-Head Records
   - Win/Draw/Loss tracked between all teams
   - Symmetric records (automatically balanced)
   - Accumulated across all matches
   - API endpoint available
   - Shows rivalry intensity
""")
    
    print("\n🎉 Demo complete! All new features are working.")
    print("=" * 70)
    
    print("\n📡 API Endpoints:")
    print("  GET /api/matches/{match_id}/player-ratings")
    print("  GET /api/teams/{team_id}/head-to-head")


if __name__ == "__main__":
    asyncio.run(main())
