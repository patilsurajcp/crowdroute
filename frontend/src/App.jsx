import { useState } from 'react'
import SearchForm    from './components/SearchForm'
import ResultCard    from './components/ResultCard'
import WeatherBadge  from './components/WeatherBadge'
import { getPredictions, getCurrentWeather, getHolidayImpact } from './services/api'

export default function App() {
  const [loading, setLoading] = useState(false)
  const [results, setResults] = useState(null)
  const [weather, setWeather] = useState(null)
  const [holiday, setHoliday] = useState(null)
  const [error,   setError]   = useState(null)

  const handleSubmit = async (formData) => {
    setLoading(true)
    setError(null)
    setResults(null)
    setWeather(null)
    setHoliday(null)

    try {
      const [predictions, weatherData, holidayData] = await Promise.all([
        getPredictions(formData),
        getCurrentWeather(formData.city).catch(() => null),
        getHolidayImpact(formData.datetime_str).catch(() => null),
      ])
      setResults(predictions)
      setWeather(weatherData)
      setHoliday(holidayData)
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
            ${holiday.impact_label === 'VERY HIGH' ? 'bg-red-50 border-red-400'    :
              holiday.impact_label === 'HIGH'      ? 'bg-orange-50 border-orange-400' :
                                                     'bg-yellow-50 border-yellow-400'}`}>
            <div className="flex items-center justify-between">
              <p className="font-bold text-gray-800">{holiday.impact_emoji} Holiday Impact Detected</p>
              <span className={`text-xs font-bold px-2 py-1 rounded-full
                ${holiday.impact_label === 'VERY HIGH' ? 'bg-red-100 text-red-700'       :
                  holiday.impact_label === 'HIGH'      ? 'bg-orange-100 text-orange-700' :
                                                         'bg-yellow-100 text-yellow-700'}`}>
                {holiday.impact_label} ×{holiday.crowd_multiplier}
              </span>
            </div>
            <p className="text-sm text-gray-600">{holiday.impact_tip}</p>
            {holiday.reasons.length > 0 && (
              <ul className="text-xs text-gray-500 space-y-1">
                {holiday.reasons.map((r, i) => <li key={i}>• {r}</li>)}
              </ul>
            )}
            {holiday.nearby_holidays.length > 0 && (
              <div className="mt-2 pt-2 border-t border-gray-200">
                <p className="text-xs font-semibold text-gray-500 mb-1">📅 Nearby Holidays:</p>
                <div className="flex flex-wrap gap-2">
                  {holiday.nearby_holidays.map((h, i) => (
                    <span key={i} className="text-xs bg-white border border-gray-200 rounded-lg px-2 py-1">
                      {h.date} — {h.name}
                    </span>
                  ))}
                </div>
              </div>
            )}
          </div>
        )}

        {/* Route Summary */}
        {results && results.route_summary && (
          <div className="flex items-center gap-2 bg-white rounded-xl px-4 py-3 shadow text-sm">
            <span>📍</span>
            <span className="font-semibold text-gray-700">{results.source}</span>
            <span className="text-gray-400">→</span>
            <span>🏁</span>
            <span className="font-semibold text-gray-700">{results.destination}</span>
            <span className="ml-auto text-blue-500 font-semibold">{results.city}</span>
          </div>
        )}

        {/* Traffic Badge */}
        {results && results.route_summary && results.route_summary.includes('traffic') && (
          <div className={`flex items-center gap-3 rounded-xl px-4 py-3 text-sm border
        ${results.route_summary.includes('HIGH')   ? 'bg-red-50 border-red-300'    :
         results.route_summary.includes('MEDIUM') ? 'bg-yellow-50 border-yellow-300' :
                                                  'bg-green-50 border-green-300'}`}>
        <span className="text-xl">🚦</span>
        <div>
        <p className="font-semibold text-gray-700">Live Traffic Conditions</p>
        <p className="text-gray-500 text-xs">{results.route_summary}</p>
       </div>
      </div>
      )}

        {/* Results */}
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