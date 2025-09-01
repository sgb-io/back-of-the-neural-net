import React from 'react';
import { MatchEventDetail } from '@/types/api';
import PlayerLink from '@/components/PlayerLink';

export const formatMatchEvent = (event: MatchEventDetail): React.ReactElement => {
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