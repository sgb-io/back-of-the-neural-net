"""Test reputation functionality."""

import pytest
from src.neuralnet.data import create_sample_world
from src.neuralnet.llm_mcp import ToolsLLMProvider, MockToolsLLMProvider


def test_player_reputation_field():
    """Test that players have reputation field."""
    world = create_sample_world()
    
    # Get first player
    first_team = next(iter(world.teams.values()))
    first_player = first_team.players[0]
    
    # Check reputation field exists and is in valid range
    assert hasattr(first_player, 'reputation')
    assert 1 <= first_player.reputation <= 100
    

def test_team_reputation_field():
    """Test that teams have reputation field."""
    world = create_sample_world()
    
    # Get first team
    first_team = next(iter(world.teams.values()))
    
    # Check reputation field exists and is in valid range
    assert hasattr(first_team, 'reputation')
    assert 1 <= first_team.reputation <= 100


def test_reputation_distribution():
    """Test that reputation values are distributed realistically."""
    world = create_sample_world()
    
    player_reputations = []
    team_reputations = []
    
    # Collect all reputation values
    for team in world.teams.values():
        team_reputations.append(team.reputation)
        for player in team.players:
            player_reputations.append(player.reputation)
    
    # Check we have variety in reputation values
    assert len(set(player_reputations)) > 5  # At least 5 different reputation values
    assert len(set(team_reputations)) > 5    # At least 5 different reputation values
    
    # Check some players have high reputation and some have low
    assert max(player_reputations) > 60  # Some high reputation players
    assert min(player_reputations) < 40  # Some low reputation players


@pytest.mark.asyncio
async def test_reputation_influences_career_summary():
    """Test that player reputation influences career summary content."""
    world = create_sample_world()
    
    # Find players with different reputation levels
    high_rep_player = None
    low_rep_player = None
    
    for team in world.teams.values():
        for player in team.players:
            if player.reputation >= 70 and high_rep_player is None:
                high_rep_player = player
            elif player.reputation <= 30 and low_rep_player is None:
                low_rep_player = player
    
    # If we don't have the exact reputation ranges, modify some players
    if high_rep_player is None:
        high_rep_player = next(iter(world.teams.values())).players[0]
        high_rep_player.reputation = 75
    
    if low_rep_player is None:
        low_rep_player = next(iter(world.teams.values())).players[1]
        low_rep_player.reputation = 25
    
    # Create LLM provider with tools
    from src.neuralnet.game_tools import GameStateTools
    tools = GameStateTools(world)
    llm_provider = MockToolsLLMProvider(tools)
    
    # Generate summaries
    high_rep_summary = await llm_provider.generate_career_summary(high_rep_player.id, world)
    low_rep_summary = await llm_provider.generate_career_summary(low_rep_player.id, world)
    
    # High reputation summaries should be longer and more elaborate
    assert len(high_rep_summary) > len(low_rep_summary)
    
    # High reputation summaries should use different language
    high_rep_words = ["recognized", "celebrated", "renowned", "exceptional", "elite"]
    low_rep_words = ["developing", "works to", "seeks to", "books at"]
    
    high_rep_summary_lower = high_rep_summary.lower()
    low_rep_summary_lower = low_rep_summary.lower()
    
    # Check for appropriate language
    has_high_rep_language = any(word in high_rep_summary_lower for word in high_rep_words)
    has_low_rep_language = any(word in low_rep_summary_lower for word in low_rep_words)
    
    assert has_high_rep_language, f"High rep summary should use appropriate language: {high_rep_summary}"
    assert has_low_rep_language, f"Low rep summary should use appropriate language: {low_rep_summary}"


def test_reputation_analysis_tools():
    """Test that reputation analysis tools work with players and teams."""
    from src.neuralnet.game_tools import GameStateTools
    
    world = create_sample_world()
    tools = GameStateTools(world)
    
    # Get first team and player
    first_team = next(iter(world.teams.values()))
    first_player = first_team.players[0]
    
    # Test player-team reputation analysis
    result = tools._analyze_reputation(first_player, first_team, "player", "team")
    
    # Should include reputation factors
    assert "entity_reputation" in result
    assert result["entity_reputation"] == first_player.reputation
    assert "relation_reputation" in result
    assert result["relation_reputation"] == first_team.reputation


if __name__ == "__main__":
    # Run basic tests
    test_player_reputation_field()
    test_team_reputation_field()
    test_reputation_distribution()
    print("All reputation tests passed!")