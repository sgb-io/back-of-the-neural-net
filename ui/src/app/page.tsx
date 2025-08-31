'use client';

import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { WorldState, MatchEvent, GoalEvent, CardEvent, SubstitutionEvent, MatchEndedEvent, AdvanceResponse, League, CompletedMatch, MatchDetail, MatchEventDetail, Fixture, NewsResponse, NewsReport, NewsMatch } from '@/types/api';
import TeamLink from '@/components/TeamLink';
import PlayerLink from '@/components/PlayerLink';

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

  // New state for news feed
  const [newsData, setNewsData] = useState<NewsResponse | null>(null);
  const [isLoadingNews, setIsLoadingNews] = useState<boolean>(false);

  // Load initial world state
  useEffect(() => {
    loadWorldState();
    loadNewsData();
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
      
      // Reload world state, completed matches, and news
      await loadWorldState();
      await loadCompletedMatches();
      await loadNewsData();
    } catch (error) {
      console.error('Failed to advance simulation:', error);
      setStatus('Failed to advance simulation');
    } finally {
      setIsAdvancing(false);
    }
  };

  const formatEvent = (event: MatchEvent): React.ReactElement => {
    switch (event.event_type) {
      case 'Goal':
        const goalEvent = event as GoalEvent;
        return (
          <span>
            ⚽ {goalEvent.minute}&apos; GOAL! <PlayerLink playerName={goalEvent.scorer} /> scores for {goalEvent.team}
            {goalEvent.assist && <span> (assist: <PlayerLink playerName={goalEvent.assist} />)</span>}
          </span>
        );
      case 'YellowCard':
      case 'RedCard':
        const cardEvent = event as CardEvent;
        return (
          <span>
            {event.event_type === 'YellowCard' ? '🟨' : '🟥'} {cardEvent.minute}&apos; {event.event_type === 'YellowCard' ? 'Yellow' : 'Red'} card for <PlayerLink playerName={cardEvent.player} /> ({cardEvent.team}) - {cardEvent.reason}
          </span>
        );
      case 'Substitution':
        const subEvent = event as SubstitutionEvent;
        return (
          <span>
            🔄 {subEvent.minute}&apos; Substitution ({subEvent.team}): <PlayerLink playerName={subEvent.player_off} /> ➔ <PlayerLink playerName={subEvent.player_on} />
          </span>
        );
      case 'MatchEnded':
        const matchEndEvent = event as MatchEndedEvent;
        return <span>🏁 Full time: {matchEndEvent.home_team} {matchEndEvent.home_score} - {matchEndEvent.away_score} {matchEndEvent.away_team}</span>;
      case 'KickOff':
        return <span>⚽ Kick off!</span>;
      default:
        return <span>{event.event_type}: {JSON.stringify(event, null, 2)}</span>;
    }
  };

  const formatMatchEvent = (event: MatchEventDetail): React.ReactElement => {
    switch (event.event_type) {
      case 'Goal':
        return (
          <span>
            ⚽ {event.minute}&apos; GOAL! <PlayerLink playerName={event.scorer || ''} /> scores for {event.team}
            {event.assist && <span> (assist: <PlayerLink playerName={event.assist} />)</span>}
          </span>
        );
      case 'YellowCard':
        return (
          <span>
            🟨 {event.minute}&apos; Yellow card for <PlayerLink playerName={event.player || ''} /> ({event.team}) - {event.reason}
          </span>
        );
      case 'RedCard':
        return (
          <span>
            🟥 {event.minute}&apos; Red card for <PlayerLink playerName={event.player || ''} /> ({event.team}) - {event.reason}
          </span>
        );
      case 'Substitution':
        return (
          <span>
            🔄 {event.minute}&apos; Substitution ({event.team}): <PlayerLink playerName={event.player_off || ''} /> ➔ <PlayerLink playerName={event.player_on || ''} />
          </span>
        );
      case 'MatchEnded':
        return <span>🏁 Full time: {event.home_team} {event.home_score} - {event.away_score} {event.away_team}</span>;
      case 'MatchStarted':
        return <span>🟢 Match started: {event.home_team} vs {event.away_team}</span>;
      case 'KickOff':
        return <span>⚽ Kick off!</span>;
      default:
        return <span>{event.event_type}</span>;
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

  const loadNewsData = async (): Promise<void> => {
    setIsLoadingNews(true);
    try {
      const response = await axios.get<NewsResponse>('/api/news');
      setNewsData(response.data);
    } catch (error) {
      console.error('Failed to load news data:', error);
      setStatus('Failed to load news data');
    } finally {
      setIsLoadingNews(false);
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
        <div className="game-info">
          <span className="season">Season {worldState.season}</span>
          <span className="date">{worldState.current_date}</span>
        </div>
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
          <h2>News</h2>
          <div className="news-feed">
            {isLoadingNews ? (
              <div>Loading news...</div>
            ) : !newsData || Object.keys(newsData.news_by_league).length === 0 ? (
              <div>No news available</div>
            ) : (
              Object.entries(newsData.news_by_league).map(([leagueId, leagueNews]) => (
                <div key={leagueId} className="league-news">
                  <h3 className="league-news-title">{leagueId.replace('_', ' ').toUpperCase()}</h3>
                  
                  {/* Recent Reports Section */}
                  {leagueNews.recent_reports.length > 0 && (
                    <div className="news-section">
                      <h4 className="news-section-title">📰 Recent Reports</h4>
                      {leagueNews.recent_reports.map((report: NewsReport) => (
                        <div key={report.id} className="news-item news-report">
                          <div className="news-headline">{report.headline}</div>
                          <div className="news-meta">
                            <span className="news-outlet">{report.outlet_name}</span>
                            {report.teams_mentioned.length > 0 && (
                              <span className="news-teams">
                                {report.teams_mentioned.map((team, index) => (
                                  <span key={index}>
                                    {index > 0 && ', '}
                                    <TeamLink teamName={team} />
                                  </span>
                                ))}
                              </span>
                            )}
                            <span className={`news-sentiment ${report.sentiment > 0 ? 'positive' : report.sentiment < 0 ? 'negative' : 'neutral'}`}>
                              {report.sentiment > 0 ? '😊' : report.sentiment < 0 ? '😞' : '😐'}
                            </span>
                          </div>
                        </div>
                      ))}
                    </div>
                  )}
                  
                  {/* Upcoming Matches Section */}
                  {leagueNews.upcoming_matches.length > 0 && (
                    <div className="news-section">
                      <h4 className="news-section-title">⚽ Upcoming Matches</h4>
                      {leagueNews.upcoming_matches.map((match: NewsMatch) => (
                        <div key={match.id} className={`news-item news-match ${match.importance !== 'normal' ? 'important-match' : ''}`}>
                          <div className="match-teams">
                            <TeamLink teamName={match.home_team} /> vs <TeamLink teamName={match.away_team} />
                            {match.importance !== 'normal' && (
                              <span className={`importance-badge ${match.importance}`}>
                                {match.importance === 'title_race' ? '👑' : 
                                 match.importance === 'derby' ? '⚔️' : 
                                 match.importance === 'relegation' ? '🔻' : '⭐'}
                              </span>
                            )}
                          </div>
                          <div className="match-info">
                            Matchday {match.matchday}
                          </div>
                          {match.media_preview && (
                            <div className="media-preview">
                              <div className="media-headline">{match.media_preview.headline}</div>
                              <div className="media-content">{match.media_preview.preview}</div>
                              <div className="media-source">— {match.media_preview.source}</div>
                            </div>
                          )}
                          {match.prediction && (
                            <div className="match-prediction">
                              <div className="prediction-score">
                                Predicted: {match.prediction.predicted_score.home_goals} - {match.prediction.predicted_score.away_goals}
                              </div>
                              <div className="prediction-probabilities">
                                <span className="prob-home">{match.home_team} {match.prediction.win_probabilities.home_win}%</span>
                                <span className="prob-draw">Draw {match.prediction.win_probabilities.draw}%</span>
                                <span className="prob-away">{match.away_team} {match.prediction.win_probabilities.away_win}%</span>
                              </div>
                            </div>
                          )}
                        </div>
                      ))}
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

      {/* Fullscreen loading overlay */}
      {isAdvancing && (
        <div className="fullscreen-loading-overlay">
          <div className="loading-spinner">
            <div className="spinner"></div>
            <div className="loading-text">Advancing simulation...</div>
          </div>
        </div>
      )}
    </div>
  );
}
