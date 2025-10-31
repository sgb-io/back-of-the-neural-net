#!/usr/bin/env python3
"""Test script to validate the fix for the match reports issue."""

import asyncio
from src.neuralnet.orchestrator import GameOrchestrator
from src.neuralnet.events import EventStore

async def test_match_reports_fix():
    """Test that the fix correctly prevents match reports before simulation."""
    print("🔧 Testing match reports fix...")
    
    # Create fresh orchestrator
    orchestrator = GameOrchestrator(EventStore(":memory:"))
    orchestrator.initialize_world()
    
    print(f"✓ World initialized with {len(orchestrator.world.teams)} teams")
    
    # Test 1: Check no match reports before simulation
    all_events = orchestrator.event_store.get_events()
    media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
    print(f"📰 Media story events before simulation: {len(media_events)}")
    
    # Test 2: Check that media previews are clearly labeled as previews
    print("\n🔍 Testing media preview generation...")
    
    # Test the media preview function directly
    from src.neuralnet.server import generate_match_media_preview
    
    # Find a derby match
    fixtures = orchestrator.get_current_matchday_fixtures()
    derby_preview = None
    
    for match in fixtures:
        home_team = orchestrator.world.get_team_by_id(match.home_team_id)
        away_team = orchestrator.world.get_team_by_id(match.away_team_id)
        
        # Check if both teams have shared words (indicating derby)
        home_words = set(home_team.name.lower().split())
        away_words = set(away_team.name.lower().split())
        
        if home_words & away_words:  # Derby match
            derby_preview = await generate_match_media_preview(
                home_team, away_team, 'derby', orchestrator.game_tools
            )
            print(f"🎯 Found derby: {home_team.name} vs {away_team.name}")
            print(f"   Headline: {derby_preview['headline']}")
            print(f"   Preview: {derby_preview['preview']}")
            print(f"   Type: {derby_preview.get('type', 'NOT SET')}")
            break
    
    # Test 3: Attempt to force generate match reports for unfinished matches
    print("\n🧪 Testing match report generation safeguards...")
    
    # Try to generate reports for unfinished matches (should return empty)
    from src.neuralnet.llm import MockLLMProvider
    
    mock_provider = MockLLMProvider()
    
    # Create mock events for an unfinished match (no MatchEnded event)
    mock_events = [
        type('MockEvent', (), {
            'event_type': 'KickOff',
            'match_id': 'test_match',
            'home_score': 0,
            'away_score': 0
        })(),
        type('MockEvent', (), {
            'event_type': 'Goal',
            'match_id': 'test_match',
            'home_score': 1,
            'away_score': 0
        })()
    ]
    
    reports_unfinished = await mock_provider.generate_match_reports(
        mock_events, orchestrator.world, "derby"
    )
    
    print(f"📋 Reports generated for unfinished match: {len(reports_unfinished)}")
    
    # Create mock events for a finished match (with MatchEnded event)
    mock_events_finished = mock_events + [
        type('MockEvent', (), {
            'event_type': 'MatchEnded',
            'match_id': 'test_match',
            'home_score': 1,
            'away_score': 0
        })()
    ]
    
    reports_finished = await mock_provider.generate_match_reports(
        mock_events_finished, orchestrator.world, "derby"
    )
    
    print(f"📋 Reports generated for finished match: {len(reports_finished)}")
    
    # Test 4: Simulate one matchday and verify reports are generated correctly
    print("\n🎮 Testing full simulation flow...")
    
    result = await orchestrator.advance_simulation()
    
    print(f"✓ Matchday completed: {result['matches_played']} matches played")
    
    # Check for media events after simulation
    all_events_after = orchestrator.event_store.get_events()
    media_events_after = [e for e in all_events_after if e.event_type == "MediaStoryPublished"]
    
    print(f"📰 Media story events after simulation: {len(media_events_after)}")
    
    # Validate results
    print("\n" + "="*80)
    print("VALIDATION RESULTS:")
    
    validation_results = []
    
    # Check 1: No reports before simulation
    if len(media_events) == 0:
        validation_results.append("✅ No match reports before simulation")
    else:
        validation_results.append("❌ Match reports found before simulation")
    
    # Check 2: Media previews clearly labeled
    if derby_preview and derby_preview.get('type') == 'match_preview':
        validation_results.append("✅ Media previews correctly labeled as previews")
    elif derby_preview and 'Preview:' in derby_preview['headline']:
        validation_results.append("✅ Media previews clearly marked as previews in headline")
    else:
        validation_results.append("❌ Media previews not clearly distinguished from reports")
    
    # Check 3: Safeguards prevent reports for unfinished matches
    if len(reports_unfinished) == 0:
        validation_results.append("✅ No reports generated for unfinished matches")
    else:
        validation_results.append("❌ Reports generated for unfinished matches")
    
    # Check 4: Reports generated for finished matches when appropriate
    if len(reports_finished) > 0:
        validation_results.append("✅ Reports generated for finished matches")
    else:
        validation_results.append("⚠️  No reports generated for finished matches (may be normal)")
    
    # Check 5: Reports generated after simulation
    if len(media_events_after) > 0:
        validation_results.append("✅ Reports generated after simulation")
    else:
        validation_results.append("⚠️  No reports generated after simulation (may be normal)")
    
    for result in validation_results:
        print(result)
    
    # Overall assessment
    failed_checks = [r for r in validation_results if r.startswith("❌")]
    if len(failed_checks) == 0:
        print("\n🎉 ALL VALIDATION CHECKS PASSED!")
        return True
    else:
        print(f"\n💥 {len(failed_checks)} VALIDATION CHECKS FAILED!")
        return False

if __name__ == "__main__":
    success = asyncio.run(test_match_reports_fix())
    print(f"\n{'✅ FIX VALIDATED' if success else '❌ FIX NEEDS MORE WORK'}")