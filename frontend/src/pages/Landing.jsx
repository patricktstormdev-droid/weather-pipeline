import { useNavigate } from 'react-router-dom'
import { useEffect, useState } from 'react'
import axios from 'axios'
import { formatDateLong, formatNumber } from '../utils/formatters'

export default function Landing() {
  const navigate = useNavigate()
  const [summary, setSummary] = useState(null)

  useEffect(() => {
    axios.get(`${import.meta.env.VITE_API_URL}/api/summary`)
      .then(res => setSummary(res.data[0]))
      .catch(err => console.error(err))
  }, [])

  return (
    <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>

      {/* Hero */}
      <div style={{
        flex: 1,
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        padding: '60px 24px',
        textAlign: 'center',
        background: 'linear-gradient(135deg, #0f1117 0%, #1a1f2e 100%)'
      }}>
        <div style={{
          fontSize: 13,
          letterSpacing: 2,
          color: '#60a5fa',
          textTransform: 'uppercase',
          marginBottom: 16
        }}>
          Data Engineering Portfolio Project
        </div>

        <h1 style={{
          fontSize: 'clamp(2rem, 5vw, 3.5rem)',
          fontWeight: 700,
          lineHeight: 1.2,
          marginBottom: 20,
          background: 'linear-gradient(135deg, #e2e8f0, #60a5fa)',
          WebkitBackgroundClip: 'text',
          WebkitTextFillColor: 'transparent'
        }}>
          Detroit Weather<br />Trend Pipeline
        </h1>

        <p style={{
          fontSize: 18,
          color: '#94a3b8',
          maxWidth: 560,
          lineHeight: 1.7,
          marginBottom: 40
        }}>
          An end-to-end data pipeline ingesting daily weather data,
          transforming it through dbt models, and surfacing anomaly
          detection via PySpark — all orchestrated with Airflow.
        </p>

        <button
          onClick={() => navigate('/dashboard')}
          style={{
            background: '#3b82f6',
            color: '#fff',
            border: 'none',
            borderRadius: 8,
            padding: '14px 32px',
            fontSize: 16,
            fontWeight: 600,
            cursor: 'pointer',
          }}
        >
          View Dashboard
        </button>
      </div>

      {/* Summary stats */}
      {summary && (
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(180px, 1fr))',
          gap: 1,
          background: '#1e2330',
          borderTop: '1px solid #2d3748'
        }}>
          {[
            { 
              label: 'Days tracked', 
              value: summary.total_days,
              detail: `${formatDateLong(summary.date_start)} to ${formatDateLong(summary.date_end)}`
            },
            { 
              label: 'Avg temperature', 
              value: `${summary.avg_temp_f}°F`,
              detail: null
            },
            { 
              label: 'Hottest day', 
              value: `${summary.max_temp_f}°F`,
              detail: formatDateLong(summary.date_max_temp)
            },
            { 
              label: 'Coldest day', 
              value: `${summary.min_temp_f}°F`,
              detail: formatDateLong(summary.date_min_temp)
            },
            { 
              label: 'Total precipitation', 
              value: `${formatNumber(summary.total_precipitation_mm)}mm`,
              detail: null
            },
            { 
              label: 'Anomaly days', 
              value: summary.anomaly_days,
              detail: null
            },
          ].map(stat => (
            <div key={stat.label} style={{
              padding: '28px 24px',
              textAlign: 'center',
              background: '#0f1117'
            }}>
              <div style={{ fontSize: 28, fontWeight: 700, color: '#60a5fa' }}>
                {stat.value}
              </div>
              <div style={{ fontSize: 13, color: '#64748b', marginTop: 6 }}>
                {stat.label}
              </div>
              {stat.detail && (
                <div style={{ fontSize: 11, color: '#475569', marginTop: 8 }}>
                  {stat.detail}
                </div>
              )}
            </div>
          ))}
        </div>
      )}

      {/* Stack badges */}
      <div style={{
        display: 'flex',
        justifyContent: 'center',
        flexWrap: 'wrap',
        gap: 10,
        padding: '24px',
        background: '#0f1117',
        borderTop: '1px solid #1e2330'
      }}>
        {['Python', 'Airflow', 'PostgreSQL', 'dbt', 'PySpark', 'Flask', 'React', 'Docker'].map(tech => (
          <span key={tech} style={{
            padding: '6px 14px',
            borderRadius: 20,
            fontSize: 13,
            background: '#1e2330',
            color: '#94a3b8',
            border: '1px solid #2d3748'
          }}>
            {tech}
          </span>
        ))}
      </div>
    </div>
  )
}