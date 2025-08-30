import React, { useState, useEffect } from 'react';
import axios from 'axios';

function App() {
  const [worldState, setWorldState] = useState(null);
  const [isAdvancing, setIsAdvancing] = useState(false);
  const [selectedLeague, setSelectedLeague] = useState('');
  const [lastEvents, setLastEvents] = useState([]);
  const [status, setStatus] = useState('');

  // Load initial world state
  useEffect(() => {
    loadWorldState();
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

  const loadWorldState = async () => {
    try {
      const response = await axios.get('/api/world');
      setWorldState(response.data);
    } catch (error) {
      console.error('Failed to load world state:', error);
      setStatus('Failed to load world state');
    }
  };

  const advanceSimulation = async () => {
    setIsAdvancing(true);
    setStatus('Advancing simulation...');
    
    try {
      const response = await axios.post('/api/advance');
      setLastEvents(response.data.events || []);
      
      if (response.data.status === 'matches_completed') {
        setStatus(`Completed ${response.data.matches_played} matches`);
      } else if (response.data.status === 'matchday_advanced') {
        setStatus('Advanced to next matchday');
      }
      
      // Reload world state
      await loadWorldState();
    } catch (error) {
      console.error('Failed to advance simulation:', error);
      setStatus('Failed to advance simulation');
    } finally {
      setIsAdvancing(false);
    }
  };

  const formatEvent = (event) => {
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

  if (!worldState) {
    return (
      <div className="app">
        <div className="loading">Loading game world...</div>
      </div>
    );
  }

  const currentLeague = worldState.leagues[selectedLeague];

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
                    <td>{team.team}</td>
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
            {worldState.next_fixtures.length === 0 ? (
              <div>No more fixtures scheduled</div>
            ) : (
              worldState.next_fixtures.map((fixture) => (
                <div key={fixture.id} className="fixture">
                  <div className="fixture-teams">
                    {fixture.home_team} vs {fixture.away_team}
                  </div>
                  <div className="fixture-info">
                    {fixture.league} - MD{fixture.matchday}
                  </div>
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
    </div>
  );
}

export default App;