import axios from 'axios';
import { TeamLookupResponse } from '@/types/api';

/**
 * Convert team name to team ID by looking it up via the API
 */
export async function getTeamIdFromName(teamName: string): Promise<string | null> {
  try {
    const response = await axios.get<TeamLookupResponse>(`/api/teams/lookup/${encodeURIComponent(teamName)}`);
    return response.data.team_id;
  } catch (error) {
    console.error('Failed to lookup team:', error);
    return null;
  }
}

/**
 * Create a team link URL from team name
 */
export function createTeamLink(teamName: string): string {
  // Convert team name to a URL-safe format as a fallback
  const safeName = teamName.toLowerCase().replace(/\s+/g, '_').replace(/[^a-z0-9_]/g, '');
  return `/teams/${safeName}`;
}