export default function WeatherBadge({ weather }) {
  if (!weather) return null
  return (
    <div className="flex items-center gap-3 bg-blue-50 border border-blue-200 rounded-xl px-4 py-2.5 text-sm">
      <span className="text-2xl">{weather.weather_emoji}</span>
      <div>
        <p className="font-semibold text-blue-800">{weather.description}</p>
        <p className="text-blue-600">{weather.temperature}°C · Humidity {weather.humidity}%</p>
      </div>
    </div>
  )
}