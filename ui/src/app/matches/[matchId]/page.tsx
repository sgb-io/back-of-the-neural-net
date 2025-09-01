'use client';

import React, { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import axios from 'axios';
import { MatchDetail } from '@/types/api';
import TeamLink from '@/components/TeamLink';
import { formatMatchEvent } from '@/utils/matchEventFormatters';

interface MatchPageProps {
  params: Promise<{
    matchId: string;
  }>;
}

export default function MatchPage({ params }: MatchPageProps) {
  const [matchId, setMatchId] = useState<string>('');
  const [matchDetail, setMatchDetail] = useState<MatchDetail | null>(null);
  const [isLoading, setIsLoading] = useState<boolean>(true);
  const [error, setError] = useState<string>('');

  useEffect(() => {
    // Resolve the params Promise and get matchId
    params.then(({ matchId: resolvedMatchId }) => {
      setMatchId(resolvedMatchId);
    });
  }, [params]);

  useEffect(() => {
    if (matchId) {
      loadMatchData();
    }
  }, [matchId]);

  const loadMatchData = useCallback(async (): Promise<void> => {
    try {
      setIsLoading(true);
      const response = await axios.get<MatchDetail>(`/api/matches/${matchId}/events`);
      setMatchDetail(response.data);
    } catch (error) {
      console.error('Failed to load match detail:', error);
      setError('Failed to load match detail');
    } finally {
      setIsLoading(false);
    }
  }, [matchId]);

  if (isLoading) {
    return (
      <div className="app">
        <div className="loading">Loading match...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="app">
        <div className="error">Error: {error}</div>
      </div>
    );
  }

  if (!matchDetail) {
    return (
      <div className="app">
        <div className="error">Match not found</div>
      </div>
    );
  }

  return (
    <div className="app">
      <header className="header">
        <h1>⚽ Back of the Neural Net</h1>
        <nav className="nav">
          <Link href="/">Home</Link>
          <Link href="/#browse-matches">Browse Matches</Link>
        </nav>
      </header>

      <div className="main">
        <div className="panel match-detail-panel">
          <div className="match-detail">
            <div className="match-detail-header">
              <Link href="/" className="back-button">
                ← Back to Home
              </Link>
              <h2>
                <TeamLink teamName={matchDetail.match.home_team} /> {matchDetail.match.home_score} - {matchDetail.match.away_score} <TeamLink teamName={matchDetail.match.away_team} />
              </h2>
              <div className="match-info">
                {matchDetail.match.league} - Matchday {matchDetail.match.matchday} (Season {matchDetail.match.season})
              </div>
            </div>
            
            <div className="events-list">
              <h3>Match Events</h3>
              {matchDetail.events.length === 0 ? (
                <div>No events recorded for this match.</div>
              ) : (
                matchDetail.events.map((event, index) => (
                  <div key={index} className="event">
                    <div className="event-type">{formatMatchEvent(event)}</div>
                  </div>
                ))
              )}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}