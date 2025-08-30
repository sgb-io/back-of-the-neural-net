// API Response Types for Back of the Neural Net

export interface TeamTableEntry {
  position: number;
  team: string;
  played: number;
  won: number;
  drawn: number;
  lost: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
}

export interface League {
  name: string;
  current_matchday: number;
  table: TeamTableEntry[];
}

export interface Fixture {
  id: string;
  home_team: string;
  away_team: string;
  league: string;
  matchday: number;
}

export interface WorldState {
  leagues: Record<string, League>;
  next_fixtures: Fixture[];
}

// Match Event Types
export interface BaseEvent {
  minute: number;
  event_type: string;
  team: string;
}

export interface GoalEvent extends BaseEvent {
  event_type: 'Goal';
  scorer: string;
  assist?: string;
}

export interface CardEvent extends BaseEvent {
  event_type: 'YellowCard' | 'RedCard';
  player: string;
  reason: string;
}

export interface SubstitutionEvent extends BaseEvent {
  event_type: 'Substitution';
  player_off: string;
  player_on: string;
}

export interface MatchEndedEvent extends BaseEvent {
  event_type: 'MatchEnded';
  home_team: string;
  away_team: string;
  home_score: number;
  away_score: number;
}

export interface KickOffEvent extends BaseEvent {
  event_type: 'KickOff';
}

export interface UnknownEvent extends BaseEvent {
  event_type: string;
  [key: string]: unknown;
}

export type MatchEvent = GoalEvent | CardEvent | SubstitutionEvent | MatchEndedEvent | KickOffEvent | UnknownEvent;

// API Response Types
export interface AdvanceResponse {
  status: 'matches_completed' | 'matchday_advanced';
  matches_played?: number;
  events?: MatchEvent[];
}