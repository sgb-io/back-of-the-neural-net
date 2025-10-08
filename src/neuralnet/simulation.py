"""Deterministic match simulation engine."""

import random
from collections.abc import Generator

from .entities import GameWorld, Match, Position, Team
from .events import (
    CornerKick,
    Foul,
    Goal,
    Injury,
    KickOff,
    MatchEnded,
    MatchEvent,
    PenaltyAwarded,
    RedCard,
    Substitution,
    YellowCard,
)


class MatchSimulator:
    """Deterministic football match simulator."""

    def __init__(self, world: GameWorld, match: Match, seed: int | None = None) -> None:
        self.world = world
        self.match = match
        self.rng = random.Random(seed or 42)

        self.home_team = world.get_team_by_id(match.home_team_id)
        self.away_team = world.get_team_by_id(match.away_team_id)

        if not self.home_team or not self.away_team:
            raise ValueError("Invalid team IDs in match")

        # Track yellow cards per player in this match
        self._match_yellow_cards: dict[str, int] = {}
        
        # Track match statistics
        self._home_shots = 0
        self._away_shots = 0
        self._home_shots_on_target = 0
        self._away_shots_on_target = 0
        self._home_corners = 0
        self._away_corners = 0
        self._home_fouls = 0
        self._away_fouls = 0
        self._home_penalties = 0
        self._away_penalties = 0
        self._possession_minutes = {"home": 0, "away": 0}

    def simulate(self) -> Generator[MatchEvent, None, None]:
        """Simulate a complete match, yielding events as they occur."""
        # Reset match state
        self.match.home_score = 0
        self.match.away_score = 0
        self.match.minute = 0
        self.match.finished = False

        # Kick off
        yield KickOff(
            match_id=self.match.id,
            minute=0,
            home_score=0,
            away_score=0
        )

        # Simulate 90 minutes of match time
        for minute in range(1, 91):
            self.match.minute = minute
            
            # Track possession for this minute based on team strength
            self._track_possession_minute()

            # Check for events this minute
            events = self._simulate_minute()
            yield from events

        # Mark match as finished
        self.match.finished = True
        
        # Calculate final possession percentages
        total_minutes = self._possession_minutes["home"] + self._possession_minutes["away"]
        home_possession = int((self._possession_minutes["home"] / total_minutes) * 100) if total_minutes > 0 else 50
        away_possession = 100 - home_possession

        # Final match result with statistics
        yield MatchEnded(
            match_id=self.match.id,
            home_team=self.home_team.id,
            away_team=self.away_team.id,
            home_score=self.match.home_score,
            away_score=self.match.away_score,
            duration_minutes=90,
            home_possession=home_possession,
            away_possession=away_possession,
            home_shots=self._home_shots,
            away_shots=self._away_shots,
            home_shots_on_target=self._home_shots_on_target,
            away_shots_on_target=self._away_shots_on_target,
            home_corners=self._home_corners,
            away_corners=self._away_corners,
            home_fouls=self._home_fouls,
            away_fouls=self._away_fouls,
            home_penalties=self._home_penalties,
            away_penalties=self._away_penalties
        )

    def _simulate_minute(self) -> list[MatchEvent]:
        """Simulate events that might occur in a single minute."""
        events = []

        # Basic probability of something happening each minute
        if self.rng.random() < 0.1:  # 10% chance per minute
            event_type = self._choose_event_type()
            event = self._create_event(event_type)
            if event:
                # Handle penalty which returns multiple events
                if isinstance(event, list):
                    events.extend(event)
                else:
                    events.append(event)
        
        # Track shots that don't result in goals or other events (happens more frequently)
        if self.rng.random() < 0.15:  # 15% chance per minute for a shot attempt
            self._track_shot_attempt()

        return events

    def _choose_event_type(self) -> str:
        """Choose what type of event occurs based on probabilities."""
        # Simple weighted random selection
        choices = [
            ("goal", 0.02),      # ~1.8 goals per match on average
            ("yellow_card", 0.04), # ~3.6 yellow cards per match
            ("red_card", 0.002),   # ~0.18 red cards per match
            ("substitution", 0.01), # Limited substitutions
            ("injury", 0.003),     # ~0.27 injuries per match
            ("corner", 0.1),       # ~9 corners per match
            ("foul", 0.2),         # ~18 fouls per match
            ("penalty", 0.001),    # ~0.09 penalties per match (rare)
        ]

        total_weight = sum(weight for _, weight in choices)
        r = self.rng.random() * total_weight

        cumulative = 0.0
        for event_type, weight in choices:
            cumulative += weight
            if r <= cumulative:
                return event_type

        return "goal"  # Default fallback

    def _create_event(self, event_type: str) -> MatchEvent | list[MatchEvent] | None:
        """Create a specific type of match event."""
        if event_type == "goal":
            return self._create_goal_event()
        elif event_type == "yellow_card":
            return self._create_yellow_card_event()
        elif event_type == "red_card":
            return self._create_red_card_event()
        elif event_type == "substitution":
            return self._create_substitution_event()
        elif event_type == "injury":
            return self._create_injury_event()
        elif event_type == "corner":
            return self._create_corner_event()
        elif event_type == "foul":
            return self._create_foul_event()
        elif event_type == "penalty":
            return self._create_penalty_event()

        return None

    def _create_goal_event(self) -> Goal:
        """Create a goal event."""
        # Choose which team scores based on team strength
        home_strength = self._calculate_team_strength(self.home_team)
        away_strength = self._calculate_team_strength(self.away_team)
        total_strength = home_strength + away_strength

        if self.rng.random() < (home_strength / total_strength):
            scoring_team = self.home_team
            self.match.home_score += 1
            # Track shot on target (resulted in goal)
            self._home_shots += 1
            self._home_shots_on_target += 1
        else:
            scoring_team = self.away_team
            self.match.away_score += 1
            # Track shot on target (resulted in goal)
            self._away_shots += 1
            self._away_shots_on_target += 1

        # Choose a random attacking player as scorer
        attackers = [
            p for p in scoring_team.players
            if p.position in [Position.ST, Position.LW, Position.RW, Position.CAM]
        ]
        if not attackers:
            attackers = [
                p for p in scoring_team.players if p.position not in [Position.GK]
            ]

        scorer = self.rng.choice(attackers) if attackers else scoring_team.players[0]

        # Maybe add an assist
        assist_player = None
        if self.rng.random() < 0.6:  # 60% chance of assist
            possible_assists = [
                p for p in scoring_team.players
                if p.id != scorer.id and p.position != Position.GK
            ]
            if possible_assists:
                assist_player = self.rng.choice(possible_assists)

        return Goal(
            match_id=self.match.id,
            minute=self.match.minute,
            home_score=self.match.home_score,
            away_score=self.match.away_score,
            scorer=scorer.name,
            team=scoring_team.id,
            assist=assist_player.name if assist_player else None
        )

    def _create_yellow_card_event(self) -> MatchEvent:
        """Create a yellow card event, or red card if player already has a yellow."""
        team = self.rng.choice([self.home_team, self.away_team])
        player = self.rng.choice(team.players)

        # Check if this player already has a yellow card in this match
        if self._match_yellow_cards.get(player.name, 0) >= 1:
            # Convert to red card instead
            player.red_cards += 1
            player.suspended = True
            player.suspension_matches_remaining = 3
            return RedCard(
                match_id=self.match.id,
                minute=self.match.minute,
                home_score=self.match.home_score,
                away_score=self.match.away_score,
                player=player.name,
                team=team.id,
                reason="Second yellow card"
            )

        reasons = [
            "Unsporting behavior",
            "Dissent",
            "Persistent fouling",
            "Delaying the game",
            "Simulation",
        ]
        reason = self.rng.choice(reasons)

        # Track this yellow card
        current_yellows = self._match_yellow_cards.get(player.name, 0)
        self._match_yellow_cards[player.name] = current_yellows + 1

        # Update player's yellow card count
        player.yellow_cards += 1

        return YellowCard(
            match_id=self.match.id,
            minute=self.match.minute,
            home_score=self.match.home_score,
            away_score=self.match.away_score,
            player=player.name,
            team=team.id,
            reason=reason
        )

    def _create_red_card_event(self) -> RedCard:
        """Create a red card event."""
        team = self.rng.choice([self.home_team, self.away_team])
        player = self.rng.choice(team.players)

        reasons = ["Serious foul play", "Violent conduct", "Offensive language"]
        reason = self.rng.choice(reasons)

        # Update player's red card count and apply 3-match suspension
        player.red_cards += 1
        player.suspended = True
        player.suspension_matches_remaining = 3

        return RedCard(
            match_id=self.match.id,
            minute=self.match.minute,
            home_score=self.match.home_score,
            away_score=self.match.away_score,
            player=player.name,
            team=team.id,
            reason=reason
        )

    def _create_substitution_event(self) -> Substitution | None:
        """Create a substitution event."""
        # Only allow substitutions after 45 minutes and if team hasn't made 3 subs yet
        if self.match.minute < 45:
            return None

        team = self.rng.choice([self.home_team, self.away_team])

        # Simple substitution logic - just pick random players
        if len(team.players) >= 2:
            player_off = self.rng.choice(team.players)
            remaining_players = [p for p in team.players if p.id != player_off.id]
            player_on = self.rng.choice(remaining_players)

            return Substitution(
                match_id=self.match.id,
                minute=self.match.minute,
                home_score=self.match.home_score,
                away_score=self.match.away_score,
                team=team.id,
                player_off=player_off.name,
                player_on=player_on.name
            )

        return None

    def _create_injury_event(self) -> Injury | None:
        """Create an injury event."""
        team = self.rng.choice([self.home_team, self.away_team])
        
        # Filter out already injured players
        available_players = [p for p in team.players if not p.injured]
        if not available_players:
            return None
            
        player = self.rng.choice(available_players)
        
        # Determine injury type and severity
        injury_types = [
            "Muscle strain", "Ankle sprain", "Knee injury", "Hamstring pull",
            "Shoulder injury", "Back strain", "Concussion", "Bruised ribs"
        ]
        injury_type = self.rng.choice(injury_types)
        
        # Determine severity based on random chance
        severity_roll = self.rng.random()
        if severity_roll < 0.6:
            severity = "minor"
            weeks_out = self.rng.randint(1, 2)
        elif severity_roll < 0.9:
            severity = "moderate" 
            weeks_out = self.rng.randint(3, 6)
        else:
            severity = "severe"
            weeks_out = self.rng.randint(7, 16)
        
        # Apply injury to player
        player.injured = True
        player.injury_weeks_remaining = weeks_out
        
        return Injury(
            match_id=self.match.id,
            minute=self.match.minute,
            home_score=self.match.home_score,
            away_score=self.match.away_score,
            player=player.name,
            team=team.id,
            injury_type=injury_type,
            severity=severity,
            weeks_out=weeks_out
        )

    def _calculate_team_strength(self, team: Team) -> float:
        """Calculate overall team strength for goal probability."""
        if not team.players:
            return 1.0

        # Simple average of key attacking attributes using age-modified stats
        total_strength = 0.0
        for player in team.players:
            # Use age-modified attributes for more realistic calculations
            attrs = player.age_modified_attributes
            
            # Weight attacking attributes more for goal probability
            strength = (
                attrs["shooting"] * 0.4 +
                attrs["pace"] * 0.2 +
                attrs["passing"] * 0.2 +
                attrs["physicality"] * 0.1 +
                player.form * 0.1  # Soft state influence
            )
            total_strength += strength

        return total_strength / len(team.players)
    
    def _track_shot_attempt(self) -> None:
        """Track a shot attempt that doesn't result in a notable event."""
        home_strength = self._calculate_team_strength(self.home_team)
        away_strength = self._calculate_team_strength(self.away_team)
        total_strength = home_strength + away_strength
        
        if self.rng.random() < (home_strength / total_strength):
            self._home_shots += 1
            # 50% chance shot is on target
            if self.rng.random() < 0.5:
                self._home_shots_on_target += 1
        else:
            self._away_shots += 1
            # 50% chance shot is on target
            if self.rng.random() < 0.5:
                self._away_shots_on_target += 1
    
    def _track_possession_minute(self) -> None:
        """Track which team has possession this minute based on team strength."""
        home_strength = self._calculate_team_strength(self.home_team)
        away_strength = self._calculate_team_strength(self.away_team)
        total_strength = home_strength + away_strength
        
        # Determine possession for this minute
        if self.rng.random() < (home_strength / total_strength):
            self._possession_minutes["home"] += 1
        else:
            self._possession_minutes["away"] += 1
    
    def _create_corner_event(self) -> CornerKick:
        """Create a corner kick event."""
        # Choose which team gets the corner based on attacking strength
        home_strength = self._calculate_team_strength(self.home_team)
        away_strength = self._calculate_team_strength(self.away_team)
        total_strength = home_strength + away_strength
        
        if self.rng.random() < (home_strength / total_strength):
            attacking_team = self.home_team
            self._home_corners += 1
        else:
            attacking_team = self.away_team
            self._away_corners += 1
        
        return CornerKick(
            match_id=self.match.id,
            minute=self.match.minute,
            home_score=self.match.home_score,
            away_score=self.match.away_score,
            team=attacking_team.id
        )
    
    def _create_foul_event(self) -> Foul:
        """Create a foul event."""
        # Choose which team commits the foul (defending team more likely)
        home_strength = self._calculate_team_strength(self.home_team)
        away_strength = self._calculate_team_strength(self.away_team)
        total_strength = home_strength + away_strength
        
        # Weaker team more likely to foul (inverse of attacking strength)
        if self.rng.random() < (away_strength / total_strength):
            fouling_team = self.home_team
            self._home_fouls += 1
        else:
            fouling_team = self.away_team
            self._away_fouls += 1
        
        # Choose a random player from the fouling team
        player = self.rng.choice(fouling_team.players)
        
        foul_types = ["regular", "dangerous", "professional"]
        foul_type = self.rng.choice(foul_types)
        
        return Foul(
            match_id=self.match.id,
            minute=self.match.minute,
            home_score=self.match.home_score,
            away_score=self.match.away_score,
            player=player.name,
            team=fouling_team.id,
            foul_type=foul_type
        )
    
    def _create_penalty_event(self) -> list[MatchEvent]:
        """Create a penalty kick event (award + goal/miss)."""
        # Choose which team gets the penalty based on attacking strength
        home_strength = self._calculate_team_strength(self.home_team)
        away_strength = self._calculate_team_strength(self.away_team)
        total_strength = home_strength + away_strength
        
        if self.rng.random() < (home_strength / total_strength):
            attacking_team = self.home_team
            defending_team = self.away_team
            self._home_penalties += 1
        else:
            attacking_team = self.away_team
            defending_team = self.home_team
            self._away_penalties += 1
        
        events = []
        
        # Penalty awarded event
        reasons = [
            "Foul in the box",
            "Handball",
            "Tripping an attacker",
            "Dangerous play in the box"
        ]
        reason = self.rng.choice(reasons)
        
        events.append(PenaltyAwarded(
            match_id=self.match.id,
            minute=self.match.minute,
            home_score=self.match.home_score,
            away_score=self.match.away_score,
            team=attacking_team.id,
            reason=reason
        ))
        
        # 75% chance to score penalty
        if self.rng.random() < 0.75:
            # Choose penalty taker (usually a striker or attacking midfielder)
            attackers = [
                p for p in attacking_team.players
                if p.position in [Position.ST, Position.CAM]
            ]
            if not attackers:
                attackers = [
                    p for p in attacking_team.players if p.position != Position.GK
                ]
            
            scorer = self.rng.choice(attackers) if attackers else attacking_team.players[0]
            
            # Update score
            if attacking_team.id == self.home_team.id:
                self.match.home_score += 1
                self._home_shots += 1
                self._home_shots_on_target += 1
            else:
                self.match.away_score += 1
                self._away_shots += 1
                self._away_shots_on_target += 1
            
            # Goal from penalty
            events.append(Goal(
                match_id=self.match.id,
                minute=self.match.minute,
                home_score=self.match.home_score,
                away_score=self.match.away_score,
                scorer=scorer.name,
                team=attacking_team.id,
                assist=None,
                penalty=True
            ))
        
        return events


