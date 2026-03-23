import { useState, useEffect, useRef, useCallback } from 'react'

export default function PlacesAutocomplete({
  name, icon, label, placeholder, city,
  onChange,         // called with (fullAddress, cityName)
  required = true
}) {
  const [query,       setQuery]       = useState('')
  const [suggestions, setSuggestions] = useState([])
  const [loading,     setLoading]     = useState(false)
  const [showList,    setShowList]    = useState(false)
  const [selected,    setSelected]    = useState(false)
  const wrapperRef  = useRef(null)
  const inputRef    = useRef(null)
  const debounceRef = useRef(null)
  const retryRef    = useRef(null)

  // ── Close on outside click ────────────────────────────────
  useEffect(() => {
    const handleClick = (e) => {
      if (wrapperRef.current && !wrapperRef.current.contains(e.target)) {
        setShowList(false)
      }
    }
    document.addEventListener('mousedown', handleClick)
    return () => document.removeEventListener('mousedown', handleClick)
  }, [])

  // ── Reset when city changes ───────────────────────────────
  useEffect(() => {
    setQuery('')
    setSuggestions([])
    setShowList(false)
    setSelected(false)
    onChange && onChange('', '')
  }, [city])

  // ── Cleanup on unmount ────────────────────────────────────
  useEffect(() => {
    return () => {
      clearTimeout(debounceRef.current)
      clearTimeout(retryRef.current)
    }
  }, [])

  // ── Fetch suggestions with retry ─────────────────────────
  const fetchSuggestions = useCallback((input, retryCount = 0) => {
    if (!window.google?.maps?.places?.AutocompleteService) {
      if (retryCount < 5) {
        console.warn(`Places API not ready, retrying (${retryCount + 1}/5)...`)
        retryRef.current = setTimeout(
          () => fetchSuggestions(input, retryCount + 1),
          600
        )
      } else {
        console.error('❌ Places API failed — disable ad blocker for localhost!')
        setLoading(false)
      }
      return
    }

    if (!input || input.length < 2) {
      setSuggestions([])
      setShowList(false)
      setLoading(false)
      return
    }

    clearTimeout(debounceRef.current)
    debounceRef.current = setTimeout(() => {
      setLoading(true)

      try {
        const service = new window.google.maps.places.AutocompleteService()
        const coords  = getCityCoords(city)

        const request = {
          input,
          componentRestrictions: { country: 'in' },
        }

        if (coords) {
          request.location = new window.google.maps.LatLng(coords.lat, coords.lng)
          request.radius   = 30000
        }

        console.log(`🔍 Searching "${input}" in ${city}...`)

        service.getPlacePredictions(request, (predictions, status) => {
          setLoading(false)
          console.log('Places status:', status, '| Results:', predictions?.length || 0)

          const OK = window.google.maps.places.PlacesServiceStatus.OK
          if (status === OK && predictions?.length > 0) {
            setSuggestions(predictions)
            setShowList(true)
          } else {
            setSuggestions([])
            setShowList(false)
          }
        })
      } catch (err) {
        console.error('Places API error:', err)
        setLoading(false)
      }
    }, 350)
  }, [city])

  // ── Handle input change ───────────────────────────────────
  const handleChange = (e) => {
    const val = e.target.value
    setQuery(val)
    setSelected(false)
    onChange && onChange(val, '')

    if (val.length >= 2) {
      setLoading(true)
      fetchSuggestions(val)
    } else {
      setSuggestions([])
      setShowList(false)
      setLoading(false)
    }
  }

  // ── Handle selection ──────────────────────────────────────
  const handleSelect = (prediction) => {
    // Full address includes city/state — critical for intercity routing
    const fullAddress = prediction.description
    const shortName   = prediction.structured_formatting?.main_text || fullAddress

    // Extract city from secondary text
    // e.g. "Bengaluru, Karnataka" → "Bengaluru"
    const secondary = prediction.structured_formatting?.secondary_text || ''
    const cityName  = secondary.split(',')[0]?.trim() || ''

    console.log(`✅ Selected: ${shortName} | Full: ${fullAddress} | City: ${cityName}`)

    setQuery(shortName)
    setSelected(true)
    setShowList(false)
    setSuggestions([])
    setLoading(false)

    // Pass full address AND detected city name
    onChange && onChange(fullAddress, cityName)
  }

  // ── Clear ─────────────────────────────────────────────────
  const handleClear = () => {
    setQuery('')
    setSuggestions([])
    setShowList(false)
    setSelected(false)
    setLoading(false)
    onChange && onChange('', '')
    inputRef.current?.focus()
  }

  // ── Highlight match ───────────────────────────────────────
  const highlight = (text, q) => {
    if (!q || !text) return text
    const idx = text.toLowerCase().indexOf(q.toLowerCase())
    if (idx === -1) return text
    return (
      <>
        {text.slice(0, idx)}
        <span className="font-bold text-blue-600">
          {text.slice(idx, idx + q.length)}
        </span>
        {text.slice(idx + q.length)}
      </>
    )
  }

  // ── Place type → emoji ────────────────────────────────────
  const getIcon = (types = []) => {
    if (types.includes('transit_station'))  return '🚉'
    if (types.includes('subway_station'))   return '🚇'
    if (types.includes('bus_station'))      return '🚌'
    if (types.includes('train_station'))    return '🚆'
    if (types.includes('airport'))          return '✈️'
    if (types.includes('hospital'))         return '🏥'
    if (types.includes('school'))           return '🏫'
    if (types.includes('university'))       return '🎓'
    if (types.includes('shopping_mall'))    return '🛍️'
    if (types.includes('restaurant'))       return '🍽️'
    if (types.includes('lodging'))          return '🏨'
    if (types.includes('park'))             return '🌳'
    if (types.includes('stadium'))          return '🏟️'
    if (types.includes('place_of_worship')) return '🛕'
    if (types.includes('neighborhood'))     return '🏘️'
    if (types.includes('route'))            return '🛣️'
    return '📍'
  }

  return (
    <div ref={wrapperRef} className="relative">

      {/* Label */}
      <label className="block text-sm font-semibold text-gray-600 mb-1">
        {icon} {label}
      </label>

      {/* Input */}
      <div className="relative">
        <input
          ref={inputRef}
          name={name}
          type="text"
          value={query}
          onChange={handleChange}
          onFocus={() => {
            if (suggestions.length > 0) setShowList(true)
          }}
          placeholder={placeholder}
          required={required}
          autoComplete="off"
          className={`w-full border-2 rounded-xl px-4 py-2.5 pr-16
            focus:outline-none transition-all duration-200
            ${selected
              ? 'border-green-400 bg-green-50'
              : showList
                ? 'border-blue-400 bg-white'
                : 'border-gray-200 bg-white hover:border-gray-300'
            }`}
        />

        {/* Right icons */}
        <div className="absolute right-3 top-1/2 -translate-y-1/2 flex items-center gap-2">
          {query.length > 0 && (
            <button
              type="button"
              onMouseDown={handleClear}
              className="text-gray-400 hover:text-gray-600 text-lg leading-none"
            >
              ×
            </button>
          )}
          {loading ? (
            <svg className="animate-spin h-4 w-4 text-blue-400 flex-shrink-0" fill="none" viewBox="0 0 24 24">
              <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"/>
              <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"/>
            </svg>
          ) : selected ? (
            <span className="text-green-500 font-bold">✓</span>
          ) : (
            <span className="text-gray-400 text-sm">🔍</span>
          )}
        </div>
      </div>

      {/* Dropdown */}
      {showList && suggestions.length > 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-2xl shadow-2xl overflow-hidden">

          <div className="px-4 py-2 bg-gray-50 border-b border-gray-100 flex items-center justify-between">
            <span className="text-xs text-gray-400 font-medium">📍 Suggestions</span>
            <span className="text-xs text-gray-300">{suggestions.length} found</span>
          </div>

          <ul className="max-h-64 overflow-y-auto">
            {suggestions.map((pred, i) => {
              const main      = pred.structured_formatting?.main_text      || pred.description
              const secondary = pred.structured_formatting?.secondary_text || ''
              return (
                <li
                  key={pred.place_id || i}
                  onMouseDown={() => handleSelect(pred)}
                  className={`flex items-start gap-3 px-4 py-3 cursor-pointer
                    hover:bg-blue-50 active:bg-blue-100 transition-colors
                    ${i < suggestions.length - 1 ? 'border-b border-gray-50' : ''}`}
                >
                  <span className="text-xl mt-0.5 flex-shrink-0">
                    {getIcon(pred.types)}
                  </span>
                  <div className="flex-1 min-w-0">
                    <p className="text-sm text-gray-800 font-medium truncate">
                      {highlight(main, query)}
                    </p>
                    {secondary && (
                      <p className="text-xs text-gray-400 truncate mt-0.5">
                        {secondary}
                      </p>
                    )}
                  </div>
                </li>
              )
            })}
          </ul>

          <div className="px-4 py-2 bg-gray-50 border-t border-gray-100 flex justify-end">
            <img
              src="https://maps.gstatic.com/mapfiles/api-3/images/powered-by-google-on-white3.png"
              alt="Powered by Google"
              className="h-4 opacity-50"
            />
          </div>
        </div>
      )}

      {/* No results */}
      {showList && !loading && query.length >= 2 && suggestions.length === 0 && (
        <div className="absolute z-50 w-full mt-1 bg-white border border-gray-200 rounded-2xl shadow-lg px-4 py-4 text-center">
          <p className="text-sm text-gray-400">😕 No places found for "{query}"</p>
          <p className="text-xs text-gray-300 mt-1">Try a different search term</p>
        </div>
      )}

    </div>
  )
}


