export function CategoryGauge({ aqi = 120, className = '' }) {
  const value = Math.max(0, Math.min(500, Number(aqi) || 0));
  const percentage = (value / 500) * 100;

  const categories = [
    { label: 'Good', range: '0-50', color: '#10B981', width: '10%' },
    { label: 'Satisfactory', range: '51-100', color: '#22C55E', width: '10%' },
    { label: 'Moderate', range: '101-200', color: '#F59E0B', width: '20%' },
    { label: 'Poor', range: '201-300', color: '#F97316', width: '20%' },
    { label: 'Very Poor', range: '301-400', color: '#EF4444', width: '20%' },
    { label: 'Severe', range: '>400', color: '#881337', width: '20%' },
  ];

  return (
    <div className={`space-y-2.5 ${className}`}>
      {/* Header info */}
      <div className="flex items-center justify-between text-xs text-[#69766E]">
        <span className="font-semibold uppercase tracking-wider">CPCB Index Spectrum</span>
        <span className="font-mono font-medium">{Math.round(value)} / 500 Max</span>
      </div>

      {/* Multi-segment Spectrum Bar */}
      <div className="relative pt-3 pb-1">
        {/* Floating Pointer Indicator */}
        <div
          className="absolute top-0 -translate-x-1/2 transition-all duration-500 flex flex-col items-center z-10"
          style={{ left: `${percentage}%` }}
        >
          <div className="w-2.5 h-2.5 bg-[#17231C] rounded-full ring-2 ring-white shadow-sm" />
          <div className="w-0.5 h-2 bg-[#17231C]" />
        </div>

        {/* Segments */}
        <div className="h-3 w-full rounded-full flex overflow-hidden shadow-inner bg-[#E3E8E1]">
          {categories.map((cat) => (
            <div
              key={cat.label}
              style={{ width: cat.width, backgroundColor: cat.color }}
              title={`${cat.label} (${cat.range})`}
              className="h-full relative group transition-opacity hover:opacity-90"
            />
          ))}
        </div>
      </div>

      {/* Legend below bar */}
      <div className="grid grid-cols-3 sm:grid-cols-6 gap-1 pt-1 text-[10px] text-[#69766E] text-center">
        {categories.map((c) => (
          <div key={c.label} className="truncate px-0.5">
            <span className="inline-block w-1.5 h-1.5 rounded-full mr-1" style={{ backgroundColor: c.color }} />
            <span className="font-medium">{c.label}</span>
          </div>
        ))}
      </div>
    </div>
  );
}

