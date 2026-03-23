import { useState, useEffect } from 'react'
import { getCityTransport } from '../services/api'
import PlacesAutocomplete from './PlacesAutocomplete'

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

const TRANSPORT_CORRIDORS = {
  chigari:    { cities: ['Hubli','Dharwad'],    description: 'Hubli-Dharwad twin city only' },
  tram:       { cities: ['Kolkata'],            description: 'Kolkata tram routes only' },
  ferry:      { cities: ['Mumbai','Kochi','Guwahati','Port Blair','Panaji','Kavaratti'], description: 'Water routes only' },
  toy_train:  { cities: ['Shimla'],             description: 'Kalka-Shimla route only' },
  shikara:    { cities: ['Srinagar'],           description: 'Dal Lake & Nagin Lake only' },
  shared_cab: { cities: ['Gangtok','Shillong'], description: 'Hill route corridors only' },
}

// All Indian city names for intercity detection
const INDIAN_CITIES_LOWER = [
  'mumbai', 'delhi', 'bengaluru', 'bangalore', 'chennai', 'kolkata',
  'hyderabad', 'pune', 'ahmedabad', 'jaipur', 'lucknow', 'hubli',
  'dharwad', 'hubballi', 'surat', 'indore', 'bhopal', 'patna', 'nagpur',
  'kochi', 'chandigarh', 'mysuru', 'mysore', 'coimbatore', 'madurai',
  'visakhapatnam', 'agra', 'varanasi', 'amritsar', 'ranchi', 'bhubaneswar',
  'guwahati', 'shimla', 'srinagar', 'dehradun', 'jodhpur', 'rajkot',
  'vadodara', 'ludhiana', 'jalandhar', 'meerut', 'faridabad', 'noida',
  'gurgaon', 'gurugram', 'vijayawada', 'thiruvananthapuram', 'thrissur',
  'salem', 'tiruchirappalli', 'tiruppur', 'kozhikode', 'allahabad',
  'kanpur', 'gwalior', 'jabalpur', 'raipur', 'nashik', 'aurangabad',
  'solapur', 'kolhapur', 'amravati', 'akola', 'nanded', 'latur',
  'gorakhpur', 'bareilly', 'moradabad', 'saharanpur', 'bikaner',
  'kota', 'ajmer', 'udaipur', 'sikar', 'bhilai', 'durg', 'raigarh',
  'bilaspur', 'korba', 'howrah', 'durgapur', 'asansol', 'siliguri',
  'warangal', 'karimnagar', 'nizamabad', 'khammam', 'rajahmundry',
  'kakinada', 'nellore', 'tirupati', 'guntur', 'kurnool', 'anantapur',
  'mangaluru', 'mangalore', 'belgaum', 'belagavi', 'gulbarga', 'kalaburagi',
  'davanagere', 'shimoga', 'tumkur', 'bidar',
]


