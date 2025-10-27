"""Sample fantasy data for testing and development."""

import uuid
from typing import Dict

from .entities import GameWorld, League, Player, Position, Team, ClubOwner, MediaOutlet, PlayerAgent, StaffMember, Rivalry, PreferredFoot, WorkRate, Weather, InjuryType, InjuryRecord, PlayerAward


def create_sample_world() -> GameWorld:
    """Create a sample game world with fantasy teams and players."""
    world = GameWorld(season=2025)
    
    # Create leagues
    premier_fantasy = League(
        id="premier_fantasy",
        name="Premier Fantasy League",
        season=2025,
        teams=[]
    )
    
    la_fantasy = League(
        id="la_fantasy", 
        name="La Fantasia League",
        season=2025,
        teams=[]
    )
    
    world.leagues["premier_fantasy"] = premier_fantasy
    world.leagues["la_fantasy"] = la_fantasy
    
    # Create Premier Fantasy teams (parody of current Premier League teams)
    premier_teams = [
        ("man_red", "Man Red"),  # Manchester United
        ("man_blue", "Man Blue"),  # Manchester City  
        ("merseyside_red", "Merseyside Red"),  # Liverpool
        ("north_london", "North London"),  # Arsenal
        ("west_london_blue", "West London Blue"),  # Chelsea
        ("newcastle_black", "Newcastle Black"),  # Newcastle United
        ("spurs_white", "Spurs White"),  # Tottenham
        ("villa_claret", "Villa Claret"),  # Aston Villa
        ("london_hammers", "London Hammers"),  # West Ham
        ("seagulls_brighton", "Seagulls Brighton"),  # Brighton
        ("midlands_wolves", "Midlands Wolves"),  # Wolves
        ("palace_eagles", "Palace Eagles"),  # Crystal Palace
        ("toffees_blue", "Toffees Blue"),  # Everton
        ("brentford_bees", "Brentford Bees"),  # Brentford
        ("fulham_white", "Fulham White"),  # Fulham
        ("forest_red", "Forest Red"),  # Nottingham Forest
        ("bournemouth_red", "Bournemouth Red"),  # AFC Bournemouth
        ("luton_orange", "Luton Orange"),  # Luton Town
        ("burnley_claret", "Burnley Claret"),  # Burnley
        ("sheffield_red", "Sheffield Red"),  # Sheffield United
    ]
    
    for team_id, team_name in premier_teams:
        team = create_fantasy_team(team_id, team_name, "premier_fantasy")
        world.teams[team_id] = team
        premier_fantasy.teams.append(team_id)
        
        # Add players to world
        for player in team.players:
            world.players[player.id] = player
    
    # Create La Fantasia teams (parody of current La Liga teams)
    la_teams = [
        ("madrid_white", "Madrid White"),  # Real Madrid
        ("barcelona_blue", "Barcelona Blue"),  # FC Barcelona
        ("atletico_red", "Atlético Red"),  # Atlético Madrid
        ("sevilla_white", "Sevilla White"),  # Sevilla FC
        ("valencia_bat", "Valencia Bat"),  # Valencia CF
        ("bilbao_lions", "Bilbao Lions"),  # Athletic Bilbao
        ("sociedad_blue", "Sociedad Blue"),  # Real Sociedad
        ("betis_green", "Betis Green"),  # Real Betis
        ("villarreal_yellow", "Villarreal Yellow"),  # Villarreal CF
        ("celta_sky", "Celta Sky"),  # Celta de Vigo
        ("osasuna_red", "Osasuna Red"),  # CA Osasuna
        ("rayo_lightning", "Rayo Lightning"),  # Rayo Vallecano
        ("getafe_blue", "Getafe Blue"),  # Getafe CF
        ("mallorca_red", "Mallorca Red"),  # RCD Mallorca
        ("cadiz_yellow", "Cádiz Yellow"),  # Cádiz CF
        ("alaves_blue", "Alavés Blue"),  # Deportivo Alavés
        ("girona_red", "Girona Red"),  # Girona FC
        ("las_palmas_yellow", "Las Palmas Yellow"),  # UD Las Palmas
        ("leganes_blue", "Leganés Blue"),  # CD Leganés
        ("espanyol_blue", "Espanyol Blue"),  # RCD Espanyol
    ]
    
    for team_id, team_name in la_teams:
        team = create_fantasy_team(team_id, team_name, "la_fantasy")
        world.teams[team_id] = team
        la_fantasy.teams.append(team_id)
        
        # Add players to world
        for player in team.players:
            world.players[player.id] = player
    
    # Create club owners, staff, agents, and media outlets
    _create_club_owners(world)
    _create_staff_members(world)
    _create_player_agents(world)
    _create_media_outlets(world)
    _create_rivalries(world)
    
    return world


