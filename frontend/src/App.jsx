import { useState } from 'react'
import SearchForm    from './components/SearchForm'
import ResultCard    from './components/ResultCard'
import WeatherBadge  from './components/WeatherBadge'
import CrowdMeter    from './components/CrowdMeter'
import { getPredictions, getCurrentWeather } from './services/api'
import axios from 'axios'

const BASE_URL = 'http://127.0.0.1:8000/api/v1'

export default function App() {
  const [loading,      setLoading]      = useState(false)
  const [results,      setResults]      = useState(null)
  const [weather,      setWeather]      = useState(null)
  const [holiday,      setHoliday]      = useState(null)
  const [availability, setAvailability] = useState(null)
  const [error,        setError]        = useState(null)

  const handleSubmit = async (formData) => {
    setLoading(true)
    setError(null)
    setResults(null)
    setWeather(null)
    setHoliday(null)
    setAvailability(null)

    try {
      const [predictions, weatherData, holidayData, availData] = await Promise.all([
        getPredictions(formData),
        getCurrentWeather(formData.city).catch(() => null),
        axios.get(`${BASE_URL}/holiday/impact`, {
          params: { datetime_str: formData.datetime_str }
        }).then(r => r.data).catch(() => null),
        axios.get(`${BASE_URL}/availability`, {
          params: {
            city:         formData.city,
            datetime_str: formData.datetime_str
          }
        }).then(r => r.data).catch(() => null)
      ])

      setResults(predictions)
      setWeather(weatherData)
      setHoliday(holidayData)
      setAvailability(availData)

    } catch (err) {
      setError(err.response?.data?.detail || 'Something went wrong. Is the backend running?')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100 px-4 py-10">
      <div className="max-w-xl mx-auto space-y-6">

        {/* Header */}
        <div className="text-center space-y-1">
          <h1 className="text-4xl font-black text-blue-700">🚌 CrowdRoute</h1>
          <p className="text-gray-500 text-sm">Find the least crowded way to travel</p>
        </div>

        <SearchForm onSubmit={handleSubmit} loading={loading} />

        {error && (
          <div className="bg-red-50 border border-red-300 text-red-700 rounded-xl px-4 py-3 text-sm">
            ❌ {error}
          </div>
        )}

        {weather && <WeatherBadge weather={weather} />}

        {/* Holiday Alert */}
        {holiday && holiday.impact_label !== 'NORMAL' && (
          <div className={`rounded-2xl px-5 py-4 border-2 space-y-2
            ${holiday.impact_label === 'VERY HIGH' ? 'bg-red-50 border-red-400' :
              holiday.impact_label === 'HIGH'      ? 'bg-orange-50 border-orange-400' :
                                                     'bg-yellow-50 border-yellow-400'}`}>
            <div className="flex items-center justify-between">
              <p className="font-bold text-gray-800">{holiday.impact_emoji} Holiday Impact</p>
              <span className="text-xs font-bold px-2 py-1 rounded-full bg-orange-100 text-orange-700">
                {holiday.impact_label} ×{holiday.crowd_multiplier}
              </span>
            </div>
            <p className="text-sm text-gray-600">{holiday.impact_tip}</p>
            {holiday.reasons.map((r, i) => (
              <p key={i} className="text-xs text-gray-500">• {r}</p>
            ))}
          </div>
        )}

        {/* Live Seat Availability */}
        {availability && (
          <div className="space-y-3">
            <h2 className="font-bold text-gray-700 text-sm uppercase tracking-wide">
              📊 Live Crowd Occupancy
            </h2>
            {['bus', 'train', 'metro'].map(transport => (
              <CrowdMeter
                key={transport}
                transport={transport}
                availability={availability[transport]}
              />
            ))}
          </div>
        )}

        {/* ML Predictions */}
        {results && (
          <div className="space-y-4">
            <div className="bg-blue-600 text-white rounded-2xl px-5 py-4 text-center shadow-lg">
              <p className="text-sm opacity-80">Recommendation for {results.city}</p>
              <p className="font-bold text-lg mt-1">🏆 {results.summary}</p>
            </div>
            <div className="space-y-3">
              {results.results.map((result, i) => (
                <ResultCard key={result.transport} result={result} isBest={i === 0} />
              ))}
            </div>
          </div>
        )}

      </div>
    </div>
  )
}
