"""Deterministic match simulation engine."""

import random
from collections.abc import Generator

from .entities import GameWorld, Match, Position, Team
from .events import (
    Goal,
    KickOff,
    MatchEnded,
    MatchEvent,
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

            # Check for events this minute
            events = self._simulate_minute()
            yield from events

        # Mark match as finished
        self.match.finished = True

        # Final match result
        yield MatchEnded(
            match_id=self.match.id,
            home_team=self.home_team.id,
            away_team=self.away_team.id,
            home_score=self.match.home_score,
            away_score=self.match.away_score,
            duration_minutes=90
        )

    def _simulate_minute(self) -> list[MatchEvent]:
        """Simulate events that might occur in a single minute."""
        events = []

        # Basic probability of something happening each minute
        if self.rng.random() < 0.1:  # 10% chance per minute
            event_type = self._choose_event_type()
            event = self._create_event(event_type)
            if event:
                events.append(event)

        return events

    def _choose_event_type(self) -> str:
        """Choose what type of event occurs based on probabilities."""
        # Simple weighted random selection
        choices = [
            ("goal", 0.02),      # ~1.8 goals per match on average
            ("yellow_card", 0.04), # ~3.6 yellow cards per match
            ("red_card", 0.002),   # ~0.18 red cards per match
            ("substitution", 0.01), # Limited substitutions
        ]

        total_weight = sum(weight for _, weight in choices)
        r = self.rng.random() * total_weight

        cumulative = 0.0
        for event_type, weight in choices:
            cumulative += weight
            if r <= cumulative:
                return event_type

        return "goal"  # Default fallback

    def _create_event(self, event_type: str) -> MatchEvent | None:
        """Create a specific type of match event."""
        if event_type == "goal":
            return self._create_goal_event()
        elif event_type == "yellow_card":
            return self._create_yellow_card_event()
        elif event_type == "red_card":
            return self._create_red_card_event()
        elif event_type == "substitution":
            return self._create_substitution_event()

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
        else:
            scoring_team = self.away_team
            self.match.away_score += 1

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

        # Update player's red card count
        player.red_cards += 1

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

    def _calculate_team_strength(self, team: Team) -> float:
        """Calculate overall team strength for goal probability."""
        if not team.players:
            return 1.0

        # Simple average of key attacking attributes
        total_strength = 0.0
        for player in team.players:
            # Weight attacking attributes more for goal probability
            strength = (
                player.shooting * 0.4 +
                player.pace * 0.2 +
                player.passing * 0.2 +
                player.physicality * 0.1 +
                player.form * 0.1  # Soft state influence
            )
            total_strength += strength

        return total_strength / len(team.players)


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

        # Update win/draw/loss records
        if match.home_score > match.away_score:
            home_team.wins += 1
            away_team.losses += 1
        elif match.away_score > match.home_score:
            away_team.wins += 1
            home_team.losses += 1
        else:
            home_team.draws += 1
            away_team.draws += 1
