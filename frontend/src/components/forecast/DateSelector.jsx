import { getTomorrowDate } from '../../utils/dateUtils';
import { formatDate } from '../../utils/aqiUtils';

export function DateSelector({ selectedDate, onSelectDate, className = '' }) {
  const tomorrow = getTomorrowDate();
  const dayAfter = (() => {
    const d = new Date(`${tomorrow}T12:00:00`);
    d.setDate(d.getDate() + 1);
    return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-${String(d.getDate()).padStart(2,'0')}`;
  })();

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="space-y-1">
        <label className="text-xs font-semibold text-[#69766E] block">Forecast Date</label>
        <input type="date" min={tomorrow} value={selectedDate || tomorrow}
          onChange={(e) => onSelectDate(e.target.value)}
          className="w-full px-3 py-2 text-xs sm:text-sm rounded-xl border border-[#E3E8E1] bg-white text-[#17231C] focus:outline-none focus:ring-2 focus:ring-[#173D2D]/20 focus:border-[#173D2D]" />
        <p className="text-[11px] text-[#69766E]">The model uses the eight consecutive days ending one day before the selected forecast date.</p>
      </div>
      <div className="space-y-1.5">
        <span className="text-[11px] text-[#69766E] block">Quick dates:</span>
        <div className="grid grid-cols-2 gap-1.5">
          {[{label:`Tomorrow · ${formatDate(tomorrow)}`,value:tomorrow},{label:`Day after · ${formatDate(dayAfter)}`,value:dayAfter}].map((preset) =>
            <button key={preset.value} type="button" onClick={() => onSelectDate(preset.value)}
              className={`p-2 rounded-lg text-left text-xs transition-colors border ${
                selectedDate === preset.value ? 'bg-[#173D2D] text-[#B7E46A] border-[#102C22] font-semibold' : 'bg-white text-[#17231C] border-[#E3E8E1] hover:bg-[#F7F8F4]'
              }`}><div className="truncate">{preset.label}</div></button>
          )}
        </div>
      </div>
    </div>
  );
}
