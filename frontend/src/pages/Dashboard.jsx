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

  useEffect(() => {
    Promise.all([
      axios.get('http://localhost:8000/api/trends'),
      axios.get('http://localhost:8000/api/anomalies'),
      axios.get('http://localhost:8000/api/spark-features'),
    ]).then(([t, a, s]) => {
      setTrends(t.data)
      setAnomalies(a.data)
      setSpark(s.data)
      setLoading(false)
    })
  }, [])

  if (loading) return (
    <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100vh' }}>
      <div style={{ color: '#60a5fa', fontSize: 18 }}>Loading data...</div>
    </div>
  )

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '32px 24px' }}>

      {/* Header */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 40 }}>
        <div>
          <h1 style={{ fontSize: 28, fontWeight: 700 }}>Weather Dashboard</h1>
          <p style={{ color: '#64748b', marginTop: 6 }}>Detroit, MI — last 90 days</p>
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