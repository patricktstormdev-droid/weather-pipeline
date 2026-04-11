import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import { formatDate, formatNumber } from '../utils/formatters'

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    return (
      <div style={{ background: '#0f1117', border: '1px solid #2d3748', borderRadius: 8, padding: 12 }}>
        <p style={{ color: '#e2e8f0', margin: 0, marginBottom: 8 }}>
          {formatDate(payload[0].payload.date)}
        </p>
        {payload.map((entry, index) => (
          <p key={index} style={{ color: entry.color, margin: 4 }}>
            {entry.name}: {formatNumber(entry.value)}°F
          </p>
        ))}
      </div>
    )
  }
  return null
}

export default function TempTrendChart({ data }) {
  const formatted = data.map(d => ({
    ...d,
    date: d.date.slice(0, 10),
    display_date: formatDate(d.date.slice(0, 10))
  }))

  return (
    <div style={{ background: '#1e2330', borderRadius: 12, padding: 24 }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 6 }}>Temperature trends</h2>
      <p style={{ color: '#64748b', fontSize: 14, marginBottom: 24 }}>
        Daily high, low, average and 7-day rolling average
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formatted}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
          <XAxis dataKey="display_date" tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} interval={13} angle={-45} textAnchor="end" height={80} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} unit="°F" />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 13 }} />
          <Line type="monotone" dataKey="temp_max_f" stroke="#f87171" dot={false} name="High" strokeWidth={1.5} />
          <Line type="monotone" dataKey="temp_min_f" stroke="#60a5fa" dot={false} name="Low" strokeWidth={1.5} />
          <Line type="monotone" dataKey="temp_avg_f" stroke="#94a3b8" dot={false} name="Avg" strokeWidth={1} strokeDasharray="4 2" />
          <Line type="monotone" dataKey="rolling_7day_avg_temp_f" stroke="#34d399" dot={false} name="7-day avg" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>
  )
}