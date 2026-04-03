import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'

export default function TempTrendChart({ data }) {
  const formatted = data.map(d => ({
    ...d,
    date: d.date.slice(0, 10)
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
          <XAxis dataKey="date" tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} interval={13} />
          <YAxis tick={{ fill: '#64748b', fontSize: 11 }} tickLine={false} unit="°F" />
          <Tooltip
            contentStyle={{ background: '#0f1117', border: '1px solid #2d3748', borderRadius: 8 }}
            labelStyle={{ color: '#e2e8f0' }}
          />
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