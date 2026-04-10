import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, ReferenceDot } from 'recharts'
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

export default function SparkFeaturesChart({ data }) {
  const formatted = data.map(d => ({
    ...d,
    date: d.date.slice(0, 10),
    display_date: formatDate(d.date.slice(0, 10))
  }))

  const anomalyDots = formatted.filter(d => d.is_anomaly)

  return (
    <div style={{ background: '#1e2330', borderRadius: 12, padding: 24 }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 6 }}>PySpark — rolling averages + anomalies</h2>
      <p style={{ color: '#64748b', fontSize: 14, marginBottom: 24 }}>
        7-day and 30-day rolling averages with anomaly days highlighted
      </p>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={formatted}>
          <CartesianGrid strokeDasharray="3 3" stroke="#2d3748" />
          <XAxis dataKey="display_date" tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} interval={13} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} unit="°F" />
          <Tooltip content={<CustomTooltip />} />
          <Legend wrapperStyle={{ color: '#94a3b8', fontSize: 13 }} />
          <Line type="monotone" dataKey="temp_avg_f" stroke="#94a3b8" dot={false} name="Daily avg" strokeWidth={1} />
          <Line type="monotone" dataKey="rolling_7day_avg_temp_f" stroke="#34d399" dot={false} name="7-day avg" strokeWidth={2} />
          <Line type="monotone" dataKey="rolling_30day_avg_temp_f" stroke="#a78bfa" dot={false} name="30-day avg" strokeWidth={2} />
          {anomalyDots.map(d => (
            <ReferenceDot key={d.date} x={d.display_date} y={d.temp_avg_f} r={6} fill="#f87171" stroke="#0f1117" strokeWidth={2} />
          ))}
        </LineChart>
      </ResponsiveContainer>
      <p style={{ color: '#64748b', fontSize: 12, marginTop: 12 }}>
        Red dots = anomaly days (temp deviated more than 2 standard deviations from 30-day mean)
      </p>
    </div>
  )
}