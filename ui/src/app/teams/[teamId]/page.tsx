'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import axios from 'axios';
import { TeamDetail, TeamMatchesResponse, WorldState, TeamHistoryResponse } from '@/types/api';
import TeamLink from '@/components/TeamLink';
import { getTeamReputationLevel, getPlayerReputationLevel, getReputationColor } from '@/utils/reputationUtils';
import { formatCurrency, formatPercentage, formatCapacity } from '@/utils/formatUtils';

interface TeamPageProps {
  params: Promise<{
    teamId: string;
  }>;
}

export default function TeamPage({ params }: TeamPageProps) {
  const [teamId, setTeamId] = useState<string>('');
  
  const [teamDetail, setTeamDetail] = useState<TeamDetail | null>(null);
  const [teamMatches, setTeamMatches] = useState<TeamMatchesResponse | null>(null);
  const [teamHistory, setTeamHistory] = useState<TeamHistoryResponse | null>(null);
  const [worldState, setWorldState] = useState<WorldState | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    // Resolve the params Promise and get teamId
    params.then(({ teamId: resolvedTeamId }) => {
      setTeamId(resolvedTeamId);
    });
  }, [params]);

  useEffect(() => {
    if (teamId) {
      loadTeamData();
    }
  }, [teamId]);

  const loadTeamData = useCallback(async (): Promise<void> => {
    try {
      setIsLoading(true);
      
      // First try to load team directly by ID
      let actualTeamId = teamId;
      
      try {
        const teamResponse = await axios.get<TeamDetail>(`/api/teams/${teamId}`);
        setTeamDetail(teamResponse.data);
      } catch (error: unknown) {
        if (error && typeof error === 'object' && 'response' in error) {
          const axiosError = error as { response?: { status?: number } };
          if (axiosError.response?.status === 404) {
            // Try to lookup team by name (convert from URL format)
            const teamName = teamId.replace(/_/g, ' ');
            try {
              const lookupResponse = await axios.get(`/api/teams/lookup/${encodeURIComponent(teamName)}`);
              actualTeamId = lookupResponse.data.team_id;
              const teamResponse = await axios.get<TeamDetail>(`/api/teams/${actualTeamId}`);
              setTeamDetail(teamResponse.data);
            } catch {
              throw new Error('Team not found');
            }
          } else {
            throw error;
          }
        }
      }
      
      // Load team matches, history and world state in parallel
      const [matchesResponse, historyResponse, worldResponse] = await Promise.all([
        axios.get<TeamMatchesResponse>(`/api/teams/${actualTeamId}/matches?limit=10`),
        axios.get<TeamHistoryResponse>(`/api/teams/${actualTeamId}/history?limit=10`),
        axios.get<WorldState>('/api/world')
      ]);
      
      setTeamMatches(matchesResponse.data);
      setTeamHistory(historyResponse.data);
      setWorldState(worldResponse.data);
    } catch (error) {
      console.error('Failed to load team data:', error);
      setError('Failed to load team data');
    } finally {
      setIsLoading(false);
    }
  }, [teamId]);

  const getPositionColor = (position: string): string => {
    switch (position) {
      case 'GK': return '#e74c3c';
      case 'CB': case 'LB': case 'RB': return '#3498db';
      case 'CM': case 'LM': case 'RM': case 'CAM': return '#f39c12';
      case 'LW': case 'RW': case 'ST': return '#2ecc71';
      default: return '#95a5a6';
    }
  };

  const getPlayerFormColor = (form: number): string => {
    if (form >= 80) return '#2ecc71'; // Green
    if (form >= 60) return '#f39c12'; // Orange
    if (form >= 40) return '#e67e22'; // Dark orange
    return '#e74c3c'; // Red
  };

  if (isLoading) {
    return (
      <div className="app">
        <div className="loading">Loading team data...</div>
      </div>
    );
  }

  if (error || !teamDetail) {
    return (
      <div className="app">
        <div className="error">
          <h2>Error</h2>
          <p>{error || 'Team not found'}</p>
          <Link href="/" className="back-button">← Back to Home</Link>
        </div>
      </div>
    );
  }

  // Find the team's league and position in table
  const teamLeague = worldState?.leagues[teamDetail.league];
  const teamPosition = teamLeague?.table.find(entry => entry.team === teamDetail.name)?.position;

  return (
    <div className="app">
      <header className="header">
        <h1>⚽ {teamDetail.name}</h1>
        <p>
          {teamLeague?.name} {teamPosition ? `- Position ${teamPosition}` : ''}
          {' '}• <span 
            style={{ 
              color: getReputationColor(teamDetail.reputation),
              fontWeight: 'bold'
            }}
          >
            {getTeamReputationLevel(teamDetail.reputation).label} Club
          </span>
        </p>
      </header>

      <div className="team-nav">
        <Link href="/" className="back-button">← Back to Home</Link>
      </div>

      <div className="team-content">
        {/* Team Stats Panel */}
        <div className="panel">
          <h2>Team Statistics</h2>
          <div className="team-stats">
            <div className="stat-row">
              <span className="stat-label">Matches Played:</span>
              <span className="stat-value">{teamDetail.matches_played}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Record:</span>
              <span className="stat-value">{teamDetail.wins}W - {teamDetail.draws}D - {teamDetail.losses}L</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Goals:</span>
              <span className="stat-value">{teamDetail.goals_for} for, {teamDetail.goals_against} against ({teamDetail.goal_difference > 0 ? '+' : ''}{teamDetail.goal_difference})</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Points:</span>
              <span className="stat-value"><strong>{teamDetail.points}</strong></span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Team Morale:</span>
              <span className="stat-value">{teamDetail.team_morale}/100</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Tactical Familiarity:</span>
              <span className="stat-value">{teamDetail.tactical_familiarity}/100</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Club Reputation:</span>
              <span 
                className="stat-value"
                style={{ 
                  color: getReputationColor(teamDetail.reputation),
                  fontWeight: 'bold'
                }}
              >
                {getTeamReputationLevel(teamDetail.reputation).label}
              </span>
            </div>
          </div>
        </div>

        {/* Club Finances Panel */}
        <div className="panel">
          <h2>Club Finances</h2>
          <div className="team-stats">
            <div className="stat-row">
              <span className="stat-label">Current Balance:</span>
              <span className="stat-value">{formatCurrency(teamDetail.balance)}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Initial Balance:</span>
              <span className="stat-value">{formatCurrency(teamDetail.initial_balance)}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Owner Investment:</span>
              <span className="stat-value">{formatCurrency(teamDetail.owner_investment)}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Monthly Wage Costs:</span>
              <span className="stat-value">{formatCurrency(teamDetail.monthly_wage_costs)}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Monthly Stadium Costs:</span>
              <span className="stat-value">{formatCurrency(teamDetail.monthly_stadium_costs)}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Monthly Facilities Costs:</span>
              <span className="stat-value">{formatCurrency(teamDetail.monthly_facilities_costs)}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Total Monthly Costs:</span>
              <span className="stat-value"><strong>{formatCurrency(teamDetail.monthly_total_costs)}</strong></span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Season Ticket Revenue:</span>
              <span className="stat-value">{formatCurrency(teamDetail.season_ticket_revenue)}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Matchday Revenue (per game):</span>
              <span className="stat-value">{formatCurrency(teamDetail.matchday_revenue_per_game)}</span>
            </div>
          </div>
        </div>

        {/* Stadium & Facilities Panel */}
        <div className="panel">
          <h2>Stadium & Facilities</h2>
          <div className="team-stats">
            <div className="stat-row">
              <span className="stat-label">Stadium Name:</span>
              <span className="stat-value">{teamDetail.stadium_name}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Stadium Capacity:</span>
              <span className="stat-value">{teamDetail.stadium_capacity.toLocaleString()}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Stadium Utilization:</span>
              <span className="stat-value">{formatPercentage(teamDetail.stadium_utilization)}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Training Facilities Quality:</span>
              <span className="stat-value">{teamDetail.training_facilities_quality}/100</span>
            </div>
          </div>
        </div>

        {/* Fanbase Panel */}
        <div className="panel">
          <h2>Fanbase</h2>
          <div className="team-stats">
            <div className="stat-row">
              <span className="stat-label">Total Fanbase:</span>
              <span className="stat-value">{teamDetail.fanbase_size.toLocaleString()}</span>
            </div>
            <div className="stat-row">
              <span className="stat-label">Season Ticket Holders:</span>
              <span className="stat-value">{formatCapacity(teamDetail.season_ticket_holders, teamDetail.stadium_capacity)}</span>
            </div>
          </div>
        </div>

        {/* Players Panel */}
        <div className="panel">
          <h2>Squad ({teamDetail.players.length} players)</h2>
          <div className="players-list">
            {teamDetail.players
              .sort((a, b) => b.overall_rating - a.overall_rating)
              .map((player) => (
                <div key={player.id} className="player-card">
                  <div className="player-header">
                    <span 
                      className="player-position" 
                      style={{ backgroundColor: getPositionColor(player.position) }}
                    >
                      {player.position}
                    </span>
                    <Link href={`/players/${player.id}`} className="player-name-link">
                      {player.name}
                    </Link>
                    <span className="player-age">({player.age})</span>
                    <span className="player-overall">{player.overall_rating}</span>
                  </div>
                  <div className="player-stats">
                    <div className="stat-group">
                      <span>PAC: {player.pace}</span>
                      <span>SHO: {player.shooting}</span>
                      <span>PAS: {player.passing}</span>
                      <span>DEF: {player.defending}</span>
                      <span>PHY: {player.physicality}</span>
                    </div>
                    <div className="player-condition">
                      <span 
                        className="form-indicator"
                        style={{ color: getPlayerFormColor(player.form) }}
                      >
                        Form: {player.form}
                      </span>
                      <span>Fitness: {player.fitness}</span>
                      <span>Morale: {player.morale}</span>
                      <span 
                        className="reputation-indicator"
                        style={{ 
                          color: getReputationColor(player.reputation),
                          fontSize: '0.8em'
                        }}
                      >
                        {getPlayerReputationLevel(player.reputation).label}
                      </span>
                      {player.injured && <span className="injured">🏥 INJURED</span>}
                      {player.yellow_cards > 0 && <span className="cards">🟨 {player.yellow_cards}</span>}
                      {player.red_cards > 0 && <span className="cards">🟥 {player.red_cards}</span>}
                    </div>
                    <div className="player-contract">
                      <span className="contract-years">
                        Contract: {player.contract_years_remaining}yr{player.contract_years_remaining !== 1 ? 's' : ''}
                      </span>
                      <span className="salary">
                        Salary: {formatCurrency(player.salary)}
                      </span>
                      <span className="market-value">
                        Value: {formatCurrency(player.market_value)}
                      </span>
                    </div>
                  </div>
                </div>
              ))}
          </div>
        </div>

        {/* Recent Matches Panel */}
        <div className="panel">
          <h2>Recent Matches</h2>
          {teamMatches && teamMatches.matches.length > 0 ? (
            <div className="matches-list">
              {teamMatches.matches.map((match) => (
                <Link 
                  key={match.id} 
                  href={`/matches/${match.id}`}
                  className="match-item"
                >
                  <div className="match-teams">
                    <span className={match.is_home ? 'home-team' : ''}>{match.home_team}</span>
                    <span className="score">{match.home_score} - {match.away_score}</span>
                    <span className={!match.is_home ? 'away-team' : ''}>{match.away_team}</span>
                  </div>
                  <div className="match-info">
                    {match.league} - MD{match.matchday} (S{match.season})
                  </div>
                </Link>
              ))}
            </div>
          ) : (
            <div>No matches found for this team.</div>
          )}
        </div>

        {/* Club Ownership Panel */}
        <div className="panel">
          <h2>Club Ownership</h2>
          {teamDetail.club_owners && teamDetail.club_owners.length > 0 ? (
            <div className="ownership-list">
              {teamDetail.club_owners.map((owner) => (
                <div key={owner.id} className="owner-card">
                  <div className="owner-header">
                    <h3>{owner.name}</h3>
                    <span className="owner-role">{owner.role}</span>
                  </div>
                  <div className="owner-details">
                    <div className="owner-stats">
                      <div className="stat-row">
                        <span className="stat-label">Wealth:</span>
                        <span className="stat-value">{owner.wealth}/100</span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">Business Acumen:</span>
                        <span className="stat-value">{owner.business_acumen}/100</span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">Ambition:</span>
                        <span className="stat-value">{owner.ambition}/100</span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">Patience:</span>
                        <span className="stat-value">{owner.patience}/100</span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">Public Approval:</span>
                        <span className="stat-value">{owner.public_approval}/100</span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">Years at Club:</span>
                        <span className="stat-value">{owner.years_at_club}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div>No ownership information available.</div>
          )}
        </div>

        {/* Staff Members Panel */}
        <div className="panel">
          <h2>Staff Members</h2>
          {teamDetail.staff_members && teamDetail.staff_members.length > 0 ? (
            <div className="staff-list">
              {teamDetail.staff_members.map((staff) => (
                <div key={staff.id} className="staff-card">
                  <div className="staff-header">
                    <h3>{staff.name}</h3>
                    <span className="staff-role">{staff.role}</span>
                  </div>
                  <div className="staff-details">
                    <div className="staff-stats">
                      <div className="stat-row">
                        <span className="stat-label">Experience:</span>
                        <span className="stat-value">{staff.experience}/100</span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">Specialization:</span>
                        <span className="stat-value">{staff.specialization}/100</span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">Morale:</span>
                        <span className="stat-value">{staff.morale}/100</span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">Team Rapport:</span>
                        <span className="stat-value">{staff.team_rapport}/100</span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">Contract:</span>
                        <span className="stat-value">{staff.contract_years_remaining} years</span>
                      </div>
                      <div className="stat-row">
                        <span className="stat-label">Salary:</span>
                        <span className="stat-value">£{staff.salary.toLocaleString()}</span>
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div>No staff information available.</div>
          )}
        </div>

        {/* Team History Panel */}
        <div className="panel">
          <h2>Recent History</h2>
          {teamHistory && teamHistory.events.length > 0 ? (
            <div className="history-list">
              {teamHistory.events.map((event) => (
                <div key={event.id} className="history-event">
                  <div className="event-timestamp">
                    {new Date(event.timestamp).toLocaleDateString()}
                  </div>
                  <div className="event-description">
                    <span className={`event-type-${event.event_type.toLowerCase()}`}>
                      {event.event_type}
                    </span>
                    <span className="event-text">{event.description}</span>
                  </div>
                </div>
              ))}
            </div>
          ) : (
            <div>No recent history available.</div>
          )}
        </div>

        {/* League Table Panel */}
        {teamLeague && (
          <div className="panel">
            <h2>League Table - {teamLeague.name}</h2>
            <table className="league-table">
              <thead>
                <tr>
                  <th className="number">Pos</th>
                  <th>Team</th>
                  <th className="number">P</th>
                  <th className="number">W</th>
                  <th className="number">D</th>
                  <th className="number">L</th>
                  <th className="number">GF</th>
                  <th className="number">GA</th>
                  <th className="number">GD</th>
                  <th className="number">Pts</th>
                </tr>
              </thead>
              <tbody>
                {teamLeague.table.map((team) => (
                  <tr 
                    key={team.position}
                    className={team.team === teamDetail.name ? 'highlighted-team' : ''}
                  >
                    <td className="number">{team.position}</td>
                    <td>
                      {team.team === teamDetail.name ? (
                        <strong>{team.team}</strong>
                      ) : (
                        <TeamLink teamName={team.team} />
                      )}
                    </td>
                    <td className="number">{team.played}</td>
                    <td className="number">{team.won}</td>
                    <td className="number">{team.drawn}</td>
                    <td className="number">{team.lost}</td>
                    <td className="number">{team.goals_for}</td>
                    <td className="number">{team.goals_against}</td>
                    <td className="number">{team.goal_difference}</td>
                    <td className="number"><strong>{team.points}</strong></td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </div>
    </div>
  );
}