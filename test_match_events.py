#!/usr/bin/env python3
"""Test script to see what match events are generated and how they're used in reports."""

import asyncio
from src.neuralnet.orchestrator import GameOrchestrator
from src.neuralnet.events import EventStore

async def test_match_events():
    """Test what match events are generated and analyze them."""
    print("🔍 Testing match event generation and reporting...")
    
    # Create fresh orchestrator
    orchestrator = GameOrchestrator(EventStore(":memory:"))
    orchestrator.initialize_world()
    
    print("✓ World initialized")
    
    # Simulate one matchday
    print("\n🏟️ Simulating matchday...")
    result = await orchestrator.advance_simulation()
    
    print(f"✓ Matches played: {result['matches_played']}")
    
    # Get all events and analyze them
    all_events = orchestrator.event_store.get_events()
    
    print(f"\n📊 Total events generated: {len(all_events)}")
    
    # Categorize events
    match_events = []
    media_events = []
    other_events = []
    
    for event in all_events:
        if event.event_type in ["Goal", "YellowCard", "RedCard", "Substitution", "KickOff", "MatchStarted", "MatchEnded"]:
            match_events.append(event)
        elif event.event_type == "MediaStoryPublished":
            media_events.append(event)
        else:
            other_events.append(event)
    
    print(f"⚽ Match-related events: {len(match_events)}")
    print(f"📰 Media events: {len(media_events)}")
    print(f"🔧 Other events: {len(other_events)}")
    
    # Show detailed match events
    print("\n⚽ MATCH EVENTS DETAIL:")
    current_match_id = None
    for event in match_events:
        if hasattr(event, 'match_id'):
            if event.match_id != current_match_id:
                current_match_id = event.match_id
                print(f"\n--- Match {current_match_id} ---")
        
        if event.event_type == "Goal":
            print(f"  🥅 {event.minute}' Goal: {event.scorer} ({event.team}) {event.home_score}-{event.away_score}")
            if hasattr(event, 'assist') and event.assist:
                print(f"      Assist: {event.assist}")
        elif event.event_type == "YellowCard":
            print(f"  🟨 {event.minute}' Yellow Card: {event.player} ({event.team}) - {event.reason}")
        elif event.event_type == "RedCard":
            print(f"  🟥 {event.minute}' Red Card: {event.player} ({event.team}) - {event.reason}")
        elif event.event_type == "Substitution":
            print(f"  🔄 {event.minute}' Substitution ({event.team}): {event.player_off} → {event.player_on}")
        elif event.event_type == "MatchEnded":
            print(f"  🏁 Match ended: {event.home_score}-{event.away_score}")
    
    # Show media events
    print(f"\n📰 MEDIA EVENTS:")
    for event in media_events:
        print(f"  📝 {event.headline}")
        print(f"      Type: {event.story_type}, Sentiment: {event.sentiment}")
        print(f"      Entities: {event.entities_mentioned}")
    
    print(f"\n🏁 Analysis complete!")

if __name__ == "__main__":
    asyncio.run(test_match_events())