import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts'
import { formatDate, formatNumber } from '../utils/formatters'

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: '#0f1117', border: '1px solid #2d3748', borderRadius: 8, padding: 12 }}>
        <p style={{ color: '#e2e8f0', margin: 0, marginBottom: 8 }}>
          {formatDate(payload[0].payload.date)}
        </p>
        <p style={{ color: '#60a5fa', margin: 0 }}>
          Precipitation: {formatNumber(payload[0].value)}mm
        </p>
      </div>
    )
  }
  return null
}

export default function PrecipChart({ data }) {
  const formatted = data.map(d => ({
    ...d,
    date: d.date.slice(0, 10),
    display_date: formatDate(d.date.slice(0, 10))
  }))

  return (
    <div style={{ background: '#1e2330', borderRadius: 12, padding: 24 }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 6 }}>Daily precipitation</h2>
      <p style={{ color: '#64748b', fontSize: 14, marginBottom: 24 }}>
        Rainfall and snowfall in millimeters
      </p>
      <ResponsiveContainer width="100%" height={220}>
        <BarChart data={formatted}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
          <XAxis dataKey="display_date" tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} interval={13} angle={-45} textAnchor="end" height={80} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} unit="mm" />
          <Tooltip content={<CustomTooltip />} />
          <Bar dataKey="precipitation_mm" fill="#60a5fa" name="Precipitation" radius={[3, 3, 0, 0]} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}