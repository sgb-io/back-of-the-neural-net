"""Demo script for TODO basket round 7 features.

This script demonstrates the new features implemented in round 7:
1. Pitch conditions (6 types affecting matches)
2. Team captains and vice-captains
3. Average player ratings tracking
4. Season records infrastructure
5. Form guide tracking (W/D/L)
"""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from neuralnet.data import create_sample_world
from neuralnet.orchestrator import GameOrchestrator
from neuralnet.events import EventStore
from neuralnet.entities import PitchCondition


async def main():
    """Demonstrate the new features from TODO basket round 7."""
    print("=" * 80)
    print("TODO BASKET ROUND 7 - FEATURE DEMONSTRATION")
    print("=" * 80)
    print()
    
    # Initialize the world
    event_store = EventStore(":memory:")
    orchestrator = GameOrchestrator(event_store=event_store)
    orchestrator.initialize_world()
    world = orchestrator.world
    
    # =========================================================================
    # Feature 1: Pitch Conditions
    # =========================================================================
    print("📊 FEATURE 1: PITCH CONDITIONS")
    print("-" * 80)
    print("Matches now track pitch conditions that can affect gameplay:")
    print()
    
    # Show pitch condition types
    print("Available pitch conditions:")
    for condition in PitchCondition:
        print(f"  • {condition.value}")
    print()
    
    # Show some matches with their pitch conditions
    print("Sample matches with pitch conditions:")
    sample_matches = list(world.matches.values())[:5]
    for match in sample_matches:
        home_team = world.get_team_by_id(match.home_team_id)
        away_team = world.get_team_by_id(match.away_team_id)
        print(f"  {home_team.name} vs {away_team.name}")
        print(f"    → Weather: {match.weather.value}, Pitch: {match.pitch_condition.value}")
    print()
    
    # =========================================================================
    # Feature 2: Team Captains
    # =========================================================================
    print("👨‍✈️ FEATURE 2: TEAM CAPTAINS & VICE-CAPTAINS")
    print("-" * 80)
    print("Each team now has designated captain and vice-captain:")
    print()
    
    # Show captains for each team
    for team in list(world.teams.values())[:4]:
        print(f"{team.name}:")
        
        if team.captain_id:
            captain = world.get_player_by_id(team.captain_id)
            print(f"  Captain: {captain.name}")
            print(f"    → Position: {captain.position.value}, Age: {captain.age}, Rating: {captain.overall_rating}")
        
        if team.vice_captain_id:
            vice_captain = world.get_player_by_id(team.vice_captain_id)
            print(f"  Vice-Captain: {vice_captain.name}")
            print(f"    → Position: {vice_captain.position.value}, Age: {vice_captain.age}, Rating: {vice_captain.overall_rating}")
        
        print()
    
    # =========================================================================
    # Feature 3: Average Player Ratings
    # =========================================================================
    print("⭐ FEATURE 3: AVERAGE PLAYER RATINGS")
    print("-" * 80)
    print("Players now track match ratings and calculate averages:")
    print()
    
    # Play some matches to generate ratings
    print("Simulating matchday 1 to generate player ratings...")
    await orchestrator.advance_simulation()
    print("✓ Matchday 1 complete\n")
    
    # Show players with ratings
    players_with_ratings = [
        p for p in world.players.values()
        if len(p.match_ratings) > 0
    ]
    
    # Sort by average rating and show top 5
    players_with_ratings.sort(key=lambda p: p.average_rating, reverse=True)
    
    print(f"Top 5 players by average rating (from {len(players_with_ratings)} who played):")
    for i, player in enumerate(players_with_ratings[:5], 1):
        team = next((t for t in world.teams.values() if player in t.players), None)
        print(f"  {i}. {player.name} ({team.name if team else 'N/A'})")
        print(f"     → Average: {player.average_rating:.2f}, Ratings: {player.match_ratings}")
    print()
    
    # =========================================================================
    # Feature 4: Season Records Infrastructure
    # =========================================================================
    print("🏆 FEATURE 4: SEASON RECORDS INFRASTRUCTURE")
    print("-" * 80)
    print("Leagues now have infrastructure to track season records:")
    print()
    
    for league in world.leagues.values():
        print(f"{league.name}:")
        print(f"  • Season records structure: {type(league.season_records)}")
        print(f"  • Can track: most goals, best defense, clean sheets, etc.")
        
        # Example: We could populate this after the season
        league.season_records[2025] = {
            "most_goals_placeholder": {"player_id": "tbd", "goals": 0, "team_id": "tbd"},
            "best_defense_placeholder": {"team_id": "tbd", "goals_conceded": 0}
        }
        print(f"  • Example record structure: {list(league.season_records[2025].keys())}")
        print()
    
    # =========================================================================
    # Feature 5: Form Guide
    # =========================================================================
    print("📈 FEATURE 5: FORM GUIDE TRACKING")
    print("-" * 80)
    print("Teams track their last 5 match results (W/D/L):")
    print()
    
    # Play more matches to build form
    print("Simulating 4 more matchdays to build form history...")
    for i in range(2, 6):
        await orchestrator.advance_simulation()
        print(f"✓ Matchday {i} complete")
    print()
    
    # Show form guides
    print("Current form guides (last 5 matches):")
    teams_sorted = sorted(world.teams.values(), key=lambda t: t.points, reverse=True)
    
    for team in teams_sorted[:6]:
        form_str = " ".join(team.recent_form)
        print(f"  {team.name:30} → {form_str:15} ({team.wins}W-{team.draws}D-{team.losses}L)")
    
    print()
    
    # =========================================================================
    # Summary
    # =========================================================================
    print("=" * 80)
    print("FEATURE SUMMARY")
    print("=" * 80)
    print()
    print("✓ Pitch Conditions: 6 types (Excellent, Good, Average, Worn, Poor, Waterlogged)")
    print("✓ Team Captains: Each team has captain and vice-captain assigned")
    print("✓ Player Ratings: Average ratings calculated from match performances")
    print("✓ Season Records: Infrastructure to track league records by season")
    print("✓ Form Guide: Last 5 match results tracked automatically (W/D/L)")
    print()
    print("All features are deterministic and maintain backward compatibility!")
    print()
    
    # =========================================================================
    # Technical Details
    # =========================================================================
    print("=" * 80)
    print("TECHNICAL DETAILS")
    print("=" * 80)
    print()
    print("Pitch Conditions:")
    print("  • Influenced by weather (rain/snow → worse conditions)")
    print("  • Generated deterministically based on match ID")
    print("  • Distribution: 25% Excellent, 35% Good, 25% Average, 10% Worn, 4% Poor, 1% Waterlogged")
    print()
    
    print("Team Captains:")
    print("  • Selected from experienced players (age 25+)")
    print("  • Prefer midfielders and defenders (CM, CB, CAM)")
    print("  • Captain = highest rated, Vice-captain = second highest")
    print("  • Selection is deterministic based on player attributes")
    print()
    
    print("Average Player Ratings:")
    print("  • Match ratings stored in player.match_ratings list")
    print("  • Average calculated via player.average_rating property")
    print("  • Ratings range from 1.0 to 10.0")
    print("  • Updated automatically after each match")
    print()
    
    print("Season Records:")
    print("  • Stored in league.season_records dict")
    print("  • Structure: {season: {record_type: record_data}}")
    print("  • Ready for end-of-season award calculations")
    print()
    
    print("Form Guide:")
    print("  • Stored in team.recent_form list")
    print("  • Automatically maintains last 5 results")
    print("  • Values: 'W' (win), 'D' (draw), 'L' (loss)")
    print("  • Already implemented, enhanced documentation")
    print()


if __name__ == "__main__":
    asyncio.run(main())
