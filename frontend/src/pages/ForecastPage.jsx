import { useEffect, useMemo, useState } from 'react';
import { Activity, Calendar, Layers, Wind, Sparkles, CheckCircle2, Database } from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { BentoCard } from '../components/ui/BentoCard';
import { Button } from '../components/ui/Button';
import { ForecastHeroCard } from '../components/forecast/ForecastHeroCard';
import { CitySelector } from '../components/forecast/CitySelector';
import { DateSelector } from '../components/forecast/DateSelector';
import { getCityForecast, getAvailableCities } from '../services/api';
import { saveForecast } from '../services/forecastService';
import { ELIGIBLE_CITIES } from '../utils/datasetInfo';
import { getAqiCategory, formatDate } from '../utils/aqiUtils';
import { getTomorrowDate } from '../utils/dateUtils';

export function ForecastPage() {
  const [city, setCity] = useState('Delhi');
  const [date, setDate] = useState(getTomorrowDate());
  const [cities, setCities] = useState(ELIGIBLE_CITIES.map((item) => item.name));
  const [forecast, setForecast] = useState(null);
  const [loading, setLoading] = useState(false);
  const [citiesLoading, setCitiesLoading] = useState(true);
  const [error, setError] = useState('');
  const [isSaved, setIsSaved] = useState(false);
  const [isSaving, setIsSaving] = useState(false);
  const [saveNotice, setSaveNotice] = useState('');

  useEffect(() => {
    let active = true;
    getAvailableCities().then((result) => {
      if (!active) return;
      if (result.success && result.data.length) {
        setCities(result.data);
        setCity((current) => result.data.includes(current) ? current : result.data[0]);
      } else {
        setError(result.error || 'Unable to load supported cities from the backend.');
      }
      setCitiesLoading(false);
    });
    return () => { active = false; };
  }, []);

  const fetchForecast = async (targetCity = city, targetDate = date) => {
    if (!targetCity || !targetDate) return;
    setLoading(true);
    setError('');
    setForecast(null);
    setIsSaved(false);
    setSaveNotice('');
    const result = await getCityForecast(targetCity, targetDate);
    if (result.success) setForecast(result.data);
    else setError(result.error);
    setLoading(false);
  };

  const handleGenerate = (event) => {
    event?.preventDefault();
    fetchForecast(city, date);
  };

  const handleSaveForecast = async () => {
    if (!forecast || isSaved || isSaving) return;
    setIsSaving(true);
    setSaveNotice('');
    try {
      await saveForecast({
        city,
        forecastDate: forecast.prediction_for_date,
        predictedAqi: forecast.predicted_next_day_aqi,
        aqiCategory: getAqiCategory(forecast.predicted_next_day_aqi).name,
      });
      setIsSaved(true);
      setSaveNotice('Forecast saved to your profile.');
    } catch (saveError) {
      setSaveNotice(saveError.message || 'Unable to save forecast. Check your Supabase setup.');
    } finally {
      setIsSaving(false);
    }
  };

  const cityInfo = useMemo(() => ELIGIBLE_CITIES.find((item) => item.name === city), [city]);
  const category = getAqiCategory(forecast?.predicted_next_day_aqi);

  return (
    <PageContainer>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold font-heading text-[#17231C]">Next-Day Air Quality Forecast</h1>
          <p className="text-xs text-[#69766E]">Generate India AQI and PM AQI predictions for any supported city using the latest eight days of available data.</p>
        </div>
        <Button onClick={handleGenerate} variant="primary" size="sm" isLoading={loading || citiesLoading} icon={Sparkles}>Generate Forecast</Button>
      </div>

      {saveNotice && <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2"><CheckCircle2 className="w-4 h-4 shrink-0" /><span>{saveNotice}</span></div>}

      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        <div className="lg:col-span-4 space-y-4">
          <BentoCard title="1. Select City" icon={Activity}>
            {citiesLoading ? <p className="text-xs text-[#69766E]">Loading cities from API...</p> :
              <CitySelector selectedCity={city} onSelectCity={setCity} cities={cities} />}
          </BentoCard>
          <BentoCard title="2. Select Forecast Date" icon={Calendar}>
            <DateSelector selectedDate={date} onSelectDate={setDate} />
            <Button onClick={handleGenerate} variant="lime" size="md" className="w-full mt-3" isLoading={loading} icon={Sparkles}>Generate Forecast</Button>
          </BentoCard>
        </div>

        <div className="lg:col-span-8 space-y-4">
          <ForecastHeroCard city={city} prediction={forecast} loading={loading} error={error}
            onSave={forecast ? handleSaveForecast : null} isSaved={isSaved} isSaving={isSaving} />
          <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
            <BentoCard title="India AQI Classification" icon={Layers}>
              <div className="space-y-2 pt-1">
                {forecast ? <><div className="text-2xl font-bold font-heading text-[#17231C]">{category.name}</div><p className="text-xs text-[#69766E]">{category.advisory}</p><p className="text-[11px] text-[#69766E]">{category.outdoorGuidance}</p></> :
                  <p className="text-xs text-[#69766E]">Classification will appear after a successful forecast.</p>}
              </div>
            </BentoCard>
            <BentoCard title="Forecast Input Summary" icon={Database}>
              <div className="space-y-2 pt-1 text-xs text-[#69766E]">
                <div className="flex justify-between"><span>Input period</span><strong className="text-[#17231C]">{forecast ? `${formatDate(forecast.input_start_date)} – ${formatDate(forecast.input_end_date)}` : '—'}</strong></div>
                <div className="flex justify-between"><span>Consecutive days</span><strong className="text-[#17231C]">{forecast?.input_days ?? '—'}</strong></div>
                <div className="flex justify-between"><span>Prepared features</span><strong className="text-[#17231C]">{forecast?.features_prepared ?? '—'} / 118</strong></div>
                <div className="flex justify-between gap-3"><span>Data source</span><strong className="text-right text-[#17231C] break-all">{forecast?.data_source || '—'}</strong></div>
              </div>
            </BentoCard>
          </div>
          <BentoCard title="Model Architecture" icon={Wind}>
            <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-xs">
              <div className="p-3 rounded-xl bg-[#F7F8F4] border border-[#E3E8E1]"><div className="font-semibold text-[#173D2D]">Full India AQI Model</div><div className="text-[#69766E] mt-1">HistGradientBoosting · 118 features</div>{forecast && <div className="font-mono text-[#17231C] mt-2">Prediction: {forecast.raw_full_aqi}</div>}</div>
              <div className="p-3 rounded-xl bg-[#F7F8F4] border border-[#E3E8E1]"><div className="font-semibold text-[#173D2D]">PM AQI Model</div><div className="text-[#69766E] mt-1">HistGradientBoosting · 118 features</div>{forecast && <div className="font-mono text-[#17231C] mt-2">Prediction: {forecast.raw_pm_aqi}</div>}</div>
            </div>
            <p className="text-[11px] text-[#69766E] mt-3">The backend creates the model inputs automatically from eight consecutive daily records. No placeholder predictions are displayed.</p>
          </BentoCard>
        </div>
      </div>
    </PageContainer>
  );
}
