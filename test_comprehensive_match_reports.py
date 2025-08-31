#!/usr/bin/env python3
"""Test script to verify no match reports exist before simulation, including checking all possible sources."""

import asyncio
import json
from src.neuralnet.orchestrator import GameOrchestrator
from src.neuralnet.events import EventStore

async def test_comprehensive_match_reports_issue():
    """Comprehensive test to check all possible sources of match report-like content."""
    print("🔍 Comprehensive test for match reports before simulation...")
    
    # Create fresh orchestrator
    orchestrator = GameOrchestrator(EventStore(":memory:"))
    orchestrator.initialize_world()
    
    print(f"✓ World initialized with {len(orchestrator.world.teams)} teams")
    
    # 1. Check MediaStoryPublished events
    all_events = orchestrator.event_store.get_events()
    media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
    print(f"📰 MediaStoryPublished events: {len(media_events)}")
    
    # 2. Check active_stories in media outlets
    total_active_stories = 0
    for outlet in orchestrator.world.media_outlets.values():
        if outlet.active_stories:
            print(f"📺 {outlet.name} has {len(outlet.active_stories)} active stories:")
            for story in outlet.active_stories:
                print(f"   - {story}")
                total_active_stories += 1
    print(f"📺 Total active stories in outlets: {total_active_stories}")
    
    # 3. Check what the news API would return
    print("\n📡 Testing news API logic...")
    
    # Simulate the news endpoint logic
    fixtures = orchestrator.get_current_matchday_fixtures()[:10]
    media_previews_generated = 0
    
    for match in fixtures:
        home_team = orchestrator.world.get_team_by_id(match.home_team_id)
        away_team = orchestrator.world.get_team_by_id(match.away_team_id)
        
        # Check if this match would get a media preview
        from src.neuralnet.server import determine_match_importance
        importance = determine_match_importance(home_team, away_team, match.league, orchestrator.world)
        
        if importance in ["high", "derby", "title_race", "relegation"]:
            print(f"🎯 {home_team.name} vs {away_team.name} - {importance} match would get media preview")
            media_previews_generated += 1
    
    print(f"🎯 Total media previews that would be generated: {media_previews_generated}")
    
    # 4. Check narratives
    narratives = orchestrator._get_recent_narratives()
    media_story_narratives = [n for n in narratives if n.get('type') == 'media_story']
    print(f"📖 Media story narratives: {len(media_story_narratives)}")
    for narrative in media_story_narratives:
        print(f"   - {narrative.get('headline')} (from {narrative.get('source')})")
    
    # 5. Check if there are any completed matches before simulation
    completed_matches = orchestrator.get_completed_matches()
    print(f"⚽ Completed matches before simulation: {len(completed_matches)}")
    
    print("\n" + "="*80)
    print("SUMMARY:")
    print(f"- MediaStoryPublished events: {len(media_events)}")
    print(f"- Active stories in outlets: {total_active_stories}")
    print(f"- Media story narratives: {len(media_story_narratives)}")
    print(f"- Media previews that would be generated: {media_previews_generated}")
    print(f"- Completed matches: {len(completed_matches)}")
    
    # Determine if this is a potential issue
    potential_issues = []
    if len(media_events) > 0:
        potential_issues.append("MediaStoryPublished events exist before simulation")
    if total_active_stories > 0:
        potential_issues.append("Active stories exist in media outlets")
    if len(media_story_narratives) > 0:
        potential_issues.append("Media story narratives exist")
    if media_previews_generated > 0:
        potential_issues.append(f"{media_previews_generated} media previews would be generated (these might look like reports)")
    
    if potential_issues:
        print("\n❌ POTENTIAL ISSUES FOUND:")
        for issue in potential_issues:
            print(f"   - {issue}")
    else:
        print("\n✅ No issues found - no match report-like content before simulation")
    
    return len(potential_issues) == 0

if __name__ == "__main__":
    success = asyncio.run(test_comprehensive_match_reports_issue())
    print(f"\n{'✅ TEST PASSED' if success else '❌ POTENTIAL ISSUES DETECTED'}")