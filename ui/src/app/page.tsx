'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { WorldState, MatchEvent, AdvanceResponse, League, CompletedMatch, MatchDetail, MatchEventDetail, Fixture } from '@/types/api';
import TeamLink from '@/components/TeamLink';

export default function Home() {
  const [worldState, setWorldState] = useState<WorldState | null>(null);
  const [isAdvancing, setIsAdvancing] = useState<boolean>(false);
  const [selectedLeague, setSelectedLeague] = useState<string>('');
  const [lastEvents, setLastEvents] = useState<MatchEvent[]>([]);
  const [status, setStatus] = useState<string>('');
  
  // New state for match browsing
  const [completedMatches, setCompletedMatches] = useState<CompletedMatch[]>([]);
  const [selectedMatch, setSelectedMatch] = useState<MatchDetail | null>(null);
  const [isLoadingMatches, setIsLoadingMatches] = useState<boolean>(false);
  const [isLoadingMatchDetail, setIsLoadingMatchDetail] = useState<boolean>(false);

  // New state for fixtures with predictions
  const [fixturesWithPredictions, setFixturesWithPredictions] = useState<Fixture[]>([]);
  const [isLoadingFixtures, setIsLoadingFixtures] = useState<boolean>(false);

  // Load initial world state
  useEffect(() => {
    loadWorldState();
    loadFixturesWithPredictions();
  }, []);

  // Set default league when world state loads
  useEffect(() => {
    if (worldState && worldState.leagues && !selectedLeague) {
      const firstLeague = Object.keys(worldState.leagues)[0];
      if (firstLeague) {
        setSelectedLeague(firstLeague);
      }
    }
  }, [worldState, selectedLeague]);

  const loadWorldState = async (): Promise<void> => {
    try {
      const response = await axios.get<WorldState>('/api/world');
      setWorldState(response.data);
    } catch (error) {
      console.error('Failed to load world state:', error);
      setStatus('Failed to load world state');
    }
  };

  const advanceSimulation = async (): Promise<void> => {
    setIsAdvancing(true);
    setStatus('Advancing simulation...');
    
    try {
      const response = await axios.post<AdvanceResponse>('/api/advance');
      setLastEvents(response.data.events || []);
      
      if (response.data.status === 'matches_completed') {
        setStatus(`Completed ${response.data.matches_played} matches`);
      } else if (response.data.status === 'matchday_advanced') {
        setStatus('Advanced to next matchday');
      }
      
      // Reload world state, completed matches, and fixtures
      await loadWorldState();
      await loadCompletedMatches();
      await loadFixturesWithPredictions();
    } catch (error) {
      console.error('Failed to advance simulation:', error);
      setStatus('Failed to advance simulation');
    } finally {
      setIsAdvancing(false);
    }
  };

  const formatEvent = (event: MatchEvent): string => {
    switch (event.event_type) {
      case 'Goal':
        return `⚽ ${event.minute}' GOAL! ${event.scorer} scores for ${event.team}${event.assist ? ` (assist: ${event.assist})` : ''}`;
      case 'YellowCard':
        return `🟨 ${event.minute}' Yellow card for ${event.player} (${event.team}) - ${event.reason}`;
      case 'RedCard':
        return `🟥 ${event.minute}' Red card for ${event.player} (${event.team}) - ${event.reason}`;
      case 'Substitution':
        return `🔄 ${event.minute}' Substitution (${event.team}): ${event.player_off} ➔ ${event.player_on}`;
      case 'MatchEnded':
        return `🏁 Full time: ${event.home_team} ${event.home_score} - ${event.away_score} ${event.away_team}`;
      case 'KickOff':
        return `⚽ Kick off!`;
      default:
        return `${event.event_type}: ${JSON.stringify(event, null, 2)}`;
    }
  };

  const formatMatchEvent = (event: MatchEventDetail): string => {
    switch (event.event_type) {
      case 'Goal':
        return `⚽ ${event.minute}' GOAL! ${event.scorer} scores for ${event.team}${event.assist ? ` (assist: ${event.assist})` : ''}`;
      case 'YellowCard':
        return `🟨 ${event.minute}' Yellow card for ${event.player} (${event.team}) - ${event.reason}`;
      case 'RedCard':
        return `🟥 ${event.minute}' Red card for ${event.player} (${event.team}) - ${event.reason}`;
      case 'Substitution':
        return `🔄 ${event.minute}' Substitution (${event.team}): ${event.player_off} ➔ ${event.player_on}`;
      case 'MatchEnded':
        return `🏁 Full time: ${event.home_team} ${event.home_score} - ${event.away_score} ${event.away_team}`;
      case 'MatchStarted':
        return `🟢 Match started: ${event.home_team} vs ${event.away_team}`;
      case 'KickOff':
        return `⚽ Kick off!`;
      default:
        return `${event.event_type}`;
    }
  };

  const loadCompletedMatches = async (): Promise<void> => {
    setIsLoadingMatches(true);
    try {
      const response = await axios.get<{matches: CompletedMatch[]}>('/api/matches?limit=20');
      setCompletedMatches(response.data.matches);
    } catch (error) {
      console.error('Failed to load completed matches:', error);
      setStatus('Failed to load completed matches');
    } finally {
      setIsLoadingMatches(false);
    }
  };

  const loadMatchDetail = async (matchId: string): Promise<void> => {
    setIsLoadingMatchDetail(true);
    try {
      const response = await axios.get<MatchDetail>(`/api/matches/${matchId}/events`);
      setSelectedMatch(response.data);
    } catch (error) {
      console.error('Failed to load match detail:', error);
      setStatus('Failed to load match detail');
    } finally {
      setIsLoadingMatchDetail(false);
    }
  };

  const loadFixturesWithPredictions = async (): Promise<void> => {
    setIsLoadingFixtures(true);
    try {
      const response = await axios.get<{fixtures: Fixture[]}>('/api/fixtures/predictions?limit=10');
      setFixturesWithPredictions(response.data.fixtures);
    } catch (error) {
      console.error('Failed to load fixtures with predictions:', error);
      setStatus('Failed to load fixtures with predictions');
    } finally {
      setIsLoadingFixtures(false);
    }
  };

  // Load completed matches when component mounts
  useEffect(() => {
    loadCompletedMatches();
  }, []);

  if (!worldState) {
    return (
      <div className="app">
        <div className="loading">Loading game world...</div>
      </div>
    );
  }

  const currentLeague: League | undefined = worldState.leagues[selectedLeague];

  return (
    <div className="app">
      <header className="header">
        <h1>⚽ Back of the Neural Net</h1>
        <p>Proper football. Artificial brains.</p>
      </header>

      <div className="controls">
        <button 
          className="advance-button" 
          onClick={advanceSimulation}
          disabled={isAdvancing}
        >
          {isAdvancing ? 'Advancing...' : 'Advance Simulation'}
        </button>
        {status && <div className="status">{status}</div>}
      </div>

      <div className="main-content">
        <div className="panel">
          <h2>League Tables</h2>
          
          <div className="league-selector">
            <select 
              value={selectedLeague} 
              onChange={(e) => setSelectedLeague(e.target.value)}
            >
              {Object.entries(worldState.leagues).map(([id, league]) => (
                <option key={id} value={id}>
                  {league.name} (Matchday {league.current_matchday})
                </option>
              ))}
            </select>
          </div>

          {currentLeague && (
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
                {currentLeague.table.map((team) => (
                  <tr key={team.position}>
                    <td className="number">{team.position}</td>
                    <td><TeamLink teamName={team.team} /></td>
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
          )}
        </div>

        <div className="panel">
          <h2>Next Fixtures</h2>
          <div className="fixtures-list">
            {isLoadingFixtures ? (
              <div>Loading fixtures...</div>
            ) : fixturesWithPredictions.length === 0 ? (
              <div>No more fixtures scheduled</div>
            ) : (
              fixturesWithPredictions.map((fixture) => (
                <div key={fixture.id} className={`fixture ${fixture.importance !== 'normal' ? 'important-fixture' : ''}`}>
                  <div className="fixture-teams">
                    <TeamLink teamName={fixture.home_team} /> vs <TeamLink teamName={fixture.away_team} />
                    {fixture.importance !== 'normal' && (
                      <span className={`importance-badge ${fixture.importance}`}>
                        {fixture.importance === 'title_race' ? '👑' : 
                         fixture.importance === 'derby' ? '⚔️' : 
                         fixture.importance === 'relegation' ? '🔻' : '⭐'}
                      </span>
                    )}
                  </div>
                  <div className="fixture-info">
                    {fixture.league} - MD{fixture.matchday}
                  </div>
                  {fixture.media_preview && (
                    <div className="media-preview">
                      <div className="media-headline">{fixture.media_preview.headline}</div>
                      <div className="media-content">{fixture.media_preview.preview}</div>
                      <div className="media-source">— {fixture.media_preview.source}</div>
                    </div>
                  )}
                  {fixture.prediction && (
                    <div className="fixture-prediction">
                      <div className="prediction-score">
                        Predicted: {fixture.prediction.predicted_score.home_goals} - {fixture.prediction.predicted_score.away_goals}
                      </div>
                      <div className="prediction-probabilities">
                        <span className="prob-home">{fixture.home_team} {fixture.prediction.win_probabilities.home_win}%</span>
                        <span className="prob-draw">Draw {fixture.prediction.win_probabilities.draw}%</span>
                        <span className="prob-away">{fixture.away_team} {fixture.prediction.win_probabilities.away_win}%</span>
                      </div>
                    </div>
                  )}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {lastEvents.length > 0 && (
        <div className="panel events-panel">
          <h2>Recent Match Events</h2>
          <div className="events-list">
            {lastEvents.slice().reverse().map((event, index) => (
              <div key={index} className="event">
                <div className="event-type">{formatEvent(event)}</div>
              </div>
            ))}
          </div>
        </div>
      )}

      <div className="panel events-panel">
        <h2>Browse Matches</h2>
        
        {selectedMatch ? (
          <div className="match-detail">
            <div className="match-detail-header">
              <button 
                className="back-button" 
                onClick={() => setSelectedMatch(null)}
              >
                ← Back to Matches
              </button>
              <h3>
                <TeamLink teamName={selectedMatch.match.home_team} /> {selectedMatch.match.home_score} - {selectedMatch.match.away_score} <TeamLink teamName={selectedMatch.match.away_team} />
              </h3>
              <div className="match-info">
                {selectedMatch.match.league} - Matchday {selectedMatch.match.matchday} (Season {selectedMatch.match.season})
              </div>
            </div>
            
            {isLoadingMatchDetail ? (
              <div className="loading">Loading match events...</div>
            ) : (
              <div className="events-list">
                {selectedMatch.events.map((event, index) => (
                  <div key={index} className="event">
                    <div className="event-type">{formatMatchEvent(event)}</div>
                  </div>
                ))}
              </div>
            )}
          </div>
        ) : (
          <div className="matches-list">
            {isLoadingMatches ? (
              <div className="loading">Loading matches...</div>
            ) : completedMatches.length === 0 ? (
              <div>No completed matches yet. Advance the simulation to see match history.</div>
            ) : (
              completedMatches.map((match) => (
                <div 
                  key={match.id} 
                  className="match-item"
                  onClick={() => loadMatchDetail(match.id)}
                >
                  <div className="match-teams">
                    <TeamLink teamName={match.home_team} /> {match.home_score} - {match.away_score} <TeamLink teamName={match.away_team} />
                  </div>
                  <div className="match-info">
                    {match.league} - MD{match.matchday} (S{match.season})
                  </div>
                </div>
              ))
            )}
          </div>
        )}
      </div>
    </div>
  );
}
