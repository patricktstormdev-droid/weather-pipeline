import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import axios from 'axios'
import TempTrendChart from '../components/TempTrendChart'
import AnomalyTable from '../components/AnomalyTable'
import SparkFeaturesChart from '../components/SparkFeaturesChart'
import PrecipChart from '../components/PrecipChart'

export default function Dashboard() {
  const navigate = useNavigate()
  const [trends, setTrends] = useState([])
  const [anomalies, setAnomalies] = useState([])
  const [spark, setSpark] = useState([])
  const [loading, setLoading] = useState(true)
  const [startDate, setStartDate] = useState('')
  const [endDate, setEndDate] = useState('')

  // Fetch data with optional date range
  const fetchData = (start, end) => {
    setLoading(true)
    const params = new URLSearchParams()
    if (start) params.append('start_date', start)
    if (end) params.append('end_date', end)

    Promise.all([
      axios.get(`${import.meta.env.VITE_API_URL}/api/trends?${params}`),
      axios.get(`${import.meta.env.VITE_API_URL}/api/anomalies?${params}`),
      axios.get(`${import.meta.env.VITE_API_URL}/api/spark-features?${params}`),
    ]).then(([t, a, s]) => {
      setTrends(t.data)
      setAnomalies(a.data)
      setSpark(s.data)
      setLoading(false)
    }).catch(err => {
      console.error(err)
      setLoading(false)
    })
  }

  // Initial load
  useEffect(() => {
    fetchData('', '')
  }, [])

  const handleDateFilter = () => {
    fetchData(startDate, endDate)
  }

  const handleResetDates = () => {
    setStartDate('')
    setEndDate('')
    fetchData('', '')
  }

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <div style={{ color: '#60a5fa', fontSize: 18 }}>Loading data...</div>
    </div>
  )

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 24px' }}>

      {/* Header */}
      <div style={{ marginBottom: 40 }}>
        <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
          <div>
            <h1 style={{ fontSize: 28, fontWeight: 700 }}>Weather Dashboard</h1>
            <p style={{ color: '#64748b', marginTop: 6 }}>Detroit, MI</p>
          </div>
          <button
            onClick={() => navigate('/')}
            style={{
              background: 'transparent',
              border: '1px solid #2d3748',
              color: '#94a3b8',
              borderRadius: 8,
              padding: '8px 18px',
              cursor: 'pointer',
              fontSize: 14
            }}
          >
            Back
          </button>
        </div>

        {/* Date Range Filter */}
        <div style={{
          background: '#1e2330',
          borderRadius: 12,
          padding: 16,
          display: 'flex',
          gap: 12,
          flexWrap: 'wrap',
          alignItems: 'flex-end'
        }}>
          <div>
            <label style={{ fontSize: 12, color: '#94a3b8', display: 'block', marginBottom: 6 }}>
              Start Date
            </label>
            <input
              type="date"
              value={startDate}
              onChange={(e) => setStartDate(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: 6,
                border: '1px solid #2d3748',
                background: '#0f1117',
                color: '#e2e8f0',
                fontSize: 14,
                cursor: 'pointer'
              }}
            />
          </div>
          <div>
            <label style={{ fontSize: 12, color: '#94a3b8', display: 'block', marginBottom: 6 }}>
              End Date
            </label>
            <input
              type="date"
              value={endDate}
              onChange={(e) => setEndDate(e.target.value)}
              style={{
                padding: '8px 12px',
                borderRadius: 6,
                border: '1px solid #2d3748',
                background: '#0f1117',
                color: '#e2e8f0',
                fontSize: 14,
                cursor: 'pointer'
              }}
            />
          </div>
          <button
            onClick={handleDateFilter}
            style={{
              background: '#3b82f6',
              color: '#fff',
              border: 'none',
              borderRadius: 6,
              padding: '8px 16px',
              fontSize: 14,
              fontWeight: 600,
              cursor: 'pointer'
            }}
          >
            Filter
          </button>
          <button
            onClick={handleResetDates}
            style={{
              background: 'transparent',
              color: '#60a5fa',
              border: '1px solid #60a5fa',
              borderRadius: 6,
              padding: '8px 16px',
              fontSize: 14,
              cursor: 'pointer'
            }}
          >
            Reset
          </button>
        </div>
      </div>

      {/* Charts */}
      <div style={{ display: 'flex', flexDirection: 'column', gap: 32 }}>
        <TempTrendChart data={trends} />
        <SparkFeaturesChart data={spark} />
        <PrecipChart data={trends} />
        <AnomalyTable data={anomalies} />
      </div>
    </div>
  )
}