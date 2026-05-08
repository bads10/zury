import { useState, useEffect } from 'react'
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, BarElement,
  Tooltip, Legend,
} from 'chart.js'
import { Bar } from 'react-chartjs-2'
import { getAnalytics } from '../api'

ChartJS.register(CategoryScale, LinearScale, BarElement, Tooltip, Legend)

const DEMO = {
  tryons_week: 47,
  conversion_rate: 23,
  top_garment: 'Robe Safran',
  daily: [12, 8, 15, 7, 20, 18, 24],
}
const DAYS = ['Lun', 'Mar', 'Mer', 'Jeu', 'Ven', 'Sam', 'Dim']

const CHART_OPTIONS = {
  responsive: true,
  plugins: { legend: { display: false } },
  scales: {
    x: {
      ticks:  { color: 'rgba(240,230,211,.55)', font: { family: 'DM Sans, system-ui' } },
      grid:   { color: 'rgba(212,168,67,.08)'  },
      border: { color: 'rgba(212,168,67,.15)'  },
    },
    y: {
      beginAtZero: true,
      ticks:  { color: 'rgba(240,230,211,.55)', font: { family: 'DM Sans, system-ui' } },
      grid:   { color: 'rgba(212,168,67,.08)'  },
      border: { color: 'rgba(212,168,67,.15)'  },
    },
  },
}

export default function Stats() {
  const sellerId = localStorage.getItem('zury_seller_id') || ''
  const [data,   setData]   = useState(null)
  const [isDemo, setIsDemo] = useState(false)

  useEffect(() => {
    getAnalytics(sellerId)
      .then(d => { setData(d); setIsDemo(false) })
      .catch(() => { setData(DEMO); setIsDemo(true) })
  }, [sellerId])

  const d = data || DEMO

  const chartData = {
    labels: DAYS,
    datasets: [{
      label: 'Try-ons',
      data: d.daily,
      backgroundColor: 'rgba(212,168,67,.7)',
      borderColor: '#D4A843',
      borderWidth: 1,
      borderRadius: 6,
    }],
  }

  return (
    <>
      <div className="page-header">
        <h1>Statistiques</h1>
      </div>

      {isDemo && (
        <div className="demo-badge">
          <svg width="12" height="12" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round">
            <circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><circle cx="12" cy="16" r=".5" fill="currentColor"/>
          </svg>
          Données de démonstration — analytics API à venir
        </div>
      )}

      {!data && (
        <div className="loading-center"><div className="spinner" /></div>
      )}

      {data && (
        <>
          <div className="metrics-grid">
            <div className="metric-card">
              <div className="metric-card__label">Try-ons cette semaine</div>
              <div className="metric-card__value">{d.tryons_week}</div>
              <div className="metric-card__sub">essayages virtuels</div>
            </div>
            <div className="metric-card">
              <div className="metric-card__label">Taux de conversion</div>
              <div className="metric-card__value">{d.conversion_rate}%</div>
              <div className="metric-card__sub">try-on → commande</div>
            </div>
            <div className="metric-card">
              <div className="metric-card__label">Top vêtement</div>
              <div className="metric-card__value metric-card__value--sm">{d.top_garment}</div>
              <div className="metric-card__sub">le plus essayé</div>
            </div>
          </div>

          <div className="chart-card">
            <h2>Try-ons — 7 derniers jours</h2>
            <Bar data={chartData} options={CHART_OPTIONS} />
          </div>
        </>
      )}
    </>
  )
}
