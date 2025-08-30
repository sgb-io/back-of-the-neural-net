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

export interface CompletedMatch {
  id: string;
  home_team: string;
  away_team: string;
  league: string;
  matchday: number;
  season: number;
  home_score: number;
  away_score: number;
  finished: boolean;
  is_home?: boolean; // For team-specific matches
}

export interface Player {
  id: string;
  name: string;
  position: string;
  age: number;
  overall_rating: number;
  pace: number;
  shooting: number;
  passing: number;
  defending: number;
  physicality: number;
  form: number;
  morale: number;
  fitness: number;
  injured: boolean;
  yellow_cards: number;
  red_cards: number;
}

export interface TeamDetail {
  id: string;
  name: string;
  league: string;
  team_morale: number;
  tactical_familiarity: number;
  matches_played: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
  players: Player[];
}

export interface TeamMatchesResponse {
  team_id: string;
  team_name: string;
  matches: CompletedMatch[];
}

export interface TeamLookupResponse {
  team_id: string;
  team_name: string;
  league: string;
}

export interface MatchEventDetail {
  event_type: string;
  timestamp: string;
  minute?: number;
  team?: string;
  player?: string;
  scorer?: string;
  assist?: string;
  player_off?: string;
  player_on?: string;
  reason?: string;
  home_team?: string;
  away_team?: string;
  home_score?: number;
  away_score?: number;
}

export interface MatchDetail {
  match_id: string;
  match: CompletedMatch;
  events: MatchEventDetail[];
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