export default function AnomalyTable({ data }) {
  return (
    <div style={{ background: '#1e2330', borderRadius: 12, padding: 24 }}>
      <h2 style={{ fontSize: 18, fontWeight: 600, marginBottom: 6 }}>Anomaly days detected</h2>
      <p style={{ color: '#64748b', fontSize: 14, marginBottom: 24 }}>
        Days where temperature deviated more than 2 standard deviations from the 30-day mean
      </p>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 14 }}>
        <thead>
          <tr style={{ borderBottom: '1px solid #2d3748' }}>
            {['Date', 'City', 'Avg temp', '30-day avg', 'Std dev', 'Deviation'].map(h => (
              <th key={h} style={{ textAlign: 'left', padding: '10px 12px', color: '#64748b', fontWeight: 500 }}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map(row => {
            const deviation = (row.temp_avg_f - row.rolling_30day_avg_temp_f).toFixed(1)
            const isHot = deviation > 0
            return (
              <tr key={row.date} style={{ borderBottom: '1px solid #1a1f2e' }}>
                <td style={{ padding: '12px 12px', color: '#e2e8f0' }}>{row.date.slice(0, 10)}</td>
                <td style={{ padding: '12px 12px', color: '#94a3b8' }}>{row.city}</td>
                <td style={{ padding: '12px 12px', color: '#e2e8f0' }}>{row.temp_avg_f}°F</td>
                <td style={{ padding: '12px 12px', color: '#94a3b8' }}>{row.rolling_30day_avg_temp_f}°F</td>
                <td style={{ padding: '12px 12px', color: '#94a3b8' }}>{row.temp_stddev_30day}°F</td>
                <td style={{ padding: '12px 12px' }}>
                  <span style={{
                    color: isHot ? '#f87171' : '#60a5fa',
                    fontWeight: 600
                  }}>
                    {isHot ? '+' : ''}{deviation}°F
                  </span>
                </td>
              </tr>
            )
          })}
        </tbody>
      </table>
    </div>
  )
}