/**
 * Format a date string (YYYY-MM-DD) to a readable format (MMM DD)
 * e.g., "2026-03-25" -> "Mar 25"
 */
export function formatDate(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr + 'T00:00:00')
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
}

/**
 * Format a date string to a longer format (MMM DD, YYYY)
 * e.g., "2026-03-25" -> "Mar 25, 2026"
 */
export function formatDateLong(dateStr) {
  if (!dateStr) return ''
  const date = new Date(dateStr + 'T00:00:00')
  return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
}

/**
 * Format a number to 2 decimal places
 */
export function formatNumber(num) {
  if (num === null || num === undefined) return ''
  return parseFloat(num).toFixed(2)
}

/**
 * Format a number to 1 decimal place
 */
export function formatNumberOneDecimal(num) {
  if (num === null || num === undefined) return ''
  return parseFloat(num).toFixed(1)
}
