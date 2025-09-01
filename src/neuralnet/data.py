"""Sample fantasy data for testing and development."""

import uuid
from typing import Dict

from .entities import GameWorld, League, Player, Position, Team, ClubOwner, MediaOutlet, PlayerAgent, StaffMember


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
    
    return world


def create_fantasy_team(team_id: str, team_name: str, league: str) -> Team:
    """Create a fantasy team with generated players."""
    team = Team(
        id=team_id,
        name=team_name,
        league=league
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
    team_seed = hash(team_id) % len(player_names)
    name_index = 0
    
    for position, count in positions_needed:
        for i in range(count):
            # Use different players for each team by offsetting the index
            actual_index = (team_seed + name_index) % len(player_names)
            if actual_index < len(player_names):
                player_name = player_names[actual_index]
                name_index += 1
            else:
                player_name = f"Fantasy Player {team_id}_{name_index}"
                name_index += 1
            
            player = create_fantasy_player(player_name, position)
            team.players.append(player)
    
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
    elif age > 32:
        # Older players may have lower fitness
        fitness = player_rng.randint(70, 95)
        form = player_rng.randint(45, 75)
    else:
        # Prime age players
        fitness = player_rng.randint(80, 100) 
        form = player_rng.randint(45, 75)
    
    return Player(
        id=str(uuid.uuid4()),
        name=name,
        position=position,
        age=age,
        peak_age=peak_age,
        fitness=fitness,
        form=form,
        sharpness=player_rng.randint(70, 85),  # Start with reasonable sharpness
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
    
    for team_id in world.teams.keys():
        owner = ClubOwner(
            id=str(uuid.uuid4()),
            name=owner_names[name_index % len(owner_names)],
            team_id=team_id,
            role=random.choice(roles),
            wealth=random.randint(60, 100),
            business_acumen=random.randint(40, 90),
            ambition=random.randint(40, 80),
            patience=random.randint(30, 70),
            public_approval=random.randint(40, 80),
            years_at_club=random.randint(1, 10)
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