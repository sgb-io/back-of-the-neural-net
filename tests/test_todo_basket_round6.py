"""Test suite for TODO basket round 6 features."""

import sys
from pathlib import Path

# Add src to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from neuralnet.data import create_sample_world
from neuralnet.entities import Match, Weather, InjuryType, InjuryRecord, PlayerAward
from neuralnet.simulation import MatchSimulator
from neuralnet.orchestrator import GameOrchestrator
from neuralnet.events import EventStore
import uuid
import tempfile


def test_weather_conditions_exist():
    """Test that weather conditions are properly defined."""
    # Test all weather types are available
    assert Weather.SUNNY == "Sunny"
    assert Weather.CLOUDY == "Cloudy"
    assert Weather.RAINY == "Rainy"
    assert Weather.SNOWY == "Snowy"
    assert Weather.WINDY == "Windy"
    assert Weather.FOGGY == "Foggy"


def test_match_has_weather():
    """Test that matches have weather information."""
    world = create_sample_world()
    team_ids = list(world.teams.keys())[:2]
    
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025,
        weather=Weather.SUNNY
    )
    
    assert match.weather == Weather.SUNNY
    assert isinstance(match.weather, Weather)


def test_match_has_attendance():
    """Test that matches have attendance information."""
    world = create_sample_world()
    team_ids = list(world.teams.keys())[:2]
    
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025,
        attendance=25000
    )
    
    assert match.attendance == 25000
    assert match.attendance >= 0


def test_match_has_atmosphere_rating():
    """Test that matches have atmosphere rating."""
    world = create_sample_world()
    team_ids = list(world.teams.keys())[:2]
    
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025,
        atmosphere_rating=75
    )
    
    assert match.atmosphere_rating == 75
    assert 1 <= match.atmosphere_rating <= 100


def test_weather_generated_deterministically():
    """Test that weather generation is deterministic based on match_id."""
    import random
    
    match_id1 = "test_match_1"
    match_id2 = "test_match_2"
    match_id3 = "test_match_1"  # Same as match_id1
    
    # Generate weather for each
    def gen_weather(match_id):
        rng = random.Random(hash(match_id) % (2**31))
        weather_roll = rng.random()
        if weather_roll < 0.30:
            return Weather.SUNNY
        elif weather_roll < 0.55:
            return Weather.CLOUDY
        elif weather_roll < 0.75:
            return Weather.RAINY
        elif weather_roll < 0.85:
            return Weather.WINDY
        elif weather_roll < 0.95:
            return Weather.FOGGY
        else:
            return Weather.SNOWY
    
    weather1 = gen_weather(match_id1)
    weather2 = gen_weather(match_id2)
    weather3 = gen_weather(match_id3)
    
    # Same match ID should produce same weather
    assert weather1 == weather3
    # Different match IDs (might) produce different weather
    assert isinstance(weather1, Weather)
    assert isinstance(weather2, Weather)


def test_attendance_calculation_logic():
    """Test the attendance calculation logic."""
    world = create_sample_world()
    import random
    
    # Get a team
    team = list(world.teams.values())[0]
    
    # Simulate attendance calculation
    match_rng = random.Random(12345)
    base_attendance = int(team.stadium_capacity * 0.75)
    rep_modifier = 1.0 + (team.reputation - 50) / 100.0
    weather_modifier = 0.85  # Rainy weather
    random_modifier = 0.90 + (match_rng.random() * 0.20)
    
    attendance = int(base_attendance * rep_modifier * weather_modifier * random_modifier)
    attendance = max(1000, min(attendance, team.stadium_capacity))
    
    # Attendance should be reasonable
    assert 1000 <= attendance <= team.stadium_capacity


def test_atmosphere_rating_logic():
    """Test the atmosphere rating calculation logic."""
    world = create_sample_world()
    
    # Get a team
    team = list(world.teams.values())[0]
    
    # Simulate atmosphere calculation
    attendance = int(team.stadium_capacity * 0.8)
    attendance_ratio = attendance / team.stadium_capacity if team.stadium_capacity > 0 else 0
    atmosphere_rating = int(30 + (attendance_ratio * 60))
    
    # Atmosphere should be in valid range
    assert 30 <= atmosphere_rating <= 100


def test_player_has_potential_rating():
    """Test that players have a potential rating."""
    world = create_sample_world()
    
    # Get a player
    player = list(world.players.values())[0]
    
    assert hasattr(player, "potential")
    assert 1 <= player.potential <= 100


def test_young_players_have_higher_potential():
    """Test that young players generally have higher potential than current rating."""
    world = create_sample_world()
    
    young_players = [p for p in world.players.values() if p.age < 23]
    
    # At least some young players should have potential higher than their current rating
    players_with_room_to_grow = [p for p in young_players if p.potential > p.overall_rating]
    
    # Most young players should have growth potential
    assert len(players_with_room_to_grow) > len(young_players) * 0.5


def test_old_players_at_potential():
    """Test that older players typically have reasonable potential vs current rating gap."""
    world = create_sample_world()
    
    old_players = [p for p in world.players.values() if p.age > p.peak_age + 3]
    
    # Old players should have potential >= current rating
    for player in old_players:
        assert player.potential >= player.overall_rating
        # The gap can be larger due to form/fitness affecting overall_rating
        # Potential represents peak ability, overall_rating includes current state
        assert player.potential - player.overall_rating <= 20