export default function SearchForm({ onSubmit, loading }) {
  const [citySearch,    setCitySearch]    = useState('')
  const [selectedCity,  setSelectedCity]  = useState('Hubli')
  const [showDropdown,  setShowDropdown]  = useState(false)
  const [transports,    setTransports]    = useState([])
  const [selectedTrans, setSelectedTrans] = useState([])
  const [loadingTrans,  setLoadingTrans]  = useState(false)
  const [mapsLoaded,    setMapsLoaded]    = useState(false)

  // Source / destination state
  const [source,        setSource]        = useState('')
  const [destination,   setDestination]   = useState('')
  const [sourceCity,    setSourceCity]    = useState('')
  const [destCity,      setDestCity]      = useState('')
  const [isIntercity,   setIsIntercity]   = useState(false)

  // ── Load Google Maps Script ONCE ─────────────────────────
  useEffect(() => {
    if (window.google?.maps?.places) {
      setMapsLoaded(true)
      return
    }
    const existingScript = document.querySelector(
      'script[src*="maps.googleapis.com"]'
    )
    if (existingScript) {
      existingScript.addEventListener('load', () => setMapsLoaded(true))
      if (window.google?.maps?.places) setMapsLoaded(true)
      return
    }
    const key = import.meta.env.VITE_GOOGLE_MAPS_API_KEY
    if (!key) {
      console.error('❌ VITE_GOOGLE_MAPS_API_KEY not set in frontend/.env')
      return
    }
    const script    = document.createElement('script')
    script.src      = `https://maps.googleapis.com/maps/api/js?key=${key}&libraries=places&loading=async`
    script.async    = true
    script.defer    = true
    script.onload   = () => {
      console.log('✅ Google Maps loaded!')
      setMapsLoaded(true)
    }
    script.onerror  = () => {
      console.error('❌ Google Maps failed — check API key or ad blocker')
    }
    document.head.appendChild(script)
  }, [])

  // ── Load Transport Options when city changes ─────────────
  useEffect(() => {
    const fetch = async () => {
      setLoadingTrans(true)
      setSource('')
      setDestination('')
      setSourceCity('')
      setDestCity('')
      setIsIntercity(false)
      try {
        const data = await getCityTransport(selectedCity)
        setTransports(data.transports)
        setSelectedTrans(data.transports.map(t => t.type))
      } catch {
        setTransports([
          { type: 'bus',   label: '🚌 Bus'   },
          { type: 'train', label: '🚆 Train' }
        ])
        setSelectedTrans(['bus', 'train'])
      } finally {
        setLoadingTrans(false)
      }
    }
    fetch()
  }, [selectedCity])

  // ── Intercity detection helper ────────────────────────────
  const detectIntercity = (detectedCity, refCity) => {
    if (!detectedCity || !refCity) return false
    const detected = detectedCity.toLowerCase().trim()
    const ref      = refCity.toLowerCase().trim()
    const selected = selectedCity.toLowerCase().trim()

    // If detected city doesn't match selected city — intercity!
    if (detected && ref && detected !== ref) return true
    if (detected && detected !== selected && INDIAN_CITIES_LOWER.includes(detected)) {
      // Check it's actually a different city
      return !selected.includes(detected) && !detected.includes(selected)
    }
    return false
  }

  const getCorridorInfo  = (type) => TRANSPORT_CORRIDORS[type] || null
  const isTransportValid = (type) => {
    const corridor = TRANSPORT_CORRIDORS[type]
    if (!corridor) return true
    return corridor.cities.includes(selectedCity)
  }

  const toggleTransport = (type) => {
    if (!isTransportValid(type)) {
      const info = getCorridorInfo(type)
      alert(`⚠️ ${type.toUpperCase()} not available in ${selectedCity}.\n${info?.description}`)
      return
    }
    setSelectedTrans(prev =>
      prev.includes(type) ? prev.filter(t => t !== type) : [...prev, type]
    )
  }

  const filtered = ALL_CITIES.filter(c =>
    c.toLowerCase().includes(citySearch.toLowerCase())
  )

  const defaultDT = () => {
    const d = new Date(Date.now() + 3600000)
    return d.toISOString().slice(0, 16)
  }

  const handleSubmit = (e) => {
    e.preventDefault()

    if (!source)      { alert('Please select a source from the suggestions!');      return }
    if (!destination) { alert('Please select a destination from the suggestions!'); return }

    let finalTransports = selectedTrans.filter(type => isTransportValid(type))

    // Intercity → only bus and train make sense
    if (isIntercity) {
      finalTransports = finalTransports.filter(t => ['bus', 'train'].includes(t))
      if (finalTransports.length === 0) finalTransports = ['bus', 'train']
    }

    if (finalTransports.length === 0) {
      alert('Please select at least one transport type!')
      return
    }

    onSubmit({
      datetime_str:    e.target.datetime.value,
      city:            selectedCity,
      source,
      destination,
      transport_types: finalTransports,
      is_holiday:      e.target.is_holiday.checked,
      is_intercity:    isIntercity,
    })
  }

  return (
    <form onSubmit={handleSubmit} className="bg-white rounded-2xl shadow-lg p-6 space-y-5">

      {/* City */}
      <div className="relative">
        <label className="block text-sm font-semibold text-gray-600 mb-1">🏙️ Departure City</label>
        <input
          type="text"
          placeholder="Search city..."
          value={citySearch}
          onChange={e => { setCitySearch(e.target.value); setShowDropdown(true) }}
          onFocus={() => setShowDropdown(true)}
          onBlur={() => setTimeout(() => setShowDropdown(false), 200)}
          className="w-full border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-400"
        />
        {showDropdown && filtered.length > 0 && (
          <ul className="absolute z-20 w-full bg-white border border-gray-200 rounded-xl mt-1 max-h-48 overflow-y-auto shadow-lg">
            {filtered.map(city => (
              <li
                key={city}
                onMouseDown={() => { setSelectedCity(city); setCitySearch(''); setShowDropdown(false) }}
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

      {/* Source */}
      {mapsLoaded ? (
        <PlacesAutocomplete
          name="source"
          icon="📍"
          label="From (Source)"
          placeholder={`Search source location...`}
          city={selectedCity}
          onChange={(fullAddress, cityName) => {
            setSource(fullAddress)
            setSourceCity(cityName)
            // Recheck intercity with new source
            const intercity = detectIntercity(destCity, cityName)
            setIsIntercity(intercity)
            if (intercity) console.log(`🚌 Intercity detected: ${cityName} → ${destCity}`)
          }}
        />
      ) : (
        <div>
          <label className="block text-sm font-semibold text-gray-600 mb-1">📍 From (Source)</label>
          <input
            type="text"
            placeholder={`e.g. Railway Station, ${selectedCity}`}
            onChange={e => setSource(e.target.value)}
            className="w-full border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
          <p className="text-xs text-yellow-600 mt-1">⏳ Loading Google Maps suggestions...</p>
        </div>
      )}

      {/* Destination */}
      {mapsLoaded ? (
        <PlacesAutocomplete
          name="destination"
          icon="🏁"
          label="To (Destination)"
          placeholder={`Search destination location...`}
          city={selectedCity}
          onChange={(fullAddress, cityName) => {
            setDestination(fullAddress)
            setDestCity(cityName)
            // Detect intercity
            const intercity = detectIntercity(cityName, sourceCity)
            setIsIntercity(intercity)
            if (intercity) console.log(`🚌 Intercity detected: ${sourceCity} → ${cityName}`)
          }}
        />
      ) : (
        <div>
          <label className="block text-sm font-semibold text-gray-600 mb-1">🏁 To (Destination)</label>
          <input
            type="text"
            placeholder="e.g. Bus Stand, Airport"
            onChange={e => setDestination(e.target.value)}
            className="w-full border border-gray-200 rounded-xl px-4 py-2.5 focus:outline-none focus:ring-2 focus:ring-blue-400"
          />
        </div>
      )}

      {/* Intercity Warning */}
      {isIntercity && (
        <div className="bg-orange-50 border-2 border-orange-300 rounded-xl px-4 py-3 space-y-1">
          <p className="font-bold text-orange-700 text-sm">
            🚌 Intercity Trip Detected!
          </p>
          <p className="text-orange-600 text-xs">
            Your route spans multiple cities.
            Only <strong>Bus</strong> and <strong>Train</strong> are available for intercity travel.
            Local transports (Metro, Chigari, Ferry etc.) have been auto-removed.
          </p>
        </div>
      )}

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

      {/* Transport Types */}
      <div>
        <label className="block text-sm font-semibold text-gray-600 mb-2">
          🚦 {isIntercity ? 'Intercity Transport Options' : `Available Transport in ${selectedCity}`}
        </label>
        {loadingTrans ? (
          <p className="text-sm text-gray-400">Loading transport options...</p>
        ) : (
          <div className="flex flex-wrap gap-3">
            {(isIntercity
              ? transports.filter(t => ['bus','train'].includes(t.type))
              : transports
            ).map(t => {
              const valid        = isTransportValid(t.type)
              const corridorInfo = getCorridorInfo(t.type)
              return (
                <div key={t.type} className="flex flex-col items-center gap-1">
                  <button
                    type="button"
                    onClick={() => toggleTransport(t.type)}
                    title={!valid && corridorInfo ? corridorInfo.description : ''}
                    className={`px-4 py-2 rounded-xl text-sm font-semibold border-2 transition-all
                      ${!valid
                        ? 'opacity-40 cursor-not-allowed bg-gray-100 border-gray-300 text-gray-400'
                        : selectedTrans.includes(t.type)
                          ? 'bg-blue-500 border-blue-500 text-white shadow-md'
                          : 'bg-white border-gray-200 text-gray-600 hover:border-blue-300'}`}
                  >
                    {t.label}
                  </button>
                  {!valid && (
                    <span className="text-xs text-red-400 text-center" style={{maxWidth:'90px'}}>
                      Not in {selectedCity}
                    </span>
                  )}
                </div>
              )
            })}
          </div>
        )}

        {/* Corridor info cards — only for non-intercity */}
        {!isIntercity && transports
          .filter(t => getCorridorInfo(t.type) && isTransportValid(t.type))
          .map(t => (
            <div key={t.type} className="mt-2 bg-blue-50 border border-blue-100 rounded-xl px-3 py-2">
              <p className="text-xs font-semibold text-blue-700">{t.label} — Service Area</p>
              <p className="text-xs text-blue-500 mt-0.5">{getCorridorInfo(t.type).description}</p>
            </div>
          ))
        }
      </div>

      {/* Holiday */}
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
        className="w-full bg-blue-500 hover:bg-blue-600 disabled:bg-blue-300 text-white font-bold py-3 rounded-xl transition-all duration-200 shadow-md"
      >
        {loading ? '🔄 Predicting...' : '🔍 Predict Crowd Levels'}
      </button>

    </form>
  )
}