def create_fantasy_team(team_id: str, team_name: str, league: str) -> Team:
    """Create a fantasy team with generated players."""
    import random
    
    # Use team_id as seed for consistent generation
    team_rng = random.Random(hash(team_id) % (2**31))
    
    # Determine team reputation based on league and some randomness
    # Premier Fantasy teams tend to have higher reputation than La Fantasia
    if league == "premier_fantasy":
        base_reputation = team_rng.randint(35, 85)
    else:  # la_fantasy
        base_reputation = team_rng.randint(30, 80)
    
    # Certain "big clubs" get reputation boosts based on name patterns
    big_club_patterns = ["madrid", "barcelona", "man_", "merseyside", "north_london", "west_london_blue"]
    if any(pattern in team_id.lower() for pattern in big_club_patterns):
        base_reputation += team_rng.randint(10, 20)
    
    # Ensure reputation stays within bounds
    team_reputation = max(1, min(100, base_reputation))
    
    # Generate stadium details based on reputation
    stadium_names = _generate_stadium_name(team_name, team_rng)
    
    # Stadium capacity based on reputation and some variance
    base_capacity = 20000 + (team_reputation * 500)  # 20k to 70k range
    capacity_variance = team_rng.randint(-5000, 15000)  # Add some randomness
    stadium_capacity = max(10000, min(100000, base_capacity + capacity_variance))
    
    # Fanbase size influenced by reputation and stadium capacity
    base_fanbase = team_reputation * 1000  # 30k to 100k base
    fanbase_variance = team_rng.randint(-10000, 20000)
    fanbase_size = max(5000, base_fanbase + fanbase_variance)
    
    # Season ticket holders (typically 30-60% of stadium capacity for successful clubs)
    st_ratio = 0.2 + (team_reputation / 100.0) * 0.4  # 20% to 60%
    season_ticket_holders = int(stadium_capacity * st_ratio * team_rng.uniform(0.8, 1.2))
    season_ticket_holders = max(500, min(season_ticket_holders, int(stadium_capacity * 0.8)))
    
    # Financial setup based on reputation and owner wealth
    base_balance = 500000 + (team_reputation * 15000)  # £500k to £2M
    initial_balance = base_balance + team_rng.randint(-200000, 500000)
    initial_balance = max(100000, initial_balance)
    
    # Monthly costs based on club size and reputation
    base_wages = 50000 + (team_reputation * 1500)  # £50k to £200k per month
    monthly_wage_costs = base_wages + team_rng.randint(-10000, 20000)
    
    stadium_costs = 10000 + (stadium_capacity // 1000) * 1000  # £10k-£100k based on capacity
    facilities_costs = 5000 + (team_reputation * 300)  # £5k-£35k based on reputation
    
    # Training facilities quality correlates with reputation but has variance
    training_quality = team_reputation + team_rng.randint(-15, 15)
    training_quality = max(1, min(100, training_quality))
    
    team = Team(
        id=team_id,
        name=team_name,
        league=league,
        reputation=team_reputation,
        # Financial setup
        balance=initial_balance,
        initial_balance=initial_balance,
        owner_investment=0,
        monthly_wage_costs=monthly_wage_costs,
        monthly_stadium_costs=stadium_costs,
        monthly_facilities_costs=facilities_costs,
        # Stadium
        stadium_name=stadium_names,
        stadium_capacity=stadium_capacity,
        # Training facilities
        training_facilities_quality=training_quality,
        # Fanbase
        fanbase_size=fanbase_size,
        season_ticket_holders=season_ticket_holders
    )
    
    # Create a full squad with starting 11, subs, and squad depth (~25 players)
    positions_needed = [
        # Starting 11 + key backups
        (Position.GK, 3),    # 1 starter + 2 backups
        (Position.CB, 4),    # 2 starters + 2 backups  
        (Position.LB, 2),    # 1 starter + 1 backup
        (Position.RB, 2),    # 1 starter + 1 backup
        (Position.CM, 4),    # 2 starters + 2 backups
        (Position.LM, 2),    # 1 starter + 1 backup
        (Position.RM, 2),    # 1 starter + 1 backup
        (Position.CAM, 2),   # 1 starter + 1 backup
        (Position.LW, 2),    # Additional wing options
        (Position.RW, 2),    # Additional wing options
        (Position.ST, 4),    # 2 starters + 2 backups
    ]
    
    player_names = get_fantasy_player_names()
    
    # Use team_id as a hash to get a different starting point for each team
    # Make sure teams have more diverse player names by using larger offsets
    team_seed = hash(team_id) % len(player_names)
    team_offset = (hash(team_id) // len(player_names)) % (len(player_names) // 3)  # Distribute across 1/3 of names
    name_index = 0
    
    for position, count in positions_needed:
        for i in range(count):
            # Use different players for each team by offsetting the index
            actual_index = (team_seed + team_offset + name_index) % len(player_names)
            if actual_index < len(player_names):
                player_name = player_names[actual_index]
                name_index += 1
            else:
                player_name = f"Fantasy Player {team_id}_{name_index}"
                name_index += 1
            
            player = create_fantasy_player(player_name, position)
            team.players.append(player)
    
    # Assign captain and vice-captain (choose from experienced, high-reputation players)
    # Prefer midfielders and defenders for captaincy
    captain_candidates = [
        p for p in team.players 
        if p.position in [Position.CM, Position.CB, Position.CAM] and p.age >= 25
    ]
    
    if not captain_candidates:
        # Fall back to any experienced player
        captain_candidates = [p for p in team.players if p.age >= 25]
    
    if captain_candidates:
        # Captain is the player with highest overall rating among candidates
        captain = max(captain_candidates, key=lambda p: p.overall_rating)
        team.captain_id = captain.id
        
        # Vice-captain is second-highest rated (excluding captain)
        vice_captain_candidates = [p for p in captain_candidates if p.id != captain.id]
        if vice_captain_candidates:
            vice_captain = max(vice_captain_candidates, key=lambda p: p.overall_rating)
            team.vice_captain_id = vice_captain.id
    
    return team


def create_fantasy_player(name: str, position: Position) -> Player:
    """Create a fantasy player with position-appropriate stats."""
    import random
    
    # Use a deterministic seed based on the player name for consistent generation
    player_seed = hash(name) % (2**31)
    player_rng = random.Random(player_seed)
    
    # Base stats around 50, with position-specific modifiers
    base_stats = {
        "pace": player_rng.randint(40, 70),
        "shooting": player_rng.randint(40, 70),
        "passing": player_rng.randint(40, 70),
        "defending": player_rng.randint(40, 70),
        "physicality": player_rng.randint(40, 70),
    }
    
    # Position-specific stat modifications
    if position == Position.GK:
        base_stats.update({
            "pace": player_rng.randint(20, 40),
            "shooting": player_rng.randint(10, 30),
            "passing": player_rng.randint(40, 70),
            "defending": player_rng.randint(70, 95),
            "physicality": player_rng.randint(60, 85),
        })
    elif position in [Position.CB]:
        base_stats.update({
            "pace": player_rng.randint(30, 60),
            "shooting": player_rng.randint(20, 50),
            "passing": player_rng.randint(50, 80),
            "defending": player_rng.randint(70, 95),
            "physicality": player_rng.randint(70, 90),
        })
    elif position in [Position.LB, Position.RB]:
        base_stats.update({
            "pace": player_rng.randint(60, 85),
            "shooting": player_rng.randint(30, 60),
            "passing": player_rng.randint(60, 85),
            "defending": player_rng.randint(60, 80),
            "physicality": player_rng.randint(50, 75),
        })
    elif position in [Position.CM, Position.CAM]:
        base_stats.update({
            "pace": player_rng.randint(50, 80),
            "shooting": player_rng.randint(50, 80),
            "passing": player_rng.randint(70, 95),
            "defending": player_rng.randint(40, 70),
            "physicality": player_rng.randint(50, 75),
        })
    elif position in [Position.LM, Position.RM, Position.LW, Position.RW]:
        base_stats.update({
            "pace": player_rng.randint(70, 95),
            "shooting": player_rng.randint(60, 85),
            "passing": player_rng.randint(60, 85),
            "defending": player_rng.randint(30, 60),
            "physicality": player_rng.randint(40, 70),
        })
    elif position == Position.ST:
        base_stats.update({
            "pace": player_rng.randint(60, 90),
            "shooting": player_rng.randint(70, 95),
            "passing": player_rng.randint(50, 80),
            "defending": player_rng.randint(20, 50),
            "physicality": player_rng.randint(60, 85),
        })
    
    # Generate realistic age and peak age
    age = player_rng.randint(18, 35)
    # Peak age varies by position and individual differences
    if position == Position.GK:
        peak_age = player_rng.randint(28, 32)  # Goalkeepers peak later
    elif position in [Position.ST, Position.LW, Position.RW]:
        peak_age = player_rng.randint(25, 29)  # Attackers peak earlier
    else:
        peak_age = player_rng.randint(26, 30)  # Midfielders and defenders
    
    # Adjust peak age for individual variation
    peak_age += player_rng.randint(-2, 2)
    peak_age = max(22, min(35, peak_age))  # Keep within reasonable bounds
    
    # Set fitness and form based on age
    if age < 23:
        # Young players often have high fitness but inconsistent form
        fitness = player_rng.randint(85, 100)
        form = player_rng.randint(40, 70)
        # Young players typically have lower reputation unless they're prodigies
        reputation = player_rng.randint(15, 40)
    elif age > 32:
        # Older players may have lower fitness but established reputation
        fitness = player_rng.randint(70, 95)
        form = player_rng.randint(45, 75)
        # Older players typically have higher reputation from career achievements
        reputation = player_rng.randint(40, 75)
    else:
        # Prime age players
        fitness = player_rng.randint(80, 100) 
        form = player_rng.randint(45, 75)
        # Prime age players have moderate to high reputation
        reputation = player_rng.randint(25, 65)
    
    # Adjust reputation based on overall ability (players with higher stats tend to be more famous)
    overall_ability = sum(base_stats.values()) / len(base_stats)
    if overall_ability > 70:
        reputation += player_rng.randint(10, 20)  # High ability players get reputation boost
    elif overall_ability < 50:
        reputation -= player_rng.randint(5, 15)   # Low ability players get reputation penalty
        
    # Ensure reputation stays within bounds
    reputation = max(1, min(100, reputation))
    
    # Generate contract details
    contract_years = player_rng.randint(1, 5)  # 1 to 5 years remaining
    
    # Determine preferred foot (70% right, 20% left, 10% both)
    foot_roll = player_rng.random()
    if foot_roll < 0.70:
        preferred_foot = PreferredFoot.RIGHT
    elif foot_roll < 0.90:
        preferred_foot = PreferredFoot.LEFT
    else:
        preferred_foot = PreferredFoot.BOTH
    
    # Determine weak foot rating (1-5 stars)
    # Distribution: 10% get 1 star, 25% get 2 stars, 40% get 3 stars, 20% get 4 stars, 5% get 5 stars
    # Players with "both" as preferred foot get better weak foot ratings
    weak_foot_roll = player_rng.random()
    if preferred_foot == PreferredFoot.BOTH:
        # Two-footed players have better weak foot ratings
        if weak_foot_roll < 0.30:
            weak_foot = 4
        elif weak_foot_roll < 0.70:
            weak_foot = 5
        else:
            weak_foot = 3
    else:
        # Regular distribution
        if weak_foot_roll < 0.10:
            weak_foot = 1
        elif weak_foot_roll < 0.35:
            weak_foot = 2
        elif weak_foot_roll < 0.75:
            weak_foot = 3
        elif weak_foot_roll < 0.95:
            weak_foot = 4
        else:
            weak_foot = 5
    
    # Determine work rates based on position
    if position == Position.ST:
        # Strikers tend to have high attacking, low/medium defending
        attacking_work_rate = player_rng.choice([WorkRate.HIGH, WorkRate.HIGH, WorkRate.MEDIUM])
        defensive_work_rate = player_rng.choice([WorkRate.LOW, WorkRate.LOW, WorkRate.MEDIUM])
    elif position in [Position.LW, Position.RW]:
        # Wingers similar to strikers
        attacking_work_rate = player_rng.choice([WorkRate.HIGH, WorkRate.MEDIUM])
        defensive_work_rate = player_rng.choice([WorkRate.LOW, WorkRate.MEDIUM])
    elif position in [Position.CB, Position.LB, Position.RB]:
        # Defenders tend to have low attacking, high defending (fullbacks can be medium/high attacking)
        if position in [Position.LB, Position.RB]:
            attacking_work_rate = player_rng.choice([WorkRate.LOW, WorkRate.MEDIUM, WorkRate.HIGH])
        else:
            attacking_work_rate = player_rng.choice([WorkRate.LOW, WorkRate.MEDIUM])
        defensive_work_rate = player_rng.choice([WorkRate.HIGH, WorkRate.HIGH, WorkRate.MEDIUM])
    elif position == Position.CAM:
        # Attacking midfielders high attacking, low/medium defending
        attacking_work_rate = player_rng.choice([WorkRate.HIGH, WorkRate.MEDIUM])
        defensive_work_rate = player_rng.choice([WorkRate.LOW, WorkRate.MEDIUM])
    elif position == Position.CM:
        # Central midfielders balanced
        attacking_work_rate = player_rng.choice([WorkRate.MEDIUM, WorkRate.HIGH])
        defensive_work_rate = player_rng.choice([WorkRate.MEDIUM, WorkRate.HIGH])
    elif position in [Position.LM, Position.RM]:
        # Wide midfielders medium/high attacking, medium defending
        attacking_work_rate = player_rng.choice([WorkRate.MEDIUM, WorkRate.HIGH])
        defensive_work_rate = WorkRate.MEDIUM
    else:  # GK
        # Goalkeepers have low work rates for both
        attacking_work_rate = WorkRate.LOW
        defensive_work_rate = WorkRate.LOW
    
    # Determine skill moves rating (1-5 stars)
    # Distribution: 15% get 1 star, 30% get 2 stars, 35% get 3 stars, 15% get 4 stars, 5% get 5 stars
    # Attacking players and wingers get better skill moves on average
    skill_roll = player_rng.random()
    if position in [Position.LW, Position.RW, Position.CAM, Position.ST]:
        # Attacking players have better skill moves
        if skill_roll < 0.05:
            skill_moves = 1
        elif skill_roll < 0.20:
            skill_moves = 2
        elif skill_roll < 0.55:
            skill_moves = 3
        elif skill_roll < 0.85:
            skill_moves = 4
        else:
            skill_moves = 5
    elif position in [Position.CB, Position.GK]:
        # Defenders and goalkeepers have lower skill moves
        if skill_roll < 0.30:
            skill_moves = 1
        elif skill_roll < 0.65:
            skill_moves = 2
        elif skill_roll < 0.90:
            skill_moves = 3
        elif skill_roll < 0.98:
            skill_moves = 4
        else:
            skill_moves = 5
    else:
        # Regular distribution for midfielders and fullbacks
        if skill_roll < 0.15:
            skill_moves = 1
        elif skill_roll < 0.45:
            skill_moves = 2
        elif skill_roll < 0.80:
            skill_moves = 3
        elif skill_roll < 0.95:
            skill_moves = 4
        else:
            skill_moves = 5
    
    # Generate player traits based on attributes
    from .entities import PlayerTrait
    traits = []
    
    # Check for specific traits based on attributes
    if base_stats["pace"] >= 85:
        traits.append(PlayerTrait.SPEEDSTER)
    if base_stats["shooting"] >= 85:
        traits.append(PlayerTrait.CLINICAL_FINISHER)
    if base_stats["passing"] >= 85:
        traits.append(PlayerTrait.PLAYMAKER)
    if base_stats["defending"] >= 85:
        traits.append(PlayerTrait.WALL)
    if base_stats["physicality"] >= 85:
        traits.append(PlayerTrait.POWERHOUSE)
    
    # Check for skill-based traits
    if skill_moves >= 4:
        if PlayerTrait.TECHNICAL not in traits:
            traits.append(PlayerTrait.TECHNICAL)
    
    # Check for work rate traits
    if attacking_work_rate == WorkRate.HIGH and defensive_work_rate == WorkRate.HIGH:
        traits.append(PlayerTrait.ENGINE)
    
    # Leadership trait for experienced players
    if age >= 28 and reputation >= 60:
        traits.append(PlayerTrait.LEADER)
    
    # Flair trait for highly skilled players
    if skill_moves == 5 and overall_ability >= 70:
        if PlayerTrait.FLAIR not in traits:
            traits.append(PlayerTrait.FLAIR)
    
    # Injury prone trait (5% chance)
    if player_rng.random() < 0.05:
        traits.append(PlayerTrait.INJURY_PRONE)
    
    # Calculate salary based on ability, age, and reputation
    base_salary = 15000  # £15k minimum
    ability_bonus = int(overall_ability * 1000)  # Up to £70k for 70+ rated players
    reputation_bonus = int(reputation * 500)  # Up to £50k for 100 reputation
    age_factor = 1.0
    
    if age < 23:
        age_factor = 0.6  # Young players earn less initially
    elif age > 32:
        age_factor = 0.8  # Older players may take wage cuts
    
    salary = int((base_salary + ability_bonus + reputation_bonus) * age_factor)
    
    # Calculate potential rating
    # Young players have higher potential than their current rating
    # Peak age players are at or near their potential
    # Older players are at their max potential (current rating is potential)
    current_rating = int(overall_ability)
    if age < 23:
        # Young players: potential is 10-25 points higher than current
        potential = current_rating + player_rng.randint(10, 25)
    elif age < peak_age:
        # Pre-peak players: potential is 5-15 points higher
        potential = current_rating + player_rng.randint(5, 15)
    elif age <= peak_age + 2:
        # Peak age players: at or very close to potential
        potential = current_rating + player_rng.randint(0, 5)
    else:
        # Post-peak players: current rating is their potential (they've peaked)
        # Set potential equal to current or slightly higher (1-2 points max)
        potential = current_rating + player_rng.randint(0, 2)
    
    # Cap potential at 100
    potential = min(100, potential)
    
    # Create the player instance 
    player = Player(
        id=str(uuid.uuid4()),
        name=name,
        position=position,
        age=age,
        peak_age=peak_age,
        fitness=fitness,
        form=form,
        reputation=reputation,
        sharpness=player_rng.randint(70, 85),  # Start with reasonable sharpness
        contract_years_remaining=contract_years,
        salary=salary,
        preferred_foot=preferred_foot,
        weak_foot=weak_foot,
        skill_moves=skill_moves,
        attacking_work_rate=attacking_work_rate,
        defensive_work_rate=defensive_work_rate,
        traits=traits,
        potential=potential,
        **base_stats
    )
    
    # Set market value using the calculated property
    player.market_value = player.calculated_market_value
    
    return player


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


def _generate_stadium_name(team_name: str, rng) -> str:
    """Generate a fantasy stadium name based on team name."""
    # Extract base name (remove color descriptors)
    base_words = []
    color_words = {"red", "blue", "white", "black", "green", "yellow", "claret", "orange"}
    
    words = team_name.lower().split()
    for word in words:
        if word not in color_words:
            base_words.append(word.capitalize())
    
    if not base_words:
        base_words = [team_name.split()[0].capitalize()]
    
    # Stadium naming patterns
    patterns = [
        f"{base_words[0]} Park",
        f"{base_words[0]} Stadium", 
        f"{base_words[0]} Arena",
        f"The {base_words[0]} Ground",
        f"{base_words[0]} Field",
        f"New {base_words[0]} Stadium",
    ]
    
    # Some special patterns for certain names
    if "merseyside" in team_name.lower():
        patterns.extend(["Anfield Fantasy", "Goodison Fantasy"])
    elif "manchester" in team_name.lower() or "man_" in team_name.lower():
        patterns.extend(["Old Trafford Fantasy", "Etihad Fantasy"])
    elif "madrid" in team_name.lower():
        patterns.extend(["Santiago Bernabéu Fantasy", "Metropolitano Fantasy"])
    elif "barcelona" in team_name.lower():
        patterns.extend(["Camp Nou Fantasy"])
    
    return rng.choice(patterns)


def _create_club_owners(world: GameWorld) -> None:
    """Create club owners for all teams."""
    import random
    
    owner_names = [
        "Sir Reginald Goldworth", "Lady Victoria Silverstein", "Lord Edmund Blackstone",
        "Baron Marcus Windmere", "Duchess Eleanor Brightwater", "Earl Thomas Stormhold",
        "Count Alexander Ironwood", "Marquess James Shadowmere", "Duke William Starforge",
        "Princess Isabella Moonhaven", "Prince Charles Fireborn", "Sir Arthur Lightbringer",
        "Lady Margaret Swiftwind", "Lord Henry Goldcrest", "Baroness Catherine Brightfire",
        "Don Carlos Ventodoro", "Doña Isabella Solbrillante", "Señor Diego Tierrafuerte",
        "Señora Carmen Ondaplatina", "Don Rafael Cieloazul", "Doña Sofia Estrellaluz"
    ]
    
    roles = ["Owner", "Chairman", "Director", "President"]
    name_index = 0
    
    for team_id, team in world.teams.items():
        # Owner wealth should correlate with team reputation
        # Elite clubs (reputation > 70) get wealthy owners (80-100)
        # Mid-tier clubs (reputation 40-70) get moderate wealth (50-85)
        # Lower clubs (reputation < 40) get varied wealth (30-70)
        
        team_rep = team.reputation
        if team_rep > 70:
            wealth_range = (80, 100)
        elif team_rep > 40:
            wealth_range = (50, 85)
        else:
            wealth_range = (30, 70)
        
        # Add some randomness but keep correlation
        owner_wealth = random.randint(wealth_range[0], wealth_range[1])
        
        # Investment tendency varies independently but wealthy owners tend to invest more
        base_investment_tendency = 30 + (owner_wealth // 2)  # 45-80 range
        investment_tendency = random.randint(
            max(1, base_investment_tendency - 20),
            min(100, base_investment_tendency + 20)
        )
        
        owner = ClubOwner(
            id=str(uuid.uuid4()),
            name=owner_names[name_index % len(owner_names)],
            team_id=team_id,
            role=random.choice(roles),
            wealth=owner_wealth,
            business_acumen=random.randint(40, 90),
            investment_tendency=investment_tendency,
            ambition=random.randint(40, 80),
            patience=random.randint(30, 70),
            public_approval=random.randint(40, 80),
            years_at_club=random.randint(1, 10),
            total_invested=0,
            last_investment=0
        )
        world.club_owners[owner.id] = owner
        name_index += 1


def _create_staff_members(world: GameWorld) -> None:
    """Create staff members for all teams."""
    import random
    
    staff_names = [
        "Giuseppe Tacticus", "Antonio Motivatore", "Francesco Preparatore", "Marco Analytico",
        "Roberto Fisico", "Andrea Mentale", "Stefano Tecnico", "Alessandro Strategico",
        "Lorenzo Atletico", "Matteo Performante", "Hans Methodology", "Klaus Systematic",
        "Wolfgang Precision", "Gunther Excellence", "Jurgen Innovative", "Franz Strategic",
        "Pierre Excellence", "Jean-Claude Perfection", "Michel Tactique", "Henri Discipline",
        "Pep Genialidad", "Luis Inteligencia", "Carlos Experiencia", "Miguel Sabiduría"
    ]
    
    roles = ["Head Coach", "Assistant Coach", "Fitness Coach", "Goalkeeping Coach", 
             "Physio", "Scout", "Analyst", "Youth Coach"]
    
    name_index = 0
    
    for team_id in world.teams.keys():
        # Each team gets 3-4 staff members
        num_staff = random.randint(3, 4)
        selected_roles = random.sample(roles, num_staff)
        
        for role in selected_roles:
            staff = StaffMember(
                id=str(uuid.uuid4()),
                name=staff_names[name_index % len(staff_names)],
                team_id=team_id,
                role=role,
                experience=random.randint(30, 90),
                specialization=random.randint(40, 95),
                morale=random.randint(40, 80),
                team_rapport=random.randint(40, 80),
                contract_years_remaining=random.randint(1, 4),
                salary=random.randint(30000, 200000)
            )
            world.staff_members[staff.id] = staff
            name_index += 1


def _create_player_agents(world: GameWorld) -> None:
    """Create player agents and assign them to players."""
    import random
    
    agent_data = [
        ("Jorge Mendes Fantasy", "Super Star Sports"),
        ("Mino Raiola Fantastic", "Power Player Management"),
        ("Jonathan Barnett Dreams", "Creative Artists Agency Fantasy"),
        ("Pini Zahavi Legends", "Elite Player Representation"),
        ("Kia Joorabchian Magic", "Media Base Sports Fantasy"),
        ("Pere Guardiola Visions", "Family Business Agency"),
        ("Volker Struth Innovations", "Sports Total Fantasy"),
        ("Fali Ramadani Excellence", "Lian Sports Fantasy"),
        ("Federico Pastorello Prestige", "P&P Sport Management Fantasy"),
        ("Carlos Bucero Success", "You First Sports Fantasy")
    ]
    
    # Create agents
    agents = []
    for i, (agent_name, agency_name) in enumerate(agent_data):
        agent = PlayerAgent(
            id=str(uuid.uuid4()),
            name=agent_name,
            agency_name=agency_name,
            negotiation_skill=random.randint(60, 95),
            network_reach=random.randint(50, 90),
            reputation=random.randint(50, 85),
            aggressiveness=random.randint(30, 80),
            clients=[]
        )
        agents.append(agent)
        world.player_agents[agent.id] = agent
    
    # Assign players to agents (roughly 70% of players have agents)
    all_players = list(world.players.keys())
    random.shuffle(all_players)
    
    players_with_agents = all_players[:int(len(all_players) * 0.7)]
    
    for i, player_id in enumerate(players_with_agents):
        agent = agents[i % len(agents)]
        agent.clients.append(player_id)


def _create_media_outlets(world: GameWorld) -> None:
    """Create media outlets for coverage."""
    import random
    
    outlets = [
        ("Fantasy Football Times", "Newspaper"),
        ("Football Fantasy Weekly", "Magazine"),
        ("Sport Vision Fantasy", "TV"),
        ("Goal Stream Fantasy", "Online"),
        ("Fantasy Match Radio", "Radio"),
        ("The Football Fantasy", "Newspaper"),
        ("Sport Tribune Fantasy", "Newspaper"),
        ("Fantasy Football Network", "TV"),
        ("Digital Sport Fantasy", "Online"),
        ("Radio Football Fantasy", "Radio")
    ]
    
    for outlet_name, outlet_type in outlets:
        outlet = MediaOutlet(
            id=str(uuid.uuid4()),
            name=outlet_name,
            outlet_type=outlet_type,
            reach=random.randint(40, 90),
            credibility=random.randint(50, 85),
            sensationalism=random.randint(30, 70),
            bias_towards_teams={},
            active_stories=[]
        )
        
        # Add some random team biases (only for a few teams)
        teams_to_bias = random.sample(list(world.teams.keys()), random.randint(2, 5))
        for team_id in teams_to_bias:
            outlet.bias_towards_teams[team_id] = random.randint(-30, 30)
        
        world.media_outlets[outlet.id] = outlet


def _create_rivalries(world: GameWorld) -> None:
    """Create rivalries between teams."""
    
    # Premier Fantasy League rivalries
    premier_rivalries = [
        # Merseyside Derby - the main example from the issue
        {
            "team1_id": "merseyside_red",
            "team2_id": "toffees_blue", 
            "name": "Merseyside Derby",
            "intensity": 95,
            "description": "The historic Merseyside rivalry between the Red and Blue sides of Liverpool"
        },
        # Manchester Derby
        {
            "team1_id": "man_red",
            "team2_id": "man_blue",
            "name": "Manchester Derby", 
            "intensity": 90,
            "description": "The fierce Manchester rivalry between United and City"
        },
        # North London Derby
        {
            "team1_id": "north_london",
            "team2_id": "spurs_white",
            "name": "North London Derby",
            "intensity": 88,
            "description": "The North London rivalry between Arsenal and Tottenham"
        },
        # West London rivalries
        {
            "team1_id": "west_london_blue",
            "team2_id": "fulham_white",
            "name": "West London Derby",
            "intensity": 70,
            "description": "Local West London rivalry"
        },
        {
            "team1_id": "west_london_blue", 
            "team2_id": "brentford_bees",
            "name": "West London Derby",
            "intensity": 65,
            "description": "West London rivalry between Chelsea and Brentford"
        },
        # London rivalries
        {
            "team1_id": "london_hammers",
            "team2_id": "palace_eagles",
            "name": "South London Derby",
            "intensity": 75,
            "description": "South-East London rivalry"
        },
        # Midlands rivalries
        {
            "team1_id": "villa_claret",
            "team2_id": "midlands_wolves",
            "name": "Midlands Derby", 
            "intensity": 80,
            "description": "Historic Midlands rivalry between Villa and Wolves"
        },
        # Claret rivalries
        {
            "team1_id": "villa_claret",
            "team2_id": "burnley_claret",
            "name": "Claret Derby",
            "intensity": 60,
            "description": "Battle of the Claret and Blue teams"
        }
    ]
    
    # La Fantasia League rivalries
    la_rivalries = [
        # El Clásico equivalent
        {
            "team1_id": "madrid_white",
            "team2_id": "barcelona_blue", 
            "name": "El Clásico Fantasia",
            "intensity": 100,
            "description": "The greatest rivalry in fantasy football between Madrid White and Barcelona Blue"
        },
        # Madrid Derby
        {
            "team1_id": "madrid_white",
            "team2_id": "atletico_red",
            "name": "Madrid Derby",
            "intensity": 85,
            "description": "The Madrid city rivalry"
        },
        # Seville Derby
        {
            "team1_id": "sevilla_white",
            "team2_id": "betis_green",
            "name": "Seville Derby",
            "intensity": 90,
            "description": "The passionate Seville city rivalry"
        },
        # Basque rivalries
        {
            "team1_id": "bilbao_lions",
            "team2_id": "sociedad_blue",
            "name": "Basque Derby",
            "intensity": 85,
            "description": "Basque regional rivalry"
        }
    ]
    
    # Create all rivalries
    all_rivalries = premier_rivalries + la_rivalries
    
    for rivalry_data in all_rivalries:
        # Check if both teams exist in the world
        if (rivalry_data["team1_id"] in world.teams and 
            rivalry_data["team2_id"] in world.teams):
            
            rivalry = Rivalry(
                id=str(uuid.uuid4()),
                team1_id=rivalry_data["team1_id"],
                team2_id=rivalry_data["team2_id"],
                name=rivalry_data["name"],
                intensity=rivalry_data["intensity"],
                description=rivalry_data["description"]
            )
            world.rivalries[rivalry.id] = rivalry