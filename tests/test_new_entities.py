#!/usr/bin/env python3
"""Test the new entities added to the simulation."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent / "src"))

from neuralnet.data import create_sample_world
from neuralnet.entities import ClubOwner, MediaOutlet, PlayerAgent, StaffMember
from neuralnet.llm import MockLLMProvider, BrainOrchestrator
from neuralnet.orchestrator import GameOrchestrator
import asyncio


def test_entity_creation():
    """Test that all new entities are created properly."""
    print("Testing entity creation...")
    world = create_sample_world()
    
    # Check basic entity counts
    assert len(world.teams) == 20, f"Expected 20 teams, got {len(world.teams)}"
    assert len(world.players) == 240, f"Expected 240 players, got {len(world.players)}"
    assert len(world.club_owners) > 0, f"Expected club owners, got {len(world.club_owners)}"
    assert len(world.staff_members) > 0, f"Expected staff members, got {len(world.staff_members)}"
    assert len(world.player_agents) > 0, f"Expected player agents, got {len(world.player_agents)}"
    assert len(world.media_outlets) > 0, f"Expected media outlets, got {len(world.media_outlets)}"
    
    print(f"✓ Created {len(world.teams)} teams")
    print(f"✓ Created {len(world.players)} players")
    print(f"✓ Created {len(world.club_owners)} club owners")
    print(f"✓ Created {len(world.staff_members)} staff members")
    print(f"✓ Created {len(world.player_agents)} player agents")
    print(f"✓ Created {len(world.media_outlets)} media outlets")


def test_entity_relationships():
    """Test relationships between entities."""
    print("\nTesting entity relationships...")
    world = create_sample_world()
    
    # Test club owners are linked to teams
    for owner in world.club_owners.values():
        team = world.get_team_by_id(owner.team_id)
        assert team is not None, f"Club owner {owner.name} linked to non-existent team {owner.team_id}"
    
    # Test staff are linked to teams  
    for staff in world.staff_members.values():
        team = world.get_team_by_id(staff.team_id)
        assert team is not None, f"Staff member {staff.name} linked to non-existent team {staff.team_id}"
    
    # Test agents have clients
    total_clients = sum(len(agent.clients) for agent in world.player_agents.values())
    assert total_clients > 0, "No players assigned to agents"
    
    # Test client relationships
    for agent in world.player_agents.values():
        for client_id in agent.clients:
            player = world.get_player_by_id(client_id)
            assert player is not None, f"Agent {agent.name} has non-existent client {client_id}"
    
    print(f"✓ All club owners properly linked to teams")
    print(f"✓ All staff members properly linked to teams")
    print(f"✓ {total_clients} players assigned to agents")
    print(f"✓ All agent-client relationships valid")


async def test_llm_integration():
    """Test that LLM updates work with new entities."""
    print("\nTesting LLM integration with new entities...")
    world = create_sample_world()
    
    llm = MockLLMProvider()
    brain = BrainOrchestrator(llm)
    
    # Test season progress analysis (which should update new entities)
    updates = await brain.process_season_progress(world)
    
    # Should have updates for various entity types
    entity_types_updated = set(update.entity_type for update in updates)
    print(f"✓ LLM generated {len(updates)} updates")
    print(f"✓ Updated entity types: {entity_types_updated}")
    
    # Verify some specific entity types were updated
    expected_types = {"team", "club_owner", "staff_member", "player_agent", "media_outlet"}
    found_types = entity_types_updated.intersection(expected_types)
    assert len(found_types) > 0, f"Expected updates for new entities, only got: {entity_types_updated}"
    print(f"✓ Successfully updated new entity types: {found_types}")


async def test_orchestrator_integration():
    """Test that the orchestrator works with new entities."""
    print("\nTesting orchestrator integration...")
    orchestrator = GameOrchestrator()
    orchestrator.initialize_world()
    
    # Test world state includes new entity information
    world_state = orchestrator.get_world_state()
    
    assert "entities_summary" in world_state, "World state missing entities_summary"
    summary = world_state["entities_summary"]
    
    assert summary["total_club_owners"] > 0, "No club owners in world state"
    assert summary["total_staff_members"] > 0, "No staff members in world state"
    assert summary["total_player_agents"] > 0, "No player agents in world state"
    assert summary["total_media_outlets"] > 0, "No media outlets in world state"
    
    print(f"✓ World state includes entity summary")
    print(f"✓ Entity counts: {summary}")
    
    # Test narratives
    assert "recent_narratives" in world_state, "World state missing recent_narratives"
    narratives = world_state["recent_narratives"]
    print(f"✓ Generated {len(narratives)} narratives")


async def main():
    """Run all tests."""
    print("Testing new simulation concepts...\n")
    
    test_entity_creation()
    test_entity_relationships()
    await test_llm_integration()
    await test_orchestrator_integration()
    
    print("\n🎉 All tests passed! New entities successfully integrated.")


if __name__ == "__main__":
    asyncio.run(main())