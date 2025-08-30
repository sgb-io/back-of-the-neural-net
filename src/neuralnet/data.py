"""Sample fantasy data for testing and development."""

import uuid
from typing import Dict

from .entities import GameWorld, League, Player, Position, Team


def create_sample_world() -> GameWorld:
    """Create a sample game world with fantasy teams and players."""
    world = GameWorld(season=2024)
    
    # Create leagues
    premier_fantasy = League(
        id="premier_fantasy",
        name="Premier Fantasy League",
        season=2024,
        teams=[]
    )
    
    la_fantasy = League(
        id="la_fantasy", 
        name="La Fantasia League",
        season=2024,
        teams=[]
    )
    
    world.leagues["premier_fantasy"] = premier_fantasy
    world.leagues["la_fantasy"] = la_fantasy
    
    # Create Premier Fantasy teams
    premier_teams = [
        ("united_dragons", "United Dragons"),
        ("city_phoenix", "City Phoenix"),
        ("rovers_wolves", "Rovers Wolves"),
        ("athletic_eagles", "Athletic Eagles"),
        ("town_tigers", "Town Tigers"),
        ("villa_lions", "Villa Lions"),
        ("wanderers_hawks", "Wanderers Hawks"),
        ("county_bears", "County Bears"),
        ("forest_foxes", "Forest Foxes"),
        ("united_sharks", "United Sharks"),
    ]
    
    for team_id, team_name in premier_teams:
        team = create_fantasy_team(team_id, team_name, "premier_fantasy")
        world.teams[team_id] = team
        premier_fantasy.teams.append(team_id)
        
        # Add players to world
        for player in team.players:
            world.players[player.id] = player
    
    # Create La Fantasia teams
    la_teams = [
        ("real_dragons", "Real Dragones"),
        ("barcelona_suns", "Barcelona Soles"),
        ("atletico_storms", "Atlético Tormentas"),
        ("valencia_flames", "Valencia Llamas"),
        ("sevilla_winds", "Sevilla Vientos"),
        ("villarreal_waves", "Villarreal Ondas"),
        ("real_eagles", "Real Águilas"),
        ("betis_stars", "Betis Estrellas"),
        ("athletic_thunder", "Athletic Truenos"),
        ("celta_comets", "Celta Cometas"),
    ]
    
    for team_id, team_name in la_teams:
        team = create_fantasy_team(team_id, team_name, "la_fantasy")
        world.teams[team_id] = team
        la_fantasy.teams.append(team_id)
        
        # Add players to world
        for player in team.players:
            world.players[player.id] = player
    
    return world


def create_fantasy_team(team_id: str, team_name: str, league: str) -> Team:
    """Create a fantasy team with generated players."""
    team = Team(
        id=team_id,
        name=team_name,
        league=league
    )
    
    # Create a basic squad (simplified formation)
    positions_needed = [
        (Position.GK, 1),
        (Position.CB, 2),
        (Position.LB, 1),
        (Position.RB, 1),
        (Position.CM, 2),
        (Position.LM, 1),
        (Position.RM, 1),
        (Position.CAM, 1),
        (Position.ST, 2),
    ]
    
    player_names = get_fantasy_player_names()
    name_index = 0
    
    for position, count in positions_needed:
        for i in range(count):
            if name_index < len(player_names):
                player_name = player_names[name_index]
                name_index += 1
            else:
                player_name = f"Fantasy Player {name_index}"
            
            player = create_fantasy_player(player_name, position)
            team.players.append(player)
    
    return team


