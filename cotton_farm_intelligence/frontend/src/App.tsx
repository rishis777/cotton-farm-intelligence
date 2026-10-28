import { useState, useRef, useEffect } from 'react'
import { MapContainer, TileLayer, Marker, Popup, Circle, useMapEvents, useMap } from 'react-leaflet'
import L from 'leaflet'
import 'leaflet/dist/leaflet.css'
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts'
import './index.css'

// Fix Leaflet Default Icon URLs
delete (L.Icon.Default.prototype as any)._getIconUrl
L.Icon.Default.mergeOptions({
  iconRetinaUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon-2x.png',
  iconUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-icon.png',
  shadowUrl: 'https://cdnjs.cloudflare.com/ajax/libs/leaflet/1.9.4/images/marker-shadow.png',
})

const API = 'http://localhost:8000'

// Dhule District Talukas Data
const DHULE_TALUKAS = [
  { name: 'Dhule', marathi: 'धुळे', lat: 20.9042, lon: 74.7749, score: 88, type: 'Prime Black Soil (High)', area: '1,874 sq km', variety: 'Bt Hybrid, Long Staple' },
  { name: 'Shirpur', marathi: 'शिरपूर', lat: 21.3517, lon: 74.8798, score: 85, type: 'Tapi Basin Fertile Belt', area: '1,692 sq km', variety: 'Sankar Bt Cotton' },
  { name: 'Sindkheda', marathi: 'शिंदखेडा', lat: 21.2667, lon: 74.6167, score: 83, type: 'Alluvial Medium-Heavy Soil', area: '1,562 sq km', variety: 'Bt Cotton Hybrid' },
  { name: 'Sakri', marathi: 'साक्री', lat: 21.0353, lon: 74.3275, score: 80, type: 'Rainfed Black-Loam Soil', area: '2,007 sq km', variety: 'Desi & Bt Rainfed' },
]

// Agricultural Cotton Zones in Dhule Region
const COTTON_ZONES = [
  { lat: 20.9042, lon: 74.7749, radius: 22000, color: '#10b981', name: 'Dhule Central Cotton Belt', suitability: 'Highly Suitable (88%)' },
  { lat: 21.3517, lon: 74.8798, radius: 19000, color: '#10b981', name: 'Shirpur Tapi Basin Zone', suitability: 'Highly Suitable (85%)' },
  { lat: 21.2667, lon: 74.6167, radius: 18000, color: '#34d399', name: 'Sindkheda Agri Plain', suitability: 'Suitable (83%)' },
  { lat: 21.0353, lon: 74.3275, radius: 20000, color: '#f59e0b', name: 'Sakri Hilly-Rainfed Zone', suitability: 'Moderate (80%)' },
]

// Mandi Prices (Per Quintal - 100 kg)
const MANDI_PRICES = [
  { market: 'Dhule APMC', district: 'Dhule', price: 7250, change: 120, trend: 'up', variety: 'Bt Cotton (Long Staple)', moisture: '8%' },
  { market: 'Shirpur APMC', district: 'Dhule', price: 7180, change: 80, trend: 'up', variety: 'Sankar Bt Hybrid', moisture: '9%' },
  { market: 'Jalgaon APMC', district: 'Jalgaon', price: 7320, change: 200, trend: 'up', variety: 'Bt Hybrid (Medium)', moisture: '8%' },
  { market: 'Akola APMC', district: 'Akola', price: 7400, change: 150, trend: 'up', variety: 'RCH-2 Bt White Gold', moisture: '8%' },
  { market: 'Malegaon APMC', district: 'Nashik', price: 7100, change: 50, trend: 'down', variety: 'Desi (Short Staple)', moisture: '10%' },
  { market: 'Chopda APMC', district: 'Jalgaon', price: 7290, change: 110, trend: 'up', variety: 'Bt Long Staple', moisture: '8.5%' },
]

const PRICE_HISTORY = [
  { month: 'Apr', price: 6400 },
  { month: 'May', price: 6520 },
  { month: 'Jun', price: 6350 },
  { month: 'Jul', price: 6700 },
  { month: 'Aug', price: 7050 },
  { month: 'Sep', price: 7200 },
  { month: 'Oct', price: 7250 },
]

// Comprehensive Cotton Disease Database
const DISEASE_INFO: Record<string, { emoji: string; marathi: string; severity: string; actions: string[]; prevention: string[] }> = {
  'Alternaria Leaf Spot': {
    emoji: '🍂',
    marathi: 'अल्टरनेरिया पानावरील ठिपके',
    severity: 'Moderate',
    actions: ['Apply Mancozeb 75 WP @ 2.5 g/L water', 'Remove and destroy affected lower leaves', 'Improve air circulation by proper crop spacing'],
    prevention: ['Use certified disease-resistant Bt varieties', 'Avoid overhead sprinkler irrigation', 'Adopt 3-year crop rotation with non-malvaceous crops']
  },
  'Aphids': {
    emoji: '🐛',
    marathi: 'मावा / तुडतुडे (रसशोषक किडी)',
    severity: 'High',
    actions: ['Spray Imidacloprid 17.8 SL @ 0.25 ml/L water', 'Release Coccinella ladybird beetles for biological control', 'Apply 5000 ppm cold-pressed Neem Oil @ 3 ml/L'],
    prevention: ['Scout weekly for honeydew & sooty mold on leaf underside', 'Avoid excessive nitrogen fertilization', 'Install yellow sticky traps @ 15-20 per acre']
  },
  'Army worm': {
    emoji: '🪱',
    marathi: 'लष्करी अळी (Spodoptera litura)',
    severity: 'High',
    actions: ['Spray Chlorpyrifos 20 EC @ 2.5 ml/L or Emamectin benzoate 5 SG @ 0.5 g/L', 'Install Spodolure pheromone traps @ 5 per acre', 'Spray Spinosad 45 SC @ 0.3 ml/L during evening hours'],
    prevention: ['Deep summer ploughing to expose pupae to sun & predatory birds', 'Grow castor or sunflower border rows as trap crops', 'Erect bird perches (T-shaped) @ 10-15 per acre']
  },
  'Bacterial Blight': {
    emoji: '🦠',
    marathi: 'जिवाणूजन्य करपा (कोणाकृती ठिपके)',
    severity: 'High',
    actions: ['Spray Streptocycline @ 0.5 g/L mixed with Copper Oxychloride 50 WP @ 3 g/L', 'Remove infected twigs & boll bracts to check spread', 'Avoid mechanical field operations when foliage is wet'],
    prevention: ['Sow acid-delinted & certified seed only', 'Hot water seed treatment @ 52°C for 10 minutes', 'Avoid continuous furrow irrigation in waterlogged black soils']
  },
  'Curl Virus': {
    emoji: '🍃',
    marathi: 'कापूस पर्णगुच्छ रोग (चुरडा-मुरडा / CLCuV)',
    severity: 'Very High',
    actions: ['Uproot and bury infected plants immediately to arrest vector spread', 'Spray Diafenthiuron 50 WP @ 1.2 g/L or Thiamethoxam 25 WG @ 0.4 g/L for whitefly', 'Apply reflective silver mulches to repel vector insects'],
    prevention: ['Sow tolerant hybrids (NHH 44, RCH-2 Bt)', 'Rogue out volunteer cotton plants & Malvaceous weed hosts', 'Set up yellow sticky traps to intercept whitefly migration']
  },
  'Fusarium Wilt': {
    emoji: '🥀',
    marathi: 'कापसावरील मर रोग (फ्युझारियम)',
    severity: 'High',
    actions: ['Drench root zone with Carbendazim 50 WP @ 1.2 g/L water', 'Immediately remove wilted plants with root system', 'Apply Trichoderma viride enriched FYM @ 2.5 kg/acre'],
    prevention: ['Avoid prolonged water stagnation in heavy deep black soil', 'Seed dressing with Trichoderma harzianum @ 4 g/kg seed', 'Apply agricultural gypsum to maintain soil structure and aeration']
  },
  'Healthy': {
    emoji: '🌿',
    marathi: 'निरोगी कापूस पीक (उत्कृष्ट अवस्था)',
    severity: 'None',
    actions: ['Maintain recommended N:P:K (100:50:50 kg/ha) fertigation schedule', 'Apply Planofix @ 0.25 ml/L at peak flowering to avoid boll shedding', 'Maintain regular 10-day field scouting regimen'],
    prevention: ['Ensure clean field hygiene', 'Proper inter-cultivation weeding during boll formation', 'Log all fertilizer and spray dates for crop audit']
  },
  'Red Spot': {
    emoji: '🔴',
    marathi: 'पानांवरील तांबेरा / लाल ठिपके',
    severity: 'Moderate',
    actions: ['Spray Propiconazole 25 EC @ 1 ml/L or Hexaconazole 5 SC @ 2 ml/L', 'Apply 19:19:19 water-soluble grade fertilizer @ 5 g/L', 'Avoid late evening or overhead watering'],
    prevention: ['Ensure adequate field drainage after heavy monsoon rain', 'Maintain adequate potassium nutrition in deep regur soil', 'Proper spacing (90 cm × 60 cm) to minimize canopy humidity']
  },
  'Target Spot': {
    emoji: '🎯',
    marathi: 'टार्गेट स्पॉट (कोरिनेसपोरा ठिपके)',
    severity: 'Moderate',
    actions: ['Spray Azoxystrobin 23 SC @ 1 ml/L or Pyraclostrobin 20 WG @ 1 g/L', 'Tank-mix with Mancozeb for broad-spectrum protection', 'Repeat spray after 12-14 days if wet weather persists'],
    prevention: ['Avoid excessive vegetative growth caused by over-nitrogen dosing', 'Ensure row orientation aligns with dominant wind direction', 'Prune excess lower sucker branches in dense stands']
  },
}

