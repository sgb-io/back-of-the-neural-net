/**
 * Utilities for handling player and team reputation display
 */

export interface ReputationLevel {
  label: string;
  description: string;
  color: string;
}

/**
 * Convert a player reputation number (1-100) to abstracted language
 */
export function getPlayerReputationLevel(reputation: number): ReputationLevel {
  if (reputation >= 85) {
    return {
      label: "World Class",
      description: "Globally recognized superstar",
      color: "#d4edda" // Light green
    };
  } else if (reputation >= 70) {
    return {
      label: "Renowned",
      description: "Well-known elite player",
      color: "#d1ecf1" // Light blue
    };
  } else if (reputation >= 55) {
    return {
      label: "Established",
      description: "Respected professional",
      color: "#fff3cd" // Light yellow
    };
  } else if (reputation >= 40) {
    return {
      label: "Promising",
      description: "Emerging talent",
      color: "#f8d7da" // Light red
    };
  } else if (reputation >= 25) {
    return {
      label: "Developing",
      description: "Squad player",
      color: "#e2e3e5" // Light gray
    };
  } else {
    return {
      label: "Unknown",
      description: "Relatively unknown",
      color: "#f8f9fa" // Very light gray
    };
  }
}

/**
 * Convert a team reputation number (1-100) to abstracted language
 */
export function getTeamReputationLevel(reputation: number): ReputationLevel {
  if (reputation >= 85) {
    return {
      label: "Elite",
      description: "Global football powerhouse",
      color: "#d4edda" // Light green
    };
  } else if (reputation >= 70) {
    return {
      label: "Top Club",
      description: "Major footballing institution",
      color: "#d1ecf1" // Light blue
    };
  } else if (reputation >= 55) {
    return {
      label: "Established",
      description: "Well-respected club",
      color: "#fff3cd" // Light yellow
    };
  } else if (reputation >= 40) {
    return {
      label: "Professional",
      description: "Solid professional club",
      color: "#f8d7da" // Light red
    };
  } else if (reputation >= 25) {
    return {
      label: "Regional",
      description: "Local club",
      color: "#e2e3e5" // Light gray
    };
  } else {
    return {
      label: "Minor",
      description: "Small local club",
      color: "#f8f9fa" // Very light gray
    };
  }
}

/**
 * Get a color for reputation display based on level
 */
export function getReputationColor(reputation: number): string {
  if (reputation >= 85) return "#28a745"; // Green
  if (reputation >= 70) return "#17a2b8"; // Blue
  if (reputation >= 55) return "#ffc107"; // Yellow
  if (reputation >= 40) return "#fd7e14"; // Orange
  if (reputation >= 25) return "#6c757d"; // Gray
  return "#868e96"; // Light gray
}