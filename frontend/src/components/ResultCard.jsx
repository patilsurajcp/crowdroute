const LEVEL_STYLES = {
  LOW:    { bg: 'bg-green-50',  border: 'border-green-400', badge: 'bg-green-100 text-green-700',  bar: 'bg-green-400',  width: 'w-1/4'  },
  MEDIUM: { bg: 'bg-yellow-50', border: 'border-yellow-400',badge: 'bg-yellow-100 text-yellow-700',bar: 'bg-yellow-400', width: 'w-2/4'  },
  HIGH:   { bg: 'bg-red-50',    border: 'border-red-400',   badge: 'bg-red-100 text-red-700',     bar: 'bg-red-400',    width: 'w-3/4'  },
}

const TRANSPORT_ICONS = { bus: '🚌', metro: '🚇', train: '🚆' }

export default function ResultCard({ result, isBest }) {
  const style = LEVEL_STYLES[result.level]

  return (
    <div className={`relative rounded-2xl border-2 ${style.border} ${style.bg} p-5 transition-all duration-300`}>
      
      {/* Best Badge */}
      {isBest && (
        <div className="absolute -top-3 -right-3 bg-blue-500 text-white text-xs font-bold px-3 py-1 rounded-full shadow">
          ⭐ BEST OPTION
        </div>
      )}

      {/* Header */}
      <div className="flex items-center justify-between mb-3">
        <div className="flex items-center gap-2">
          <span className="text-3xl">{TRANSPORT_ICONS[result.transport]}</span>
          <span className="font-bold text-gray-800 text-lg capitalize">{result.transport}</span>
        </div>
        <span className={`text-sm font-bold px-3 py-1 rounded-full ${style.badge}`}>
          {result.emoji} {result.level}
        </span>
      </div>

      {/* Crowd Bar */}
      <div className="w-full bg-gray-200 rounded-full h-2 mb-3">
        <div className={`h-2 rounded-full ${style.bar} ${style.width} transition-all duration-500`}></div>
      </div>

      {/* Confidence */}
      <div className="flex justify-between text-sm text-gray-500">
        <span>💡 {result.advice}</span>
        <span className="font-semibold">{result.confidence}%</span>
      </div>
    </div>
  )
}