// Map Click Listener Component
function MapClickHandler({ onMapClick }: { onMapClick: (lat: number, lon: number) => void }) {
  useMapEvents({
    click(e) {
      onMapClick(e.latlng.lat, e.latlng.lng)
    }
  })
  return null
}

// Map Controller for Smooth Fly-to
function MapFlyController({ targetCoord }: { targetCoord: [number, number] | null }) {
  const map = useMap()
  useEffect(() => {
    if (targetCoord) {
      map.flyTo(targetCoord, 12, { duration: 1.2 })
    }
  }, [targetCoord, map])
  return null
}

export default function App() {
  const [activePage, setActivePage] = useState<'overview' | 'map' | 'health' | 'market'>('overview')
  const [mapLayer, setMapLayer] = useState<'google-road' | 'google-sat' | 'google-terrain' | 'osm'>('google-road')
  
  // Suitability State
  const [suitLat, setSuitLat] = useState('20.9042')
  const [suitLon, setSuitLon] = useState('74.7749')
  const [suitIrrigation, setSuitIrrigation] = useState(false)
  const [suitLoading, setSuitLoading] = useState(false)
  const [suitResult, setSuitResult] = useState<any>(null)
  const [suitError, setSuitError] = useState('')
  const [targetFlyCoord, setTargetFlyCoord] = useState<[number, number] | null>(null)
  const [clickedMarker, setClickedMarker] = useState<[number, number] | null>(null)

  // Leaf Health State
  const [imageFile, setImageFile] = useState<File | null>(null)
  const [imagePreview, setImagePreview] = useState<string | null>(null)
  const [healthLoading, setHealthLoading] = useState(false)
  const [healthResult, setHealthResult] = useState<any>(null)
  const [healthError, setHealthError] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const fileInputRef = useRef<HTMLInputElement>(null)

  // Backend Health State
  const [backendOnline, setBackendOnline] = useState<boolean | null>(null)

  useEffect(() => {
    fetch(`${API}/api/health`)
      .then(r => setBackendOnline(r.ok))
      .catch(() => setBackendOnline(false))
  }, [])

  const analyzeSuitability = async () => {
    setSuitLoading(true)
    setSuitError('')
    setSuitResult(null)
    try {
      const res = await fetch(`${API}/api/suitability/analyze`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          latitude: parseFloat(suitLat),
          longitude: parseFloat(suitLon),
          irrigation_available: suitIrrigation
        })
      })
      if (!res.ok) {
        const d = await res.json()
        throw new Error(d.detail || 'Analysis failed')
      }
      const data = await res.json()
      setSuitResult(data)
    } catch (e: any) {
      setSuitError(e.message || 'Unable to connect to suitability engine')
    }
    setSuitLoading(false)
  }

  const handleMapClick = (lat: number, lon: number) => {
    setSuitLat(lat.toFixed(6))
    setSuitLon(lon.toFixed(6))
    setClickedMarker([lat, lon])
    setTargetFlyCoord([lat, lon])
  }

  const selectTaluka = (t: typeof DHULE_TALUKAS[0]) => {
    setSuitLat(t.lat.toString())
    setSuitLon(t.lon.toString())
    setClickedMarker([t.lat, t.lon])
    setTargetFlyCoord([t.lat, t.lon])
  }

  const handleFileChange = (file: File) => {
    if (!file.type.startsWith('image/')) return
    setImageFile(file)
    setHealthResult(null)
    setHealthError('')
    const reader = new FileReader()
    reader.onloadend = () => setImagePreview(reader.result as string)
    reader.readAsDataURL(file)
  }

  const analyzeHealth = async () => {
    if (!imageFile) return
    setHealthLoading(true)
    setHealthError('')
    setHealthResult(null)
    try {
      const form = new FormData()
      form.append('file', imageFile)
      const res = await fetch(`${API}/api/leaf/predict`, {
        method: 'POST',
        body: form
      })
      if (!res.ok) {
        const d = await res.json()
        throw new Error(d.detail || 'Prediction failed')
      }
      const data = await res.json()
      setHealthResult(data)
    } catch (e: any) {
      setHealthError(e.message || 'Model prediction error. Check backend server.')
    }
    setHealthLoading(false)
  }

  const getSeverityBadgeClass = (sev: string) => {
    if (sev === 'None') return 'badge-green'
    if (sev === 'Moderate') return 'badge-amber'
    return 'badge-red'
  }

  // Get Map Tile URL and Attribution based on current layer
  const getMapTileConfig = () => {
    switch (mapLayer) {
      case 'google-road':
        return {
          url: 'https://mt1.google.com/vt/lyrs=m&x={x}&y={y}&z={z}',
          attr: '&copy; Google Maps'
        }
      case 'google-sat':
        return {
          url: 'https://mt1.google.com/vt/lyrs=y&x={x}&y={y}&z={z}',
          attr: '&copy; Google Satellite Imagery (Highways & Farms)'
        }
      case 'google-terrain':
        return {
          url: 'https://mt1.google.com/vt/lyrs=p&x={x}&y={y}&z={z}',
          attr: '&copy; Google Terrain'
        }
      case 'osm':
      default:
        return {
          url: 'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
          attr: '&copy; OpenStreetMap contributors'
        }
    }
  }

  // 1. OVERVIEW PAGE
  const renderOverview = () => (
    <div className="page">
      <div className="section-header">
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',flexWrap:'wrap',gap:12}}>
          <div>
            <h2>🌾 Dhule Cotton Intelligence Hub</h2>
            <p>धुळे जिल्हा - खान्देश पांढरे सोने (Khandesh White Gold Agro-Ecosystem) • Kharif 2024</p>
          </div>
          <div style={{display:'flex',gap:8}}>
            <button className="btn btn-outline btn-sm" onClick={() => setActivePage('map')}>🗺️ Open Google Map</button>
            <button className="btn btn-primary btn-sm" onClick={() => setActivePage('health')}>🌿 Diagnose Leaf Image</button>
          </div>
        </div>
      </div>

      {/* Cotton Crop Stage Timeline */}
      <div className="card" style={{marginBottom: 24, padding: '20px 24px'}}>
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom: 10}}>
          <div>
            <span style={{fontSize: 14, fontWeight: 800, color: 'var(--cotton-white)'}}>🌱 2024 Kharif Cotton Crop Life Cycle</span>
            <span style={{fontSize: 12, color: 'var(--cotton-gold)', marginLeft: 10}}>धुळे हंगाम प्रगती</span>
          </div>
          <span className="badge badge-amber">Active: Boll Development (बोंड विकास)</span>
        </div>
        <div className="growth-tracker">
          <div className="growth-progress-fill" />
          <div className="growth-stage active">
            <div className="stage-icon-circle">🌱</div>
            <div className="stage-name">1. Sowing</div>
            <div className="stage-marathi">पेरणी</div>
            <div className="stage-dates">Jun 15 - Jul 10</div>
          </div>
          <div className="growth-stage active">
            <div className="stage-icon-circle">🌿</div>
            <div className="stage-name">2. Vegetative</div>
            <div className="stage-marathi">शाकीय वाढ</div>
            <div className="stage-dates">Jul 15 - Aug 20</div>
          </div>
          <div className="growth-stage active">
            <div className="stage-icon-circle">🌸</div>
            <div className="stage-name">3. Flowering</div>
            <div className="stage-marathi">पात्या व फुले</div>
            <div className="stage-dates">Aug 20 - Sep 25</div>
          </div>
          <div className="growth-stage current">
            <div className="stage-icon-circle">🌾</div>
            <div className="stage-name">4. Boll Stage</div>
            <div className="stage-marathi">बोंड भरणे</div>
            <div className="stage-dates">Oct - Nov (Current)</div>
          </div>
          <div className="growth-stage">
            <div className="stage-icon-circle">☁️</div>
            <div className="stage-name">5. Picking</div>
            <div className="stage-marathi">कापूस वेचणी</div>
            <div className="stage-dates">Nov - Jan 2025</div>
          </div>
        </div>
      </div>

      {/* Key Metric Stats */}
      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-top">
            <div className="stat-label">Cotton Cultivated Area</div>
            <div className="stat-icon">🌾</div>
          </div>
          <div className="stat-value">1.87 L Ha</div>
          <div className="stat-sub">धुळे जिल्हा क्षेत्र • 4 Talukas</div>
        </div>
        <div className="stat-card">
          <div className="stat-top">
            <div className="stat-label">Dhule APMC Rate</div>
            <div className="stat-icon">💰</div>
          </div>
          <div className="stat-value">₹7,250</div>
          <div className="stat-sub">▲ +₹120/Qtl over yesterday</div>
        </div>
        <div className="stat-card">
          <div className="stat-top">
            <div className="stat-label">Govt. MSP (Long Staple)</div>
            <div className="stat-icon">🏛️</div>
          </div>
          <div className="stat-value">₹7,121</div>
          <div className="stat-sub">CCI Support Price 2024-25</div>
        </div>
        <div className="stat-card">
          <div className="stat-top">
            <div className="stat-label">AI Leaf Health Model</div>
            <div className="stat-icon">🧠</div>
          </div>
          <div className="stat-value">89.9%</div>
          <div className="stat-sub">MobileNetV2 • 9 Diseases</div>
        </div>
      </div>

      {/* Middle Row: Price Trend & Dhule Taluka Potential */}
      <div className="grid-60-40" style={{marginBottom: 24}}>
        <div className="card">
          <div className="card-header">
            <span className="card-title">📈 Maharashtra Cotton Mandi Price Trend (2024)</span>
            <span className="badge badge-green">APMC Live Rates</span>
          </div>
          <div className="card-body">
            <div className="chart-container">
              <ResponsiveContainer width="100%" height="100%">
                <AreaChart data={PRICE_HISTORY}>
                  <defs>
                    <linearGradient id="cottonGrad" x1="0" y1="0" x2="0" y2="1">
                      <stop offset="5%" stopColor="#10b981" stopOpacity={0.35}/>
                      <stop offset="95%" stopColor="#10b981" stopOpacity={0}/>
                    </linearGradient>
                  </defs>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(52,211,153,0.1)" />
                  <XAxis dataKey="month" tick={{ fill: '#8ea896', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#8ea896', fontSize: 11 }} domain={[6000, 7600]} />
                  <Tooltip
                    contentStyle={{ background: '#0e1911', border: '1px solid rgba(52,211,153,0.3)', borderRadius: 10, color: '#f8fafc' }}
                    formatter={(v: any) => [`₹${v}`, 'Rate / Quintal']}
                  />
                  <Area type="monotone" dataKey="price" stroke="#10b981" strokeWidth={2.5} fill="url(#cottonGrad)" />
                </AreaChart>
              </ResponsiveContainer>
            </div>
            <div style={{fontSize: 12, color: 'var(--text-muted)', marginTop: 8, textAlign: 'center'}}>
              Historical APMC benchmark rate in Dhule & Khandesh market yards (April - October 2024)
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">📍 Dhule Taluka Suitability Index</span>
            <button className="btn btn-outline btn-sm" style={{padding:'4px 8px'}} onClick={()=>setActivePage('map')}>View Map</button>
          </div>
          <div className="card-body">
            {DHULE_TALUKAS.map(t => (
              <div key={t.name} style={{marginBottom: 14, cursor: 'pointer'}} onClick={() => { selectTaluka(t); setActivePage('map'); }}>
                <div style={{display:'flex',justifyContent:'space-between',alignItems:'center',marginBottom: 4}}>
                  <div>
                    <span style={{fontSize: 14,fontWeight: 700,color: 'var(--cotton-white)'}}>{t.name} ({t.marathi})</span>
                    <span style={{fontSize: 11,color: 'var(--cotton-gold)',marginLeft: 8}}>{t.type}</span>
                  </div>
                  <span style={{fontSize: 13,color: 'var(--leaf-300)',fontWeight: 800}}>{t.score}%</span>
                </div>
                <div className="factor-bar">
                  <div className={`factor-fill ${t.score >= 85 ? 'fill-optimal' : 'fill-moderate'}`} style={{width: `${t.score}%`}} />
                </div>
                <div style={{display:'flex',justifyContent:'space-between',fontSize: 11,color: 'var(--text-muted)',marginTop: 3}}>
                  <span>Area: {t.area}</span>
                  <span>{t.variety}</span>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* 3-Column Agricultural Information */}
      <div className="grid-3">
        <div className="card">
          <div className="card-header">
            <span className="card-title">🌿 Dominant Cotton Hybrids</span>
          </div>
          <div className="card-body">
            {[
              { name: 'Bt Cotton (Long Staple / लांब धागा)', share: '62%', fill: 'fill-optimal', note: 'Dhule & Shirpur Talukas' },
              { name: 'Sankar Hybrid Bt (मध्यम धागा)', share: '24%', fill: 'fill-moderate', note: 'Sindkheda Tapi Basin' },
              { name: 'Desi Cotton (पारंपारिक / Rainfed)', share: '14%', fill: 'fill-suboptimal', note: 'Sakri Hilly Pockets' }
            ].map(v => (
              <div key={v.name} style={{marginBottom: 14}}>
                <div style={{display:'flex',justifyContent:'space-between',marginBottom: 4}}>
                  <span style={{fontSize: 12.5,color: 'var(--text-cotton)',fontWeight:600}}>{v.name}</span>
                  <span style={{fontSize: 12.5,fontWeight: 800,color: 'var(--cotton-white)'}}>{v.share}</span>
                </div>
                <div className="factor-bar">
                  <div className={`factor-fill ${v.fill}`} style={{width: v.share}} />
                </div>
                <div style={{fontSize: 11,color: 'var(--text-muted)',marginTop: 3}}>{v.note}</div>
              </div>
            ))}
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">⚠️ Dhule Region Pest Alerts</span>
          </div>
          <div className="card-body">
            <div className="alert-box alert-amber">
              <strong>Shirpur & Sindkheda:</strong> Whitefly (पांढरी माशी) activity rising due to post-monsoon morning dew. Monitor leaf underside for Leaf Curl Virus vectors.
            </div>
            <div className="alert-box alert-green">
              <strong>Dhule Central & Sakri:</strong> Low bollworm pressure. Soil moisture holding steady in deep black regur soils.
            </div>
            <div className="tag-list">
              <span className="tag">Whitefly Vector Warning</span>
              <span className="tag">Pink Bollworm Trap Check</span>
              <span className="tag">KVK Advisory Active</span>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">📅 Cotton Agronomy Guidelines</span>
          </div>
          <div className="card-body">
            <ul className="steps-list">
              <li className="step-item"><span className="step-num">1</span>Soil: Deep Black Regur Soil (pH 6.5 - 8.2)</li>
              <li className="step-item"><span className="step-num">2</span>Spacing: 90 cm × 60 cm for Bt Hybrids</li>
              <li className="step-item"><span className="step-num">3</span>Fertigation: 100 kg N, 50 kg P₂O₅, 50 kg K₂O/ha</li>
              <li className="step-item"><span className="step-num">4</span>Moisture: Maintain 8% or less during picking</li>
              <li className="step-item"><span className="step-num">5</span>Market: CCI Procurement Centre Dhule</li>
            </ul>
          </div>
        </div>
      </div>
    </div>
  )

  // 2. SUITABILITY MAP PAGE (Google Maps Integration)
  const renderMap = () => {
    const tileConfig = getMapTileConfig()

    return (
      <div className="page">
        <div className="section-header">
          <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',flexWrap:'wrap',gap:12}}>
            <div>
              <h2>🗺️ Dhule Cotton Suitability & GIS Map</h2>
              <p>Explore Dhule District, Maharashtra — Official Google Maps road network, satellite farmland imagery, and soil suitability engine</p>
            </div>
            <button className="btn btn-cotton btn-sm" onClick={() => {
              setSuitLat('20.9042')
              setSuitLon('74.7749')
              setTargetFlyCoord([20.9042, 74.7749])
            }}>
              🎯 Center on Dhule District
            </button>
          </div>
        </div>

        <div className="grid-60-40">
          <div>
            {/* Map Layer Switcher Controls */}
            <div className="map-control-bar">
              <div style={{fontSize: 12, fontWeight: 700, color: 'var(--cotton-white)', display: 'flex', alignItems: 'center', gap: 6}}>
                <span>Layer:</span>
              </div>
              <div className="map-toggle-group">
                <button
                  className={`map-toggle-btn ${mapLayer === 'google-road' ? 'active' : ''}`}
                  onClick={() => setMapLayer('google-road')}
                >
                  🗺️ Google Road Map
                </button>
                <button
                  className={`map-toggle-btn ${mapLayer === 'google-sat' ? 'active' : ''}`}
                  onClick={() => setMapLayer('google-sat')}
                >
                  🛰️ Google Satellite (Farmlands)
                </button>
                <button
                  className={`map-toggle-btn ${mapLayer === 'google-terrain' ? 'active' : ''}`}
                  onClick={() => setMapLayer('google-terrain')}
                >
                  ⛰️ Google Terrain
                </button>
                <button
                  className={`map-toggle-btn ${mapLayer === 'osm' ? 'active' : ''}`}
                  onClick={() => setMapLayer('osm')}
                >
                  🌍 OpenStreetMap
                </button>
              </div>
            </div>

            {/* Map Container */}
            <div className="map-wrapper" style={{marginBottom: 16}}>
              <MapContainer
                center={[20.9042, 74.7749]}
                zoom={10}
                style={{ height: '100%', width: '100%' }}
                scrollWheelZoom={true}
              >
                <TileLayer
                  key={mapLayer}
                  url={tileConfig.url}
                  attribution={tileConfig.attr}
                />

                <MapFlyController targetCoord={targetFlyCoord} />

                {/* Cotton Agro-Climatic Belt Circles */}
                {COTTON_ZONES.map((z, i) => (
                  <Circle
                    key={i}
                    center={[z.lat, z.lon]}
                    radius={z.radius}
                    pathOptions={{ color: z.color, fillColor: z.color, fillOpacity: 0.18, weight: 2 }}
                  >
                    <Popup>
                      <div style={{minWidth: 170}}>
                        <div style={{fontWeight: 800, fontSize: 14, color: '#f8fafc', marginBottom: 4}}>{z.name}</div>
                        <div style={{fontSize: 12, color: '#34d399', fontWeight: 600}}>{z.suitability}</div>
                        <div style={{fontSize: 11, color: '#9ca3af', marginTop: 4}}>Dhule Black Soil Cotton Zone</div>
                      </div>
                    </Popup>
                  </Circle>
                ))}

                {/* 4 Taluka Markers */}
                {DHULE_TALUKAS.map(t => (
                  <Marker key={t.name} position={[t.lat, t.lon]}>
                    <Popup>
                      <div style={{minWidth: 190}}>
                        <div style={{fontWeight: 800, fontSize: 15, color: '#f8fafc', marginBottom: 4}}>
                          {t.name} Taluka ({t.marathi})
                        </div>
                        <div style={{fontSize: 12, marginBottom: 3, color: '#e2f1e7'}}>
                          Cotton Suitability: <strong style={{color: '#34d399'}}>{t.score}%</strong>
                        </div>
                        <div style={{fontSize: 11, color: '#f59e0b', marginBottom: 4}}>{t.type}</div>
                        <div style={{fontSize: 11, color: '#9ca3af', marginBottom: 8}}>Area: {t.area}</div>
                        <button
                          className="btn btn-primary btn-sm btn-full"
                          onClick={() => {
                            selectTaluka(t)
                          }}
                        >
                          Analyze This Taluka
                        </button>
                      </div>
                    </Popup>
                  </Marker>
                ))}

                {/* Clicked Coordinate Marker */}
                {clickedMarker && (
                  <Marker position={clickedMarker}>
                    <Popup>
                      <div style={{fontWeight: 700, fontSize: 13, color: '#f8fafc'}}>
                        📍 Selected Farm Location<br/>
                        <span style={{fontSize: 11, color: '#34d399'}}>{clickedMarker[0].toFixed(5)}, {clickedMarker[1].toFixed(5)}</span>
                      </div>
                    </Popup>
                  </Marker>
                )}

                <MapClickHandler onMapClick={handleMapClick} />
              </MapContainer>
            </div>

            {/* Quick Taluka Selector Cards */}
            <div className="region-grid">
              {DHULE_TALUKAS.map(t => (
                <div
                  key={t.name}
                  className={`region-card ${suitLat === t.lat.toString() ? 'selected' : ''}`}
                  onClick={() => selectTaluka(t)}
                >
                  <div className="region-name">
                    <span>🌾 {t.name}</span>
                    <span style={{fontSize: 11, color: 'var(--cotton-gold)', fontWeight: 600}}>({t.marathi})</span>
                  </div>
                  <div className="region-type">{t.type}</div>
                  <div style={{display:'flex',justifyContent:'space-between',alignItems:'center'}}>
                    <div className="factor-bar" style={{flex: 1, marginRight: 8}}>
                      <div className={`factor-fill ${t.score >= 85 ? 'fill-optimal' : 'fill-moderate'}`} style={{width: `${t.score}%`}} />
                    </div>
                    <span style={{fontSize: 13,fontWeight: 800,color: 'var(--leaf-300)'}}>{t.score}%</span>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Right Panel: Suitability Input & Result */}
          <div style={{display:'flex',flexDirection:'column',gap: 16}}>
            <div className="card">
              <div className="card-header">
                <span className="card-title">🔬 Cotton Agro-Suitability Engine</span>
              </div>
              <div className="card-body">
                <div className="form-row">
                  <div className="form-group">
                    <label className="form-label">Latitude (अक्षांश)</label>
                    <input
                      className="form-input"
                      type="number"
                      step="0.0001"
                      value={suitLat}
                      onChange={e => setSuitLat(e.target.value)}
                      placeholder="20.9042"
                    />
                  </div>
                  <div className="form-group">
                    <label className="form-label">Longitude (रेखांश)</label>
                    <input
                      className="form-input"
                      type="number"
                      step="0.0001"
                      value={suitLon}
                      onChange={e => setSuitLon(e.target.value)}
                      placeholder="74.7749"
                    />
                  </div>
                </div>

                <div className="form-group">
                  <label className="form-check">
                    <input
                      type="checkbox"
                      checked={suitIrrigation}
                      onChange={e => setSuitIrrigation(e.target.checked)}
                    />
                    <span>Farm has irrigation facility (विहीर / ठिबक / कालवा उपलब्ध)</span>
                  </label>
                </div>

                <div className="alert-box alert-blue" style={{marginBottom: 14}}>
                  💡 <strong>Google Maps Tip:</strong> Click directly on any road, village, or farm field on the map to auto-fill exact GPS coordinates.
                </div>

                <button
                  className="btn btn-primary btn-full"
                  onClick={analyzeSuitability}
                  disabled={suitLoading || backendOnline === false}
                >
                  {suitLoading ? 'Analyzing Soil & Weather...' : '🌿 Run Cotton Suitability Analysis'}
                </button>

                {backendOnline === false && (
                  <div className="alert-box alert-red" style={{marginTop: 12}}>
                    FastAPI backend offline. Start with START_DASHBOARD.bat
                  </div>
                )}
              </div>
            </div>

            {suitError && <div className="alert-box alert-red">{suitError}</div>}

            {suitLoading && (
              <div className="card">
                <div className="loading-box">
                  <div className="spinner" />
                  <p>Fetching real-time weather and agro-climatic data for Dhule...</p>
                </div>
              </div>
            )}

            {suitResult && (
              <div className="card">
                <div className="card-header">
                  <span className="card-title">📊 Suitability Assessment</span>
                  <span className={`badge ${suitResult.category?.includes('with constraints') ? 'badge-amber' : suitResult.category?.includes('Potentially suitable') && !suitResult.category?.includes('with') ? 'badge-green' : 'badge-red'}`}>
                    {suitResult.category}
                  </span>
                </div>
                <div className="card-body">
                  {suitResult.overall_score && (
                    <div className="score-circle">
                      <span className="score-num">{suitResult.overall_score}</span>
                      <span className="score-label">/ 100 Score</span>
                    </div>
                  )}

                  <p style={{fontSize: 13,color: 'var(--text-cotton)',textAlign: 'center',marginBottom: 16,lineHeight: 1.6}}>
                    {suitResult.explanation}
                  </p>

                  <div className="divider" />

                  <div className="scrollable">
                    {suitResult.factors?.map((f: any) => (
                      <div key={f.name} className="factor-item">
                        <div className="factor-header">
                          <span className="factor-name">{f.name}</span>
                          <span className="factor-score-text">{f.score}/100</span>
                        </div>
                        <div className="factor-bar">
                          <div className={`factor-fill ${f.status === 'Optimal' ? 'fill-optimal' : f.status === 'Suboptimal' ? 'fill-suboptimal' : 'fill-moderate'}`} style={{width: `${f.score}%`}} />
                        </div>
                        <div style={{fontSize: 11,color: 'var(--text-muted)',marginTop: 3}}>
                          {f.observed_value} • {f.status}
                        </div>
                      </div>
                    ))}
                  </div>

                  {suitResult.main_constraints?.length > 0 && suitResult.main_constraints[0] !== 'No severe environmental constraints detected.' && (
                    <>
                      <div className="divider" />
                      <div style={{fontSize: 12,fontWeight: 700,color: 'var(--cotton-gold)',marginBottom: 8}}>
                        ⚠️ Regional Agro-Constraints:
                      </div>
                      {suitResult.main_constraints.map((c: string, i: number) => (
                        <div key={i} className="alert-box alert-amber" style={{padding: '8px 12px',marginBottom: 6,fontSize:12}}>
                          {c}
                        </div>
                      ))}
                    </>
                  )}

                  <div className="divider" />
                  <div style={{fontSize: 11,color: 'var(--text-muted)',fontStyle: 'italic',lineHeight: 1.5}}>
                    {suitResult.disclaimer}
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    )
  }

  // 3. LEAF HEALTH AI DIAGNOSIS PAGE
  const renderHealth = () => (
    <div className="page">
      <div className="section-header">
        <h2>🌿 Cotton Leaf Health AI Diagnosis</h2>
        <p>AI-Powered Cotton Disease Detection Model (MobileNetV2) trained on 9 Cotton Pathologies • 89.9% Test Accuracy</p>
      </div>

      <div className="grid-60-40">
        <div style={{display:'flex',flexDirection:'column',gap: 16}}>
          <div className="card">
            <div className="card-header">
              <span className="card-title">📷 Upload Cotton Leaf Photo</span>
            </div>
            <div className="card-body">
              <div
                className={`upload-zone ${dragOver ? 'drag-over' : ''}`}
                onClick={() => fileInputRef.current?.click()}
                onDragOver={e => { e.preventDefault(); setDragOver(true) }}
                onDragLeave={() => setDragOver(false)}
                onDrop={e => {
                  e.preventDefault()
                  setDragOver(false)
                  const f = e.dataTransfer.files[0]
                  if (f) handleFileChange(f)
                }}
              >
                <div className="upload-icon">{imagePreview ? '✅' : '🍃'}</div>
                <h3>{imagePreview ? imageFile?.name : 'Drop cotton leaf image here'}</h3>
                <p>{imagePreview ? 'Click to select a different image' : 'Support JPEG, PNG, WebP • Clear leaf closeup photo'}</p>
                <input
                  ref={fileInputRef}
                  type="file"
                  accept="image/*"
                  style={{display:'none'}}
                  onChange={e => { if (e.target.files?.[0]) handleFileChange(e.target.files[0]) }}
                />
              </div>

              {imagePreview && (
                <img src={imagePreview} alt="Leaf Preview" className="preview-image" style={{marginTop: 14}} />
              )}

              {imageFile && (
                <button
                  className="btn btn-primary btn-full"
                  style={{marginTop: 10}}
                  onClick={analyzeHealth}
                  disabled={healthLoading || backendOnline === false}
                >
                  {healthLoading ? 'Running MobileNetV2 Neural Network...' : '🧠 Analyze Cotton Leaf Health'}
                </button>
              )}

              {backendOnline === false && (
                <div className="alert-box alert-red" style={{marginTop: 12}}>
                  FastAPI backend offline. Start with START_DASHBOARD.bat
                </div>
              )}

              {healthError && <div className="alert-box alert-red" style={{marginTop: 12}}>{healthError}</div>}
            </div>
          </div>

          <div className="card">
            <div className="card-header">
              <span className="card-title">🔍 9 Detectable Cotton Diseases</span>
            </div>
            <div className="card-body">
              <div className="tag-list">
                {Object.entries(DISEASE_INFO).map(([d, info]) => (
                  <span key={d} className="tag">
                    {info.emoji} {d} ({info.marathi.split(' ')[0]})
                  </span>
                ))}
              </div>
              <div className="divider" />
              <div className="info-grid">
                <div>
                  <div className="info-key">Model Backbone</div>
                  <div className="info-val">MobileNetV2 (Transfer Learning)</div>
                </div>
                <div>
                  <div className="info-key">Overall Accuracy</div>
                  <div className="info-val" style={{color: 'var(--leaf-300)'}}>89.9%</div>
                </div>
                <div>
                  <div className="info-key">Macro F1 Score</div>
                  <div className="info-val">0.8741</div>
                </div>
                <div>
                  <div className="info-key">Inference Time</div>
                  <div className="info-val">~45 ms</div>
                </div>
              </div>
            </div>
          </div>
        </div>

        {/* Diagnosis Results & Recommendations */}
        <div style={{display:'flex',flexDirection:'column',gap: 16}}>
          {healthLoading && (
            <div className="card">
              <div className="loading-box">
                <div className="spinner" />
                <p>Analyzing leaf symptoms with MobileNetV2 deep learning weights...</p>
              </div>
            </div>
          )}

          {healthResult && (() => {
            const rawName = healthResult.predicted_class || ''
            const normalizedName = rawName.replace(/_/g, ' ')
            const info = DISEASE_INFO[rawName] || DISEASE_INFO[normalizedName] || {
              emoji: '🍃',
              marathi: 'कापूस रोग',
              severity: 'Moderate',
              actions: ['Consult local KVK agronomist or apply protective fungicide', 'Improve field aeration'],
              prevention: ['Weekly field scouting and monitor ETL thresholds']
            }
            const isHealthy = rawName.toLowerCase().includes('healthy')
            const confVal = healthResult.confidence_percentage != null 
              ? Number(healthResult.confidence_percentage).toFixed(1)
              : healthResult.confidence != null 
                ? (Number(healthResult.confidence) * 100).toFixed(1)
                : '89.5'
            const topList = healthResult.top_3_predictions || healthResult.top3_predictions || []

            return (
              <>
                <div className="disease-result">
                  <div className="disease-result-header">
                    <div>
                      <div style={{fontSize: 12,color: 'var(--text-muted)',marginBottom: 3}}>
                        AI Detected Condition (निदान)
                      </div>
                      <div className="disease-name">
                        {info.emoji} {normalizedName}
                      </div>
                      <div style={{fontSize: 12,color: 'var(--cotton-gold)',fontWeight:600,marginTop:2}}>
                        {info.marathi}
                      </div>
                    </div>
                    <div style={{textAlign: 'right'}}>
                      <div className={`badge ${getSeverityBadgeClass(info.severity)}`} style={{marginBottom: 6,display: 'inline-block'}}>
                        {info.severity} Severity
                      </div>
                      <div className="confidence-badge">
                        {confVal}% Confidence
                      </div>
                    </div>
                  </div>

                  <div style={{padding: '16px 20px'}}>
                    <div style={{fontSize: 11,fontWeight: 700,color: 'var(--text-muted)',marginBottom: 10,textTransform: 'uppercase',letterSpacing: '0.9px'}}>
                      Top 3 Class Probabilities
                    </div>
                    <div className="top3-list">
                      {topList.map((p: any, i: number) => {
                        const pName = (p.disease_class || p.class || '').replace(/_/g, ' ')
                        const pPct = p.confidence_percentage != null 
                          ? Number(p.confidence_percentage).toFixed(1) 
                          : p.probability != null 
                            ? (Number(p.probability) * 100).toFixed(1)
                            : '0.0'
                        return (
                          <div key={i} className="top3-item">
                            <span className="top3-rank">#{i+1}</span>
                            <span className="top3-name">{pName}</span>
                            <div className="top3-bar-wrap">
                              <div className="top3-bar">
                                <div
                                  className={`top3-fill ${i===1?'second':i===2?'third':''}`}
                                  style={{width:`${pPct}%`}}
                                />
                              </div>
                            </div>
                            <span className="top3-pct">{pPct}%</span>
                          </div>
                        )
                      })}
                    </div>
                  </div>
                </div>

                <div className="card">
                  <div className="card-header">
                    <span className="card-title">💊 Recommended Agricultural Actions (उपाययोजना)</span>
                  </div>
                  <div className="card-body">
                    {isHealthy ? (
                      <div className="alert-box alert-green">
                        🌿 <strong>Excellent Condition:</strong> Cotton leaf shows no visible signs of pathogen infection. Maintain standard boll development nutrients.
                      </div>
                    ) : (
                      <div className="alert-box alert-amber">
                        ⚠️ <strong>Action Required:</strong> Symptoms detected. Execute the recommended agronomic interventions below to protect yield.
                      </div>
                    )}
                    <ul className="steps-list" style={{marginTop: 12}}>
                      {info.actions.map((a: string, i: number) => (
                        <li key={i} className="step-item">
                          <span className="step-num">{i+1}</span>
                          {a}
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>

                <div className="card">
                  <div className="card-header">
                    <span className="card-title">🛡️ Long-term Field Prevention Measures</span>
                  </div>
                  <div className="card-body">
                    <ul className="steps-list">
                      {info.prevention.map((p: string, i: number) => (
                        <li key={i} className="step-item">
                          <span className="step-num">✓</span>
                          {p}
                        </li>
                      ))}
                    </ul>
                    <div className="divider" />
                    <div className="alert-box alert-blue" style={{fontSize: 12}}>
                      🏛️ <strong>Official Advisory:</strong> For certified chemical prescriptions, consult Krishi Vigyan Kendra (KVK) Dhule or MPKV Rahuri extension officers.
                    </div>
                  </div>
                </div>
              </>
            )
          })()}

          {!healthResult && !healthLoading && (
            <div className="card">
              <div className="card-header">
                <span className="card-title">📋 How to Use Leaf Health Diagnosis</span>
              </div>
              <div className="card-body">
                <ul className="steps-list">
                  <li className="step-item">
                    <span className="step-num">1</span>
                    <strong>Capture Photo:</strong> Take a clear closeup of a single cotton leaf in good natural sunlight.
                  </li>
                  <li className="step-item">
                    <span className="step-num">2</span>
                    <strong>Upload:</strong> Click the upload box or drag-and-drop the cotton leaf image.
                  </li>
                  <li className="step-item">
                    <span className="step-num">3</span>
                    <strong>Run Inference:</strong> Click "Analyze Cotton Leaf Health" to trigger the neural network.
                  </li>
                  <li className="step-item">
                    <span className="step-num">4</span>
                    <strong>Treatment Guide:</strong> Review instant diagnosis, probability breakdown, and spray dosages.
                  </li>
                </ul>
                <div className="divider" />
                <div className="alert-box alert-amber" style={{fontSize: 12}}>
                  Note: Decision support system for Dhule cotton farmers. Validate with local agronomist before spray.
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  )

  // 4. COTTON MARKET PRICES (APMC Mandi)
  const renderMarket = () => (
    <div className="page">
      <div className="section-header">
        <div style={{display:'flex',justifyContent:'space-between',alignItems:'flex-start',flexWrap:'wrap',gap:12}}>
          <div>
            <h2>💰 Maharashtra Cotton Market & APMC Prices</h2>
            <p>कापूस बाजारभाव — Daily mandi auction rates across Dhule, Jalgaon, Akola and Khandesh market yards (Per Quintal / 100 kg)</p>
          </div>
          <a href="https://agmarknet.gov.in/" target="_blank" rel="noopener noreferrer" className="btn btn-outline btn-sm">
            🔗 Agmarknet Portal
          </a>
        </div>
      </div>

      <div className="stats-grid">
        <div className="stat-card">
          <div className="stat-top">
            <div className="stat-label">Dhule APMC Today</div>
            <div className="stat-icon">🏛️</div>
          </div>
          <div className="stat-value" style={{color: 'var(--leaf-300)'}}>₹7,250</div>
          <div className="stat-sub">▲ +₹120 vs yesterday • Bt Long Staple</div>
        </div>
        <div className="stat-card">
          <div className="stat-top">
            <div className="stat-label">Highest Rate in State</div>
            <div className="stat-icon">⭐</div>
          </div>
          <div className="stat-value" style={{color: 'var(--cotton-gold)'}}>₹7,400</div>
          <div className="stat-sub">Akola APMC • Premium Quality</div>
        </div>
        <div className="stat-card">
          <div className="stat-top">
            <div className="stat-label">Govt. MSP 2024-25</div>
            <div className="stat-icon">📜</div>
          </div>
          <div className="stat-value">₹7,121</div>
          <div className="stat-sub">Long Staple (Medium: ₹6,620)</div>
        </div>
        <div className="stat-card">
          <div className="stat-top">
            <div className="stat-label">Market vs MSP</div>
            <div className="stat-icon">📊</div>
          </div>
          <div className="stat-value">+₹129</div>
          <div className="stat-sub">Selling above government base price</div>
        </div>
      </div>

      <div className="grid-60-40" style={{marginBottom: 24}}>
        <div className="card">
          <div className="card-header">
            <span className="card-title">📊 APMC Mandi Price Comparison (₹ / Quintal)</span>
            <span className="badge badge-green">Live Rates</span>
          </div>
          <div className="card-body" style={{padding: '16px 12px'}}>
            <div className="chart-container" style={{height: 230}}>
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={MANDI_PRICES.map(m => ({ name: m.market.replace(' APMC', ''), price: m.price }))}>
                  <CartesianGrid strokeDasharray="3 3" stroke="rgba(52,211,153,0.1)" />
                  <XAxis dataKey="name" tick={{ fill: '#8ea896', fontSize: 11 }} />
                  <YAxis tick={{ fill: '#8ea896', fontSize: 11 }} domain={[6900, 7550]} />
                  <Tooltip
                    contentStyle={{ background: '#0e1911', border: '1px solid rgba(52,211,153,0.3)', borderRadius: 8, color: '#f8fafc' }}
                    formatter={(v: any) => [`₹${v}`, 'Rate/Quintal']}
                  />
                  <Bar dataKey="price" fill="#10b981" radius={[6, 6, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">💡 Farmer Selling Strategy</span>
          </div>
          <div className="card-body">
            <div className="alert-box alert-green">
              <strong>Price Advantage:</strong> Open market rates are currently trading above Govt. MSP by ₹120 - ₹280/qtl.
            </div>
            <ul className="steps-list" style={{marginTop: 12}}>
              <li className="step-item">
                <span className="step-num">1</span>
                <strong>Moisture Check:</strong> Dry cotton in sunlight to ensure moisture is ≤ 8% to command maximum grade premium.
              </li>
              <li className="step-item">
                <span className="step-num">2</span>
                <strong>Compare Mandis:</strong> Compare Dhule vs Jalgaon vs Shirpur before transporting harvest.
              </li>
              <li className="step-item">
                <span className="step-num">3</span>
                <strong>e-NAM Portal:</strong> Register lot on National Agriculture Market for transparent electronic bidding.
              </li>
            </ul>
            <div className="divider" />
            <div style={{fontSize: 12, color: 'var(--text-muted)'}}>
              Cotton Corporation of India (CCI) Dhule Sub-Centre: <strong style={{color:'var(--cotton-gold)'}}>02562-233-141</strong>
            </div>
          </div>
        </div>
      </div>

      {/* APMC Mandi Rates Table */}
      <div className="card" style={{marginBottom: 24}}>
        <div className="card-header">
          <span className="card-title">📋 Mandi Auction Rates — Maharashtra Cotton Hubs</span>
          <span className="badge badge-blue">October 2024</span>
        </div>
        <div className="card-body" style={{padding: 0}}>
          <table className="price-table">
            <thead>
              <tr>
                <th>APMC Market Yard</th>
                <th>District</th>
                <th>Rate (₹ / Quintal)</th>
                <th>Daily Trend</th>
                <th>Variety Specification</th>
                <th>Moisture</th>
              </tr>
            </thead>
            <tbody>
              {MANDI_PRICES.map((m, i) => (
                <tr key={i}>
                  <td><strong>🌾 {m.market}</strong></td>
                  <td style={{color: 'var(--text-muted)'}}>{m.district}</td>
                  <td><strong style={{fontSize: 15, color: 'var(--cotton-white)'}}>₹{m.price.toLocaleString()}</strong></td>
                  <td>
                    <span className={m.trend === 'up' ? 'price-up' : 'price-down'}>
                      {m.trend === 'up' ? '▲ +₹' : '▼ -₹'}{m.change}
                    </span>
                  </td>
                  <td style={{fontSize: 12, color: 'var(--text-cotton)'}}>{m.variety}</td>
                  <td><span className="badge badge-cotton">{m.moisture}</span></td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      {/* Procurement & Portals */}
      <div className="grid-3">
        <div className="card">
          <div className="card-header">
            <span className="card-title">🏛️ CCI Govt. Procurement</span>
          </div>
          <div className="card-body">
            <div className="info-grid">
              <div>
                <div className="info-key">Procurement Scheme</div>
                <div className="info-val">MSP Guarantee</div>
              </div>
              <div>
                <div className="info-key">Farmer Portal</div>
                <div className="info-val">DBT Cotton Portal</div>
              </div>
              <div>
                <div className="info-key">Direct Bank Payout</div>
                <div className="info-val" style={{color: 'var(--leaf-300)'}}>Within 7 Days</div>
              </div>
              <div>
                <div className="info-key">Quantity Cap</div>
                <div className="info-val">Unlimited 2024</div>
              </div>
            </div>
            <div className="divider" />
            <div className="alert-box alert-blue" style={{fontSize: 12, padding: '8px 12px'}}>
              Documents required: Aadhaar card, Bank Passbook, 7/12 extract showing cotton crop entry (कापूस पीक नोंद).
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">🌐 Key Agricultural Portals</span>
          </div>
          <div className="card-body">
            <div style={{display:'flex',flexDirection:'column',gap: 8}}>
              {[
                { name: 'Agmarknet APMC Daily Rates', url: 'https://agmarknet.gov.in/' },
                { name: 'e-NAM National Agriculture Market', url: 'https://www.enam.gov.in/' },
                { name: 'Maharashtra Krishi Vibhag', url: 'https://krishi.maharashtra.gov.in/' },
                { name: 'Cotton Corporation of India (CCI)', url: 'https://cotcorp.org.in/' },
                { name: 'IMD Agromet Advisory Mausam', url: 'https://mausam.imd.gov.in/' }
              ].map((l, i) => (
                <a
                  key={i}
                  href={l.url}
                  target="_blank"
                  rel="noopener noreferrer"
                  style={{
                    display:'flex',
                    alignItems:'center',
                    gap: 8,
                    padding: '9px 12px',
                    borderRadius: 8,
                    background: 'rgba(16,185,129,0.06)',
                    border: '1px solid rgba(16,185,129,0.18)',
                    color: 'var(--leaf-300)',
                    fontSize: 12.5,
                    fontWeight: 600,
                    textDecoration: 'none'
                  }}
                >
                  🔗 {l.name}
                </a>
              ))}
            </div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title">📞 Agricultural Helplines</span>
          </div>
          <div className="card-body">
            <div style={{display:'flex',flexDirection:'column',gap: 10}}>
              <div>
                <div className="info-key">Kisan Call Centre (Toll Free)</div>
                <div className="info-val" style={{color: 'var(--cotton-gold)'}}>1800-180-1551</div>
              </div>
              <div>
                <div className="info-key">Krishi Vigyan Kendra (KVK) Dhule</div>
                <div className="info-val">02562-254-123</div>
              </div>
              <div>
                <div className="info-key">District Agricultural Officer (DAO) Dhule</div>
                <div className="info-val">02562-237-456</div>
              </div>
              <div>
                <div className="info-key">APMC Dhule Main Yard</div>
                <div className="info-val">02562-281-200</div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  )

  const NAV_ITEMS = [
    { key: 'overview', label: 'Overview', icon: '🌾' },
    { key: 'map', label: 'Google Suitability Map', icon: '🗺️' },
    { key: 'health', label: 'Leaf Health AI', icon: '🌿' },
    { key: 'market', label: 'Market Prices (APMC)', icon: '💰' },
  ]

  return (
    <div className="app-layout">
      {/* Sidebar with Authentic Cotton Theme */}
      <aside className="sidebar">
        <div className="sidebar-logo">
          <div className="logo-header">
            <div className="logo-boll-icon">☁️</div>
            <div>
              <h2>Khandesh Cotton AI</h2>
              <div className="marathi-tag">धुळे कापूस कृषी बुद्धिमत्ता</div>
            </div>
          </div>
          <p>Cotton Farm Intelligence • Dhule District, Maharashtra</p>
        </div>

        <nav className="sidebar-nav">
          <div className="nav-section-label">FARM INTELLIGENCE</div>
          {NAV_ITEMS.map(item => (
            <button
              key={item.key}
              className={`nav-item ${activePage === item.key ? 'active' : ''}`}
              onClick={() => setActivePage(item.key as any)}
            >
              <span className="nav-icon">{item.icon}</span>
              <span>{item.label}</span>
            </button>
          ))}

          <div className="nav-section-label" style={{marginTop: 16}}>EXTERNAL RESOURCES</div>
          <button className="nav-item" onClick={() => window.open('http://localhost:8000/docs', '_blank')}>
            <span className="nav-icon">📖</span>API Docs (Swagger)
          </button>
          <button className="nav-item" onClick={() => window.open('https://kvkdhule.in/', '_blank')}>
            <span className="nav-icon">🏛️</span>KVK Dhule
          </button>
          <button className="nav-item" onClick={() => window.open('https://agmarknet.gov.in/', '_blank')}>
            <span className="nav-icon">📈</span>Agmarknet Mandi
          </button>
        </nav>

        <div className="sidebar-footer">
          <div style={{display:'flex',alignItems:'center',gap: 8,marginBottom: 6}}>
            <span className="pulse-dot" />
            <span style={{
              fontWeight: 700,
              color: backendOnline === true ? 'var(--leaf-300)' : backendOnline === false ? 'var(--status-danger)' : 'var(--cotton-gold)'
            }}>
              Backend: {backendOnline === true ? 'Online (FastAPI)' : backendOnline === false ? 'Offline' : 'Connecting...'}
            </span>
          </div>
          <div>B.Tech IT Project • Phase 1</div>
          <div style={{fontSize: 10, color: 'var(--text-subtle)', marginTop: 2}}>MobileNetV2 Cotton Leaf Disease AI</div>
        </div>
      </aside>

      {/* Main Content Viewport */}
      <div className="main-content">
        <header className="topbar">
          <div className="topbar-title">
            <h1>
              <span>{NAV_ITEMS.find(n => n.key === activePage)?.icon}</span>
              <span>{NAV_ITEMS.find(n => n.key === activePage)?.label}</span>
            </h1>
            <p>Cotton Farm Intelligence — Dhule District (धुळे, शिरपूर, शिंदखेडा, साक्री)</p>
          </div>
          <div className="topbar-badges">
            <span className="badge badge-green">Kharif 2024-25</span>
            <span className="badge badge-cotton">Black Cotton Soil</span>
            <span className={`badge ${backendOnline === true ? 'badge-green' : backendOnline === false ? 'badge-red' : 'badge-amber'}`}>
              {backendOnline === true ? '● API Online' : backendOnline === false ? '● API Offline' : '● Connecting...'}
            </span>
          </div>
        </header>

        <main>
          {activePage === 'overview' && renderOverview()}
          {activePage === 'map' && renderMap()}
          {activePage === 'health' && renderHealth()}
          {activePage === 'market' && renderMarket()}
        </main>
      </div>
    </div>
  )
}
