'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import axios from 'axios';
import { PlayerDetail } from '@/types/api';
import TeamLink from '@/components/TeamLink';

interface PlayerPageProps {
  params: Promise<{
    playerId: string;
  }>;
}

export default function PlayerPage({ params }: PlayerPageProps) {
  const [playerId, setPlayerId] = useState<string>('');
  const [playerDetail, setPlayerDetail] = useState<PlayerDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');
  const [careerSummary, setCareerSummary] = useState<string>('');
  const [isLoadingCareerSummary, setIsLoadingCareerSummary] = useState<boolean>(false);

  useEffect(() => {
    // Resolve the params Promise and get playerId
    params.then(({ playerId: resolvedPlayerId }) => {
      setPlayerId(resolvedPlayerId);
    });
  }, [params]);

  useEffect(() => {
    if (playerId) {
      loadPlayerData();
    }
  }, [playerId]);

  const loadPlayerData = useCallback(async (): Promise<void> => {
    try {
      setIsLoading(true);
      const response = await axios.get<PlayerDetail>(`/api/players/${playerId}`);
      setPlayerDetail(response.data);
      
      // Load career summary after player data is loaded
      loadCareerSummary();
    } catch (error) {
      console.error('Failed to load player data:', error);
      setError('Failed to load player data');
    } finally {
      setIsLoading(false);
    }
  }, [playerId]);

  const loadCareerSummary = useCallback(async (): Promise<void> => {
    if (!playerId) return;
    
    try {
      setIsLoadingCareerSummary(true);
      const response = await axios.get(`/api/players/${playerId}/career-summary`);
      setCareerSummary(response.data.career_summary);
    } catch (error) {
      console.error('Failed to load career summary:', error);
      setCareerSummary('Unable to generate career summary at this time.');
    } finally {
      setIsLoadingCareerSummary(false);
    }
  }, [playerId]);

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

  const getAttributeColor = (value: number): string => {
    if (value >= 80) return '#2ecc71'; // Green
    if (value >= 70) return '#f39c12'; // Orange
    if (value >= 60) return '#e67e22'; // Dark orange
    return '#e74c3c'; // Red
  };

  if (isLoading) {
    return (
      <div className="app">
        <div className="loading">Loading player data...</div>
      </div>
    );
  }

  if (error || !playerDetail) {
    return (
      <div className="app">
        <div className="error">
          <h2>Error</h2>
          <p>{error || 'Player not found'}</p>
          <Link href="/" className="back-button">← Back to Home</Link>
        </div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <h1>🧑‍💼 {playerDetail.name}</h1>
        <p>
          <span 
            className="player-position-header" 
            style={{ backgroundColor: getPositionColor(playerDetail.position) }}
          >
            {playerDetail.position}
          </span>
          {' '}• Age {playerDetail.age} • Overall {playerDetail.overall_rating}
        </p>
      </header>

      <div className="player-nav">
        <Link href="/" className="back-button">← Back to Home</Link>
        <Link href={`/teams/${playerDetail.current_team.id}`} className="team-link">
          View Team: {playerDetail.current_team.name}
        </Link>
      </div>

      <div className="player-content">
        {/* Player Overview Panel */}
        <div className="panel">
          <h2>Player Overview</h2>
          <div className="player-overview">
            <div className="overview-section">
              <h3>Current Club</h3>
              <div className="current-club">
                <TeamLink teamName={playerDetail.current_team.name} />
                <span className="league-name">({playerDetail.current_team.league})</span>
              </div>
            </div>
            
            <div className="overview-section">
              <h3>Current Condition</h3>
              <div className="condition-stats">
                <div className="condition-item">
                  <span 
                    className="condition-label"
                    style={{ color: getPlayerFormColor(playerDetail.form) }}
                  >
                    Form:
                  </span>
                  <span className="condition-value">{playerDetail.form}/100</span>
                </div>
                <div className="condition-item">
                  <span className="condition-label">Morale:</span>
                  <span className="condition-value">{playerDetail.morale}/100</span>
                </div>
                <div className="condition-item">
                  <span className="condition-label">Fitness:</span>
                  <span className="condition-value">{playerDetail.fitness}/100</span>
                </div>
                {playerDetail.injured && (
                  <div className="condition-item">
                    <span className="injured-status">🏥 INJURED</span>
                  </div>
                )}
              </div>
            </div>
          </div>
        </div>

        {/* Player Attributes Panel */}
        <div className="panel">
          <h2>Player Attributes</h2>
          <div className="attributes-grid">
            <div className="attribute-item">
              <span className="attribute-label">Pace:</span>
              <span 
                className="attribute-value"
                style={{ color: getAttributeColor(playerDetail.pace) }}
              >
                {playerDetail.pace}
              </span>
            </div>
            <div className="attribute-item">
              <span className="attribute-label">Shooting:</span>
              <span 
                className="attribute-value"
                style={{ color: getAttributeColor(playerDetail.shooting) }}
              >
                {playerDetail.shooting}
              </span>
            </div>
            <div className="attribute-item">
              <span className="attribute-label">Passing:</span>
              <span 
                className="attribute-value"
                style={{ color: getAttributeColor(playerDetail.passing) }}
              >
                {playerDetail.passing}
              </span>
            </div>
            <div className="attribute-item">
              <span className="attribute-label">Defending:</span>
              <span 
                className="attribute-value"
                style={{ color: getAttributeColor(playerDetail.defending) }}
              >
                {playerDetail.defending}
              </span>
            </div>
            <div className="attribute-item">
              <span className="attribute-label">Physicality:</span>
              <span 
                className="attribute-value"
                style={{ color: getAttributeColor(playerDetail.physicality) }}
              >
                {playerDetail.physicality}
              </span>
            </div>
          </div>
        </div>

        {/* Season Statistics Panel */}
        <div className="panel">
          <h2>Current Season Statistics</h2>
          <div className="season-stats-grid">
            <div className="stat-item">
              <span className="stat-label">Matches Played:</span>
              <span className="stat-value">{playerDetail.season_stats.matches_played}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Minutes Played:</span>
              <span className="stat-value">{playerDetail.season_stats.minutes_played}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Goals:</span>
              <span className="stat-value">{playerDetail.season_stats.goals}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Assists:</span>
              <span className="stat-value">{playerDetail.season_stats.assists}</span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Yellow Cards:</span>
              <span className="stat-value">
                {playerDetail.season_stats.yellow_cards > 0 && '🟨 '}
                {playerDetail.season_stats.yellow_cards}
              </span>
            </div>
            <div className="stat-item">
              <span className="stat-label">Red Cards:</span>
              <span className="stat-value">
                {playerDetail.season_stats.red_cards > 0 && '🟥 '}
                {playerDetail.season_stats.red_cards}
              </span>
            </div>
          </div>
        </div>

        {/* Career Summary Panel */}
        <div className="panel">
          <h2>Career Summary</h2>
          <div className="career-summary">
            {isLoadingCareerSummary ? (
              <p className="summary-loading">
                <em>🧠 Generating AI-powered career summary...</em>
              </p>
            ) : careerSummary ? (
              <div className="summary-content">
                {careerSummary.split('\n').map((paragraph, index) => (
                  paragraph.trim() && (
                    <p key={index} className="summary-paragraph">
                      {paragraph.trim()}
                    </p>
                  )
                ))}
              </div>
            ) : (
              <p className="summary-placeholder">
                <em>Career summary powered by AI will be available soon...</em>
              </p>
            )}
            <div className="career-facts">
              <div className="fact-item">
                <span className="fact-label">Position:</span>
                <span className="fact-value">{playerDetail.position}</span>
              </div>
              <div className="fact-item">
                <span className="fact-label">Age:</span>
                <span className="fact-value">{playerDetail.age} years old</span>
              </div>
              <div className="fact-item">
                <span className="fact-label">Overall Rating:</span>
                <span className="fact-value">{playerDetail.overall_rating}/100</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}