def create_fantasy_player(name: str, position: Position) -> Player:
    """Create a fantasy player with position-appropriate stats."""
    import random
    
    # Base stats around 50, with position-specific modifiers
    base_stats = {
        "pace": random.randint(40, 70),
        "shooting": random.randint(40, 70),
        "passing": random.randint(40, 70),
        "defending": random.randint(40, 70),
        "physicality": random.randint(40, 70),
    }
    
    # Position-specific stat modifications
    if position == Position.GK:
        base_stats.update({
            "pace": random.randint(20, 40),
            "shooting": random.randint(10, 30),
            "passing": random.randint(40, 70),
            "defending": random.randint(70, 95),
            "physicality": random.randint(60, 85),
        })
    elif position in [Position.CB]:
        base_stats.update({
            "pace": random.randint(30, 60),
            "shooting": random.randint(20, 50),
            "passing": random.randint(50, 80),
            "defending": random.randint(70, 95),
            "physicality": random.randint(70, 90),
        })
    elif position in [Position.LB, Position.RB]:
        base_stats.update({
            "pace": random.randint(60, 85),
            "shooting": random.randint(30, 60),
            "passing": random.randint(60, 85),
            "defending": random.randint(60, 80),
            "physicality": random.randint(50, 75),
        })
    elif position in [Position.CM, Position.CAM]:
        base_stats.update({
            "pace": random.randint(50, 80),
            "shooting": random.randint(50, 80),
            "passing": random.randint(70, 95),
            "defending": random.randint(40, 70),
            "physicality": random.randint(50, 75),
        })
    elif position in [Position.LM, Position.RM, Position.LW, Position.RW]:
        base_stats.update({
            "pace": random.randint(70, 95),
            "shooting": random.randint(60, 85),
            "passing": random.randint(60, 85),
            "defending": random.randint(30, 60),
            "physicality": random.randint(40, 70),
        })
    elif position == Position.ST:
        base_stats.update({
            "pace": random.randint(60, 90),
            "shooting": random.randint(70, 95),
            "passing": random.randint(50, 80),
            "defending": random.randint(20, 50),
            "physicality": random.randint(60, 85),
        })
    
    return Player(
        id=str(uuid.uuid4()),
        name=name,
        position=position,
        age=random.randint(18, 35),
        **base_stats
    )


def get_fantasy_player_names() -> list[str]:
    """Get a list of fantasy player names."""
    return [
        # English-inspired fantasy names
        "Gareth Thunderfoot", "Marcus Swiftwind", "Oliver Ironshot", "James Stormpass",
        "William Goldstrike", "Harry Lightspeed", "George Strongarm", "Thomas Quickfire",
        "Daniel Steadyhand", "Michael Boldkick", "Alexander Fasttrack", "Christopher Trueheart",
        "Matthew Sharpshoot", "Andrew Fleetstep", "Joshua Powershot", "David Windrunner",
        "Robert Starpass", "John Flashstrike", "Paul Swiftturn", "Mark Thunderbolt",
        
        # Spanish-inspired fantasy names  
        "Carlos Ventoloco", "Diego Rayodorado", "Fernando Piedefuego", "Alejandro Tormentazo",
        "Rafael Vientoswift", "Miguel Llamarapida", "Antonio Ondamagica", "Francisco Solbrillante",
        "Jose Truenofuerte", "Manuel Estrellaluz", "Pablo Cometaveloz", "Javier Lluviafina",
        "Eduardo Tempestadoro", "Ricardo Fuegosalvaje", "Adrian Rayo Azul", "Santiago Ventofrio",
        "Sebastian Marcabrava", "Nicolas Ondaalta", "Gabriel Vientonorte", "Rodrigo Solponiente",
        
        # More creative fantasy names
        "Zephyr Moonkick", "Blaze Starforge", "Storm Windcaller", "Phoenix Flamefoot",
        "Thunder Swiftblade", "Lightning Fastpass", "Frost Ironwill", "Shadow Nightstrike",
        "Crystal Pureheart", "Silver Moonbeam", "Gold Sunfire", "Diamond Strongkick",
        "Ruby Speedster", "Emerald Swiftfoot", "Sapphire Trueshoot", "Onyx Powerplay",
        "Mercury Quickpass", "Neptune Wavemaker", "Jupiter Stormcaller", "Mars Firefeet",
    ]