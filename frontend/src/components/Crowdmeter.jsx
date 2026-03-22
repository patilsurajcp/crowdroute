export default function CrowdMeter({ transport, availability }) {
  if (!availability) return null

  const { crowd_percent, status, source, note } = availability

  // Metro not available in this city
  if (availability.available === false) return null

  const color =
    crowd_percent >= 85 ? 'bg-red-500'    :
    crowd_percent >= 60 ? 'bg-yellow-400' :
    crowd_percent >= 30 ? 'bg-green-500'  : 'bg-green-400'

  const icons = { bus: '🚌', metro: '🚇', train: '🚆' }

  return (
    <div className="bg-white rounded-xl border border-gray-200 p-4 space-y-2">

      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <span className="text-xl">{icons[transport]}</span>
          <span className="font-semibold text-gray-700 capitalize">{transport}</span>
          {transport === 'metro' && availability.metro_info && (
            <span className="text-xs bg-blue-100 text-blue-700 px-2 py-0.5 rounded-full font-medium">
              {availability.metro_info.operator}
            </span>
          )}
        </div>
        <span className="font-bold text-gray-800 text-lg">{crowd_percent}%</span>
      </div>

      {/* Progress Bar */}
      <div className="w-full bg-gray-100 rounded-full h-3">
        <div
          className={`h-3 rounded-full transition-all duration-700 ${color}`}
          style={{ width: `${crowd_percent}%` }}
        />
      </div>

      {/* Status */}
      <div className="flex items-center justify-between text-xs text-gray-500">
        <span>{status?.emoji} {status?.label}</span>
        {source === 'smart_estimation' && (
          <span className="italic">📊 Estimated</span>
        )}
        {source === 'irctc_api' && (
          <span className="text-green-600 font-medium">✅ Live Data</span>
        )}
      </div>

      {/* Metro Lines */}
      {transport === 'metro' && availability.lines?.length > 0 && (
        <div className="pt-1 border-t border-gray-100">
          <p className="text-xs text-gray-500">
            🚇 {availability.lines.length} lines · {availability.total_stations} stations
          </p>
        </div>
      )}

      {note && (
        <p className="text-xs text-gray-400 italic">{note}</p>
      )}
    </div>
  )
}