import { Wind, Calendar, AlertCircle, Bookmark, Check } from 'lucide-react';
import { getAqiCategory, formatAqi, formatDate } from '../../utils/aqiUtils';

export function ForecastHeroCard({
  city, prediction, loading = false, error = null, onSave = null,
  isSaved = false, isSaving = false,
}) {
  const predictedAqi = prediction?.predicted_next_day_aqi;
  const targetDate = prediction?.prediction_for_date;
  const category = getAqiCategory(predictedAqi);

  return (
    <div className="relative overflow-hidden rounded-2xl bg-[#173D2D] text-white p-5 sm:p-7 border border-[#102C22] shadow-sm">
      <div className="relative z-10 flex flex-col gap-5">
        <div className="flex flex-wrap items-center justify-between gap-3">
          <div>
            <h2 className="text-2xl font-bold font-heading text-white">{city}</h2>
            <div className="text-xs text-[#A8BFA9] flex items-center gap-1.5 mt-1">
              <Calendar className="w-3.5 h-3.5 text-[#B7E46A]" />
              <span>Forecast date: <strong className="text-white">{formatDate(targetDate)}</strong></span>
            </div>
          </div>
          <div className="flex items-center gap-2">
            {onSave && !loading && !error && Number.isFinite(Number(predictedAqi)) && (
              <button type="button" onClick={onSave} disabled={isSaved || isSaving}
                className={`inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
                  isSaved ? 'bg-emerald-950/60 border-emerald-500/40 text-emerald-300' : 'bg-white/10 hover:bg-white/20 border-white/20 text-white'
                }`}>
                {isSaved ? <><Check className="w-3.5 h-3.5" />Saved</> : <><Bookmark className="w-3.5 h-3.5 text-[#B7E46A]" />{isSaving ? 'Saving...' : 'Save Forecast'}</>}
              </button>
            )}
            {prediction && !loading && !error && <span className="px-3 py-1 rounded-lg border text-xs font-semibold"
              style={{backgroundColor:category.bgColor,borderColor:category.borderColor,color:category.textColor}}>{category.name}</span>}
          </div>
        </div>

        {loading ? (
          <div className="py-8 flex flex-col items-center justify-center gap-2">
            <div className="w-8 h-8 border-2 border-[#B7E46A] border-t-transparent rounded-full animate-spin" />
            <p className="text-xs text-[#A8BFA9]">Generating forecast with both trained models...</p>
          </div>
        ) : error ? (
          <div className="p-3.5 rounded-xl bg-rose-950/40 border border-rose-800/60 text-xs text-rose-200 flex items-start gap-2.5">
            <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
            <div><div className="font-semibold text-white">Forecast unavailable</div><div className="mt-0.5">{error}</div></div>
          </div>
        ) : prediction ? (
          <div className="grid grid-cols-1 sm:grid-cols-12 gap-5 items-center">
            <div className="sm:col-span-7 flex items-baseline gap-3">
              <span className="text-5xl sm:text-6xl font-extrabold font-heading text-white tracking-tight">{formatAqi(predictedAqi)}</span>
              <span className="text-xs font-bold text-[#A8BFA9] uppercase">India AQI</span>
            </div>
            <div className="sm:col-span-5 p-3.5 rounded-xl bg-white/5 border border-white/10 text-xs space-y-2">
              <div className="flex items-center justify-between text-[#A8BFA9]">
                <span>PM AQI forecast</span><span className="text-white font-mono font-semibold">{formatAqi(prediction.predicted_pm_aqi)}</span>
              </div>
              <div className="flex items-center justify-between text-[#A8BFA9]">
                <span>Input data through</span><span className="text-white font-mono">{formatDate(prediction.input_end_date)}</span>
              </div>
              <div className="flex items-center justify-between text-[#A8BFA9]">
                <span>Model features</span><span className="text-white font-mono"> {prediction.features_prepared}/118</span>
              </div>
              <div className="pt-1 text-[11px] text-[#A8BFA9] border-t border-white/10">{category.advisory}</div>
            </div>
          </div>
        ) : (
          <div className="py-7 text-center text-xs text-[#A8BFA9]">
            <Wind className="w-6 h-6 mx-auto mb-2 opacity-70" />
            Select a city and forecast date, then generate a prediction.
          </div>
        )}
      </div>
    </div>
  );
}
