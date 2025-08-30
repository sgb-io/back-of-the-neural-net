'use client';

import React from 'react';
import Link from 'next/link';
import axios from 'axios';

interface PlayerLinkProps {
  playerName: string;
  className?: string;
}

interface PlayerLookupResponse {
  player_id: string;
  player_name: string;
  position: string;
}

export default function PlayerLink({ playerName, className = 'player-name-link' }: PlayerLinkProps) {
  const [playerId, setPlayerId] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState<boolean>(false);

  React.useEffect(() => {
    const lookupPlayer = async () => {
      if (!playerName) return;
      
      try {
        setIsLoading(true);
        const response = await axios.get<PlayerLookupResponse>(`/api/players/lookup/${encodeURIComponent(playerName)}`);
        setPlayerId(response.data.player_id);
      } catch (error) {
        console.warn(`Could not find player ID for: ${playerName}`, error);
        setPlayerId(null);
      } finally {
        setIsLoading(false);
      }
    };

    lookupPlayer();
  }, [playerName]);

  if (isLoading) {
    return <span className={className}>{playerName}</span>;
  }

  if (playerId) {
    return (
      <Link href={`/players/${playerId}`} className={className}>
        {playerName}
      </Link>
    );
  }

  // If no player ID found, just render as text
  return <span className={className}>{playerName}</span>;
}