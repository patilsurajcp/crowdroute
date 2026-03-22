import { useState, useEffect } from 'react'
import { getCityTransport } from '../services/api'

const ALL_CITIES = [
  'Agartala','Agra','Ahmedabad','Aizawl','Allahabad','Amravati','Amritsar',
  'Aurangabad','Bareilly','Bengaluru','Bhilai','Bhiwandi','Bhopal','Bhubaneswar',
  'Bikaner','Chandigarh','Chennai','Coimbatore','Cuttack','Daman','Dehradun',
  'Delhi','Dharwad','Dhanbad','Dispur','Faridabad','Firozabad','Gangtok',
  'Gorakhpur','Guntur','Guwahati','Gwalior','Howrah','Hubli','Hyderabad',
  'Imphal','Indore','Itanagar','Jabalpur','Jaipur','Jalandhar','Jamshedpur',
  'Jodhpur','Kanpur','Kavaratti','Kochi','Kohima','Kolkata','Kota','Kozhikode',
  'Lucknow','Ludhiana','Madurai','Meerut','Moradabad','Mumbai','Mysuru','Nagpur',
  'Nashik','Noida','Panaji','Patna','Port Blair','Pune','Raipur','Rajkot',
  'Ranchi','Saharanpur','Salem','Shillong','Shimla','Silvassa','Solapur',
  'Srinagar','Surat','Thiruvananthapuram','Thrissur','Tiruchirappalli',
  'Tiruppur','Vadodara','Varanasi','Vijayawada','Warangal',
].sort()

export default function SearchForm({ onSubmit, loading }) {
  const [citySearch,     setCitySearch]     = useState('')
  const [selectedCity,   setSelectedCity]   = useState('Hubli')
  const [showDropdown,   setShowDropdown]   = useState(false)
  const [transports,     setTransports]     = useState([])
  const [selectedTrans,  setSelectedTrans]  = useState([])
  const [loadingTrans,   setLoadingTrans]   = useState(false)

  // ── Load transport options when city changes ─────────────
  useEffect(() => {
    const fetchTransport = async () => {
      setLoadingTrans(true)
      try {
        const data = await getCityTransport(selectedCity)
        setTransports(data.transports)
        setSelectedTrans(data.transports.map(t => t.type)) // select all by default
      } catch {
        // fallback
        setTransports([
          { type: 'bus',   label: '🚌 Bus'   },
          { type: 'train', label: '🚆 Train' }
        ])
        setSelectedTrans(['bus', 'train'])
      } finally {
        setLoadingTrans(false)
      }
    }
    fetchTransport()
  }, [selectedCity])

  const toggleTransport = (type) => {
    setSelectedTrans(prev =>
      prev.includes(type)
        ? prev.filter(t => t !== type)
        : [...prev, type]
    )
  }

  const filtered = ALL_CITIES.filter(c =>
    c.toLowerCase().includes(citySearch.toLowerCase())
  )

  const handleSubmit = (e) => {
    e.preventDefault()
    if (selectedTrans.length === 0) {
      alert('Please select at least one transport type!')
      return
    }
    onSubmit({
      datetime_str:    e.target.datetime.value,
      city:            selectedCity,
      transport_types: selectedTrans,
      is_holiday:      e.target.is_holiday.checked,
    })
  }

  const defaultDT = () => {
    const d = new Date(Date.now() + 3600000)
    return d.toISOString().slice(0, 16)
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-6 space-y-5">

      {/* City Search */}
      <div className="relative">
        <label className="block text-sm font-semibold text-gray-600 mb-1">🏙️ City</label>
        <input
          type="text"
          placeholder={`Search city...`}
          value={citySearch}
          onChange={e => { setCitySearch(e.target.value); setShowDropdown(true) }}
          onFocus={() => setShowDropdown(true)}
          onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
          className="w-full border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        {showDropdown && filtered.length > 0 && (
          <ul className="absolute z-10 w-full bg-white border border-gray-200 rounded-xl mt-1 max-h-48 overflow-y-auto shadow-lg">
            {filtered.map(city => (
              <li
                key={city}
                onMouseDown={() => {
                  setSelectedCity(city)
                  setCitySearch('')
                  setShowDropdown(false)
                }}
                className={`px-4 py-2 cursor-pointer hover:bg-blue-50 text-sm
                  ${city === selectedCity ? 'bg-blue-50 font-semibold text-blue-600' : ''}`}
              >
                {city}
              </li>
            ))}
          </ul>
        )}
        <p className="text-xs text-gray-400 mt-1">
          Selected: <span className="font-semibold text-blue-600">{selectedCity}</span>
        </p>
      </div>

      {/* Date & Time */}
      <div>
        <label className="block text-sm font-semibold text-gray-600 mb-1">📅 Date & Time</label>
        <input
          type="datetime-local"
          name="datetime"
          defaultValue={defaultDT()}
          required
          className="w-full border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
      </div>

      {/* Transport Types — Dynamic! */}
      <div>
        <label className="block text-sm font-semibold text-gray-600 mb-2">
          🚦 Available Transport in {selectedCity}
        </label>

        {loadingTrans ? (
          <p className="text-sm text-gray-400">Loading transport options...</p>
        ) : (
          <div className="flex flex-wrap gap-3">
            {transports.map(t => (
              <button
                key={t.type}
                type="button"
                onClick={() => toggleTransport(t.type)}
                className={`px-4 py-2 rounded-xl text-sm font-semibold border-2 transition-all
                  ${selectedTrans.includes(t.type)
                    ? 'bg-blue-500 border-blue-500 text-white'
                    : 'bg-white border-gray-200 text-gray-600 hover:border-blue-300'}`}
              >
                {t.label}
              </button>
            ))}
          </div>
        )}

        {/* Hubli special note */}
        {selectedCity === 'Hubli' && (
          <p className="text-xs text-green-600 mt-2 font-medium">
            ⚡ Chigari is Hubli-Dharwad's electric bus service — eco-friendly and reliable!
          </p>
        )}
      </div>

      {/* Holiday Toggle */}
      <div className="flex items-center gap-3">
        <input type="checkbox" name="is_holiday" id="holiday" className="w-4 h-4 accent-blue-500" />
        <label htmlFor="holiday" className="text-sm font-semibold text-gray-600 cursor-pointer">
          🎉 Public Holiday?
        </label>
      </div>

      {/* Submit */}
      <button
        type="submit"
        disabled={loading || loadingTrans}
        className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white font-bold py-3 rounded-xl transition-all duration-200"
      >
        {loading ? '🔄 Predicting...' : '🔍 Predict Crowd Levels'}
      </button>
    </form>
  )
}