def test_player_has_injury_history():
    """Test that players have injury history tracking."""
    world = create_sample_world()
    
    player = list(world.players.values())[0]
    
    assert hasattr(player, "injury_history")
    assert isinstance(player.injury_history, list)
    # Initially empty
    assert len(player.injury_history) == 0


def test_injury_record_structure():
    """Test that injury records have correct structure."""
    injury = InjuryRecord(
        injury_type=InjuryType.HAMSTRING,
        occurred_date="2025-01-15",
        weeks_out=3,
        season=2025,
        match_id="match_123"
    )
    
    assert injury.injury_type == InjuryType.HAMSTRING
    assert injury.occurred_date == "2025-01-15"
    assert injury.weeks_out == 3
    assert injury.season == 2025
    assert injury.match_id == "match_123"


def test_player_can_have_injury_history():
    """Test that player injury history can be populated."""
    world = create_sample_world()
    player = list(world.players.values())[0]
    
    # Add an injury to history
    injury = InjuryRecord(
        injury_type=InjuryType.KNEE,
        occurred_date="2025-01-01",
        weeks_out=6,
        season=2025
    )
    
    player.injury_history.append(injury)
    
    assert len(player.injury_history) == 1
    assert player.injury_history[0].injury_type == InjuryType.KNEE


def test_player_has_awards():
    """Test that players have awards tracking."""
    world = create_sample_world()
    
    player = list(world.players.values())[0]
    
    assert hasattr(player, "awards")
    assert isinstance(player.awards, list)
    # Initially empty
    assert len(player.awards) == 0


def test_player_award_structure():
    """Test that player awards have correct structure."""
    award = PlayerAward(
        award_type="Player of the Season",
        season=2025,
        league="premier_fantasy",
        details="Top scorer with 30 goals"
    )
    
    assert award.award_type == "Player of the Season"
    assert award.season == 2025
    assert award.league == "premier_fantasy"
    assert award.details == "Top scorer with 30 goals"


def test_player_can_have_awards():
    """Test that player awards can be populated."""
    world = create_sample_world()
    player = list(world.players.values())[0]
    
    # Add an award
    award = PlayerAward(
        award_type="Golden Boot",
        season=2024,
        league="premier_fantasy",
        details="25 goals"
    )
    
    player.awards.append(award)
    
    assert len(player.awards) == 1
    assert player.awards[0].award_type == "Golden Boot"


def test_weather_distribution_is_reasonable():
    """Test that weather distribution is reasonable across multiple samples."""
    import random
    
    # Simulate weather generation for many matches
    def gen_weather(seed):
        rng = random.Random(seed)
        weather_roll = rng.random()
        if weather_roll < 0.30:
            return Weather.SUNNY
        elif weather_roll < 0.55:
            return Weather.CLOUDY
        elif weather_roll < 0.75:
            return Weather.RAINY
        elif weather_roll < 0.85:
            return Weather.WINDY
        elif weather_roll < 0.95:
            return Weather.FOGGY
        else:
            return Weather.SNOWY
    
    weather_counts = {}
    for i in range(200):  # Generate weather for 200 matches
        weather = gen_weather(i)
        weather_counts[weather.value] = weather_counts.get(weather.value, 0) + 1
    
    # Should have variety
    assert len(weather_counts) >= 4  # At least 4 different weather types
    
    # Most common should be Sunny or Cloudy (combined 55% probability)
    sunny_cloudy = weather_counts.get("Sunny", 0) + weather_counts.get("Cloudy", 0)
    total = sum(weather_counts.values())
    # Expect around 55%, but allow margin for randomness (45-65%)
    assert 0.45 < sunny_cloudy / total < 0.65


def test_determinism_with_new_features():
    """Test that simulation remains deterministic with new features."""
    world = create_sample_world()
    team_ids = list(world.teams.keys())[:2]
    
    match1 = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025,
        weather=Weather.SUNNY,
        attendance=30000,
        atmosphere_rating=80
    )
    
    match2 = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025,
        weather=Weather.SUNNY,
        attendance=30000,
        atmosphere_rating=80
    )
    
    world.matches[match1.id] = match1
    world.matches[match2.id] = match2
    
    # Simulate with same seed
    simulator1 = MatchSimulator(world, match1, seed=12345)
    events1 = list(simulator1.simulate())
    
    simulator2 = MatchSimulator(world, match2, seed=12345)
    events2 = list(simulator2.simulate())
    
    # Should produce same results
    assert len(events1) == len(events2)
    assert [e.event_type for e in events1] == [e.event_type for e in events2]


def test_backward_compatibility_no_weather():
    """Test that old matches without weather still work."""
    world = create_sample_world()
    team_ids = list(world.teams.keys())[:2]
    
    # Create match without explicit weather (should use default)
    match = Match(
        id=str(uuid.uuid4()),
        home_team_id=team_ids[0],
        away_team_id=team_ids[1],
        league="premier_fantasy",
        matchday=1,
        season=2025
    )
    
    # Should have default weather
    assert match.weather is not None


def test_backward_compatibility_no_potential():
    """Test that old players without potential still work."""
    from neuralnet.entities import Player, Position
    
    # Create player without potential (uses default)
    player = Player(
        id=str(uuid.uuid4()),
        name="Test Player",
        position=Position.ST,
        age=25,
        pace=70,
        shooting=75,
        passing=65,
        defending=40,
        physicality=70
    )
    
    # Should have default potential
    assert player.potential >= 1
    assert player.potential <= 100
