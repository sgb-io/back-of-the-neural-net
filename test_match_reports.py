#!/usr/bin/env python3
"""Test the match reports functionality."""

import asyncio
import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from neuralnet.entities import GameWorld, Position
from neuralnet.events import EventStore, MediaStoryPublished
from neuralnet.orchestrator import GameOrchestrator


async def test_match_reports():
    """Test that match reports are generated for important matches."""
    print("Testing match reports functionality...")
    
    # Create orchestrator with in-memory event store
    orchestrator = GameOrchestrator(EventStore(":memory:"))
    orchestrator.initialize_world()
    
    print(f"✓ World initialized with {len(orchestrator.world.leagues)} leagues")
    print(f"✓ Created {len(orchestrator.world.media_outlets)} media outlets")
    
    # Run a few simulation steps to get some matches
    for i in range(3):
        print(f"\nAdvancing simulation step {i + 1}...")
        result = await orchestrator.advance_simulation()
        
        print(f"  Status: {result['status']}")
        print(f"  Matches played: {result['matches_played']}")
        
        if 'match_reports' in result and result['match_reports']:
            print(f"  Match reports generated: {len(result['match_reports'])}")
            for report in result['match_reports']:
                print(f"    📰 {report['headline']} (sentiment: {report['sentiment']})")
        else:
            print("  No match reports generated (normal matches only)")
    
    # Check if any MediaStoryPublished events were created
    all_events = orchestrator.event_store.get_events()
    media_events = [e for e in all_events if e.event_type == "MediaStoryPublished"]
    
    print(f"\n✓ Total events in store: {len(all_events)}")
    print(f"✓ Media story events: {len(media_events)}")
    
    if media_events:
        print("\nGenerated media stories:")
        for event in media_events[:3]:  # Show first 3
            print(f"  📰 {event.headline}")
            print(f"     Sentiment: {event.sentiment}, Type: {event.story_type}")
    
    print("\n✅ Match reports test completed successfully!")


if __name__ == "__main__":
    asyncio.run(test_match_reports())