// ── City coordinates for location bias ───────────────────────
function getCityCoords(city) {
  const coords = {
    'Mumbai':            { lat: 19.0760, lng: 72.8777 },
    'Delhi':             { lat: 28.6139, lng: 77.2090 },
    'Bengaluru':         { lat: 12.9716, lng: 77.5946 },
    'Chennai':           { lat: 13.0827, lng: 80.2707 },
    'Kolkata':           { lat: 22.5726, lng: 88.3639 },
    'Hyderabad':         { lat: 17.3850, lng: 78.4867 },
    'Pune':              { lat: 18.5204, lng: 73.8567 },
    'Ahmedabad':         { lat: 23.0225, lng: 72.5714 },
    'Jaipur':            { lat: 26.9124, lng: 75.7873 },
    'Lucknow':           { lat: 26.8467, lng: 80.9462 },
    'Hubli':             { lat: 15.3647, lng: 75.1240 },
    'Dharwad':           { lat: 15.4589, lng: 75.0078 },
    'Srinagar':          { lat: 34.0837, lng: 74.7973 },
    'Shimla':            { lat: 31.1048, lng: 77.1734 },
    'Kochi':             { lat: 9.9312,  lng: 76.2673 },
    'Guwahati':          { lat: 26.1445, lng: 91.7362 },
    'Bhubaneswar':       { lat: 20.2961, lng: 85.8245 },
    'Chandigarh':        { lat: 30.7333, lng: 76.7794 },
    'Nagpur':            { lat: 21.1458, lng: 79.0882 },
    'Indore':            { lat: 22.7196, lng: 75.8577 },
    'Bhopal':            { lat: 23.2599, lng: 77.4126 },
    'Patna':             { lat: 25.5941, lng: 85.1376 },
    'Varanasi':          { lat: 25.3176, lng: 82.9739 },
    'Amritsar':          { lat: 31.6340, lng: 74.8723 },
    'Agra':              { lat: 27.1767, lng: 78.0081 },
    'Coimbatore':        { lat: 11.0168, lng: 76.9558 },
    'Madurai':           { lat: 9.9252,  lng: 78.1198 },
    'Mysuru':            { lat: 12.2958, lng: 76.6394 },
    'Surat':             { lat: 21.1702, lng: 72.8311 },
    'Noida':             { lat: 28.5355, lng: 77.3910 },
    'Gangtok':           { lat: 27.3389, lng: 88.6065 },
    'Shillong':          { lat: 25.5788, lng: 91.8933 },
    'Port Blair':        { lat: 11.6234, lng: 92.7265 },
    'Panaji':            { lat: 15.4909, lng: 73.8278 },
    'Dehradun':          { lat: 30.3165, lng: 78.0322 },
    'Ranchi':            { lat: 23.3441, lng: 85.3096 },
    'Vijayawada':        { lat: 16.5062, lng: 80.6480 },
    'Thiruvananthapuram':{ lat: 8.5241,  lng: 76.9366 },
    'Jodhpur':           { lat: 26.2389, lng: 73.0243 },
    'Raipur':            { lat: 21.2514, lng: 81.6296 },
    'Nashik':            { lat: 19.9975, lng: 73.7898 },
    'Aurangabad':        { lat: 19.8762, lng: 75.3433 },
    'Rajkot':            { lat: 22.3039, lng: 70.8022 },
    'Vadodara':          { lat: 22.3072, lng: 73.1812 },
    'Ludhiana':          { lat: 30.9010, lng: 75.8573 },
    'Jalandhar':         { lat: 31.3260, lng: 75.5762 },
    'Meerut':            { lat: 28.9845, lng: 77.7064 },
    'Faridabad':         { lat: 28.4089, lng: 77.3178 },
    'Allahabad':         { lat: 25.4358, lng: 81.8463 },
    'Kanpur':            { lat: 26.4499, lng: 80.3319 },
    'Gwalior':           { lat: 26.2183, lng: 78.1828 },
    'Warangal':          { lat: 17.9689, lng: 79.5941 },
    'Kozhikode':         { lat: 11.2588, lng: 75.7804 },
    'Thrissur':          { lat: 10.5276, lng: 76.2144 },
    'Salem':             { lat: 11.6643, lng: 78.1460 },
    'Howrah':            { lat: 22.5958, lng: 88.2636 },
    'Jabalpur':          { lat: 23.1815, lng: 79.9864 },
    'Gorakhpur':         { lat: 26.7606, lng: 83.3732 },
    'Bikaner':           { lat: 28.0229, lng: 73.3119 },
    'Bareilly':          { lat: 28.3670, lng: 79.4304 },
  }
  return coords[city] || { lat: 20.5937, lng: 78.9629 }
}