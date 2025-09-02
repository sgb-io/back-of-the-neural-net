/**
 * Utility functions for formatting values
 */

export function formatCurrency(amount: number): string {
  return `£${amount.toLocaleString()}`;
}

export function formatPercentage(value: number): string {
  return `${(value * 100).toFixed(1)}%`;
}

export function formatCapacity(used: number, total: number): string {
  const percentage = total > 0 ? (used / total * 100).toFixed(1) : '0.0';
  return `${used.toLocaleString()} / ${total.toLocaleString()} (${percentage}%)`;
}