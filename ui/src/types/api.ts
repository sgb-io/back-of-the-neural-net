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

export interface MatchPrediction {
  home_team: string;
  away_team: string;
  win_probabilities: {
    home_win: number;
    draw: number;
    away_win: number;
  };
  predicted_score: {
    home_goals: number;
    away_goals: number;
  };
  factors: {
    home_strength: number;
    away_strength: number;
    home_form: number;
    away_form: number;
  };
}

export interface MediaPreview {
  headline: string;
  preview: string;
  source: string;
  importance: string;
}

export interface Fixture {
  id: string;
  home_team: string;
  away_team: string;
  home_team_id?: string;
  away_team_id?: string;
  league: string;
  matchday: number;
  finished?: boolean;
  home_score?: number | null;
  away_score?: number | null;
  prediction?: MatchPrediction | null;
  importance?: string;
  media_preview?: MediaPreview | null;
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
  reputation: number;
  injured: boolean;
  yellow_cards: number;
  red_cards: number;
}

export interface ClubOwner {
  id: string;
  name: string;
  role: string;
  wealth: number;
  business_acumen: number;
  ambition: number;
  patience: number;
  public_approval: number;
  years_at_club: number;
}

export interface StaffMember {
  id: string;
  name: string;
  role: string;
  experience: number;
  specialization: number;
  morale: number;
  team_rapport: number;
  contract_years_remaining: number;
  salary: number;
}

export interface TeamHistoryEvent {
  id: string;
  timestamp: string;
  event_type: string;
  description: string;
  statement_type?: string;
  message?: string;
  public_reaction?: number;
  headline?: string;
  story_type?: string;
  sentiment?: number;
  home_team?: string;
  away_team?: string;
  home_score?: number;
  away_score?: number;
}

export interface TeamHistoryResponse {
  team_id: string;
  team_name: string;
  events: TeamHistoryEvent[];
  total: number;
}

export interface TeamDetail {
  id: string;
  name: string;
  league: string;
  team_morale: number;
  tactical_familiarity: number;
  reputation: number;
  matches_played: number;
  wins: number;
  draws: number;
  losses: number;
  goals_for: number;
  goals_against: number;
  goal_difference: number;
  points: number;
  // Financial information
  balance: number;
  initial_balance: number;
  owner_investment: number;
  monthly_wage_costs: number;
  monthly_stadium_costs: number;
  monthly_facilities_costs: number;
  monthly_total_costs: number;
  season_ticket_revenue: number;
  matchday_revenue_per_game: number;
  // Stadium and facilities
  stadium_name: string;
  stadium_capacity: number;
  training_facilities_quality: number;
  // Fanbase
  fanbase_size: number;
  season_ticket_holders: number;
  stadium_utilization: number;
  players: Player[];
  club_owners: ClubOwner[];
  staff_members: StaffMember[];
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

export interface PlayerLookupResponse {
  player_id: string;
  player_name: string;
  position: string;
}

export interface PlayerSeasonStats {
  goals: number;
  assists: number;
  yellow_cards: number;
  red_cards: number;
  matches_played: number;
  minutes_played: number;
}

export interface PlayerCurrentTeam {
  id: string;
  name: string;
  league: string;
}

export interface PlayerDetail {
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
  reputation: number;
  injured: boolean;
  yellow_cards: number;
  red_cards: number;
  current_team: PlayerCurrentTeam;
  season_stats: PlayerSeasonStats;
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
  season: number;
  current_date: string;
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

// News Feed Types
export interface NewsReport {
  id: string;
  type: 'report';
  timestamp: string;
  headline: string;
  story_type: string;
  sentiment: number;
  outlet_name: string;
  teams_mentioned: string[];
}

export interface NewsMatch {
  id: string;
  type: 'upcoming_match';
  home_team: string;
  away_team: string;
  league: string;
  matchday: number;
  finished: boolean;
  prediction?: MatchPrediction | null;
  importance: string;
  media_preview?: MediaPreview | null;
}

export interface NewsLeague {
  recent_reports: NewsReport[];
  upcoming_matches: NewsMatch[];
}

export interface NewsResponse {
  news_by_league: Record<string, NewsLeague>;
}

// API Response Types
export interface AdvanceResponse {
  status: 'matches_completed' | 'matchday_advanced';
  matches_played?: number;
  events?: MatchEvent[];
}