class MatchEngine:
    """Orchestrates match simulation and event handling."""

    def __init__(self, world: GameWorld) -> None:
        self.world = world

    def simulate_match(
        self, match_id: str, seed: int | None = None
    ) -> list[MatchEvent]:
        """Simulate a complete match and return all events."""
        match = self.world.get_match_by_id(match_id)
        if not match:
            raise ValueError(f"Match {match_id} not found")

        simulator = MatchSimulator(self.world, match, seed)
        events = list(simulator.simulate())

        # Update team statistics
        self._update_team_stats(match)
        
        # Update player form based on match performance
        self._update_player_form_after_match(events, match)
        
        # Update match-based progression (fitness costs, suspension countdown)
        self.world.advance_match_progression(events)

        return events

    def _update_team_stats(self, match: Match) -> None:
        """Update team statistics after a match."""
        home_team = self.world.get_team_by_id(match.home_team_id)
        away_team = self.world.get_team_by_id(match.away_team_id)

        if not home_team or not away_team:
            return

        # Update match counts
        home_team.matches_played += 1
        away_team.matches_played += 1

        # Update goals
        home_team.goals_for += match.home_score
        home_team.goals_against += match.away_score
        away_team.goals_for += match.away_score
        away_team.goals_against += match.home_score
        
        # Track clean sheets
        if match.away_score == 0:
            home_team.clean_sheets += 1
        if match.home_score == 0:
            away_team.clean_sheets += 1

        # Update win/draw/loss records (overall and home/away)
        if match.home_score > match.away_score:
            home_team.wins += 1
            home_team.home_wins += 1
            away_team.losses += 1
            away_team.away_losses += 1
            # Update streaks
            self._update_streak(home_team, result="win")
            self._update_streak(away_team, result="loss")
        elif match.away_score > match.home_score:
            away_team.wins += 1
            away_team.away_wins += 1
            home_team.losses += 1
            home_team.home_losses += 1
            # Update streaks
            self._update_streak(away_team, result="win")
            self._update_streak(home_team, result="loss")
        else:
            home_team.draws += 1
            home_team.home_draws += 1
            away_team.draws += 1
            away_team.away_draws += 1
            # Update streaks
            self._update_streak(home_team, result="draw")
            self._update_streak(away_team, result="draw")
    
    def _update_streak(self, team: Team, result: str) -> None:
        """Update team's current and longest streaks."""
        if result == "win":
            if team.current_streak >= 0:
                # Continue or start winning streak
                team.current_streak += 1
            else:
                # End losing streak, start winning streak
                team.current_streak = 1
            
            # Update longest winning streak if needed
            if team.current_streak > team.longest_winning_streak:
                team.longest_winning_streak = team.current_streak
        
        elif result == "loss":
            if team.current_streak <= 0:
                # Continue or start losing streak
                team.current_streak -= 1
            else:
                # End winning streak, start losing streak
                team.current_streak = -1
            
            # Update longest losing streak if needed
            if abs(team.current_streak) > team.longest_losing_streak:
                team.longest_losing_streak = abs(team.current_streak)
        
        else:  # draw
            # Draw ends any streak
            team.current_streak = 0

    def _update_player_form_after_match(self, events: list, match: Match) -> None:
        """Update player form based on match performance."""
        import random
        
        home_team = self.world.get_team_by_id(match.home_team_id)
        away_team = self.world.get_team_by_id(match.away_team_id)
        
        if not home_team or not away_team:
            return
        
        # Track player performances
        player_stats = {}
        
        # Initialize all players
        for team in [home_team, away_team]:
            for player in team.players:
                player_stats[player.name] = {
                    'player': player,
                    'goals': 0,
                    'assists': 0,
                    'yellow_cards': 0,
                    'red_cards': 0,
                    'team_won': False,
                    'team_drew': False
                }
        
        # Set team result for all players
        home_won = match.home_score > match.away_score
        away_won = match.away_score > match.home_score
        draw = match.home_score == match.away_score
        
        for player in home_team.players:
            if player.name in player_stats:
                player_stats[player.name]['team_won'] = home_won
                player_stats[player.name]['team_drew'] = draw
                
        for player in away_team.players:
            if player.name in player_stats:
                player_stats[player.name]['team_won'] = away_won  
                player_stats[player.name]['team_drew'] = draw
        
        # Process match events
        for event in events:
            if hasattr(event, 'event_type'):
                if event.event_type == "Goal":
                    scorer_name = getattr(event, 'scorer', None)
                    assist_name = getattr(event, 'assist', None)
                    
                    if scorer_name and scorer_name in player_stats:
                        player_stats[scorer_name]['goals'] += 1
                    
                    if assist_name and assist_name in player_stats:
                        player_stats[assist_name]['assists'] += 1
                        
                elif event.event_type == "YellowCard":
                    player_name = getattr(event, 'player', None)
                    if player_name and player_name in player_stats:
                        player_stats[player_name]['yellow_cards'] += 1
                        
                elif event.event_type == "RedCard":
                    player_name = getattr(event, 'player', None)
                    if player_name and player_name in player_stats:
                        player_stats[player_name]['red_cards'] += 1
        
        # Update player form based on performance
        rng = random.Random(42)  # Use fixed seed for consistency
        
        for player_name, stats in player_stats.items():
            player = stats['player']
            form_change = 0
            
            # Positive form changes
            form_change += stats['goals'] * 3  # +3 per goal
            form_change += stats['assists'] * 2  # +2 per assist
            
            if stats['team_won']:
                form_change += 1  # +1 for team win
            elif stats['team_drew']:
                form_change += 0  # Neutral for draw
            else:
                form_change -= 1  # -1 for team loss
            
            # Negative form changes  
            form_change -= stats['yellow_cards'] * 1  # -1 per yellow card
            form_change -= stats['red_cards'] * 3  # -3 per red card
            
            # Add some randomness (small chance of form change regardless of performance)
            random_factor = rng.randint(-1, 1)  # -1, 0, or +1
            form_change += random_factor
            
            # Apply form change with bounds
            new_form = max(1, min(100, player.form + form_change))
            player.form = new_form
