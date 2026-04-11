/**
 * Format a date string (YYYY-MM-DD or ISO string) to a readable format (MMM DD)
 * e.g., "2026-03-25" -> "Mar 25"
 * e.g., "2026-03-25T00:00:00" -> "Mar 25"
 */
export function formatDate(dateStr) {
  if (!dateStr) return ''
  try {
    // Extract just the YYYY-MM-DD part if it's an ISO string
    const dateOnly = typeof dateStr === 'string' ? dateStr.split('T')[0] : dateStr
    const date = new Date(dateOnly + 'T00:00:00Z')
    if (isNaN(date.getTime())) return ''
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric' })
  } catch {
    return ''
  }
}

/**
 * Format a date string to a longer format (MMM DD, YYYY)
 * e.g., "2026-03-25" -> "Mar 25, 2026"
 * e.g., "2026-03-25T00:00:00" -> "Mar 25, 2026"
 */
export function formatDateLong(dateStr) {
  if (!dateStr) return ''
  try {
    // Extract just the YYYY-MM-DD part if it's an ISO string
    const dateOnly = typeof dateStr === 'string' ? dateStr.split('T')[0] : dateStr
    const date = new Date(dateOnly + 'T00:00:00Z')
    if (isNaN(date.getTime())) return ''
    return date.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' })
  } catch {
    return ''
  }
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
