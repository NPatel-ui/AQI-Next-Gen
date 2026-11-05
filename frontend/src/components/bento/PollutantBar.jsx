export function PollutantBar({
  name,
  label,
  value,
  unit = 'µg/m³',
  cpcbStandard = 60,
  maxScale = 250,
}) {
  const numValue = value !== null && value !== undefined ? Number(value) : null;
  const percentage = numValue !== null ? Math.min(100, (numValue / maxScale) * 100) : 0;
  const isOverStandard = numValue !== null && numValue > cpcbStandard;

  return (
    <div className="space-y-1.5 p-3 rounded-xl bg-[#F7F8F4] border border-[#E3E8E1] hover:border-[#A8BFA9] transition-colors">
      <div className="flex items-center justify-between text-xs">
        <div className="flex items-center gap-1.5">
          <span className="font-bold text-[#17231C]">{label || name}</span>
          <span className="text-[10px] text-[#69766E]">({unit})</span>
        </div>
        <div className="font-mono text-xs font-semibold text-[#17231C]">
          {numValue !== null ? `${numValue.toFixed(1)}` : 'N/A'}
        </div>
      </div>

      {/* Progress Bar with National Standard Marker */}
      <div className="relative w-full h-2 rounded-full bg-[#E3E8E1] overflow-hidden">
        <div
          className={`h-full rounded-full transition-all duration-500 ${
            numValue === null
              ? 'bg-transparent'
              : isOverStandard
              ? 'bg-amber-500'
              : 'bg-emerald-500'
          }`}
          style={{ width: `${percentage}%` }}
        />
      </div>

      <div className="flex items-center justify-between text-[10px] text-[#69766E]">
        <span>Safe: ≤{cpcbStandard} {unit}</span>
        {isOverStandard && (
          <span className="text-amber-700 font-medium">Exceeds standard</span>
        )}
      </div>
    </div>
  );
}

