import { useEffect, useState } from 'react';
import { GitCompare, Sparkles } from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { BentoCard } from '../components/ui/BentoCard';
import { AqiBadge } from '../components/ui/Badge';
import { getAvailableCities, getCityForecast } from '../services/api';
import { ELIGIBLE_CITIES } from '../utils/datasetInfo';
import { getAqiCategory, formatDate } from '../utils/aqiUtils';
import { getTomorrowDate } from '../utils/dateUtils';

function CityForecastCard({ city, result, loading, error, tone }) {
  const value = result?.predicted_next_day_aqi;
  const category = getAqiCategory(value);
  return <div className={`p-5 rounded-2xl bg-white border ${tone === 'green' ? 'border-[#10B981]' : 'border-[#173D2D]'} space-y-4`}>
    <div className="flex items-start justify-between gap-2"><div><h2 className="text-xl font-bold font-heading text-[#17231C]">{city}</h2><div className="text-xs text-[#69766E]">{ELIGIBLE_CITIES.find((c) => c.name === city)?.state || 'India'}</div></div>{result && <AqiBadge aqi={value} />}</div>
    {loading ? <p className="py-8 text-center text-xs text-[#69766E]">Generating forecast...</p> :
      error ? <p className="text-xs text-rose-700 bg-rose-50 border border-rose-200 rounded-lg p-3">{error}</p> :
      result ? <div className="space-y-3"><div className="grid grid-cols-2 gap-2.5">
        <div className="p-3 rounded-xl bg-[#F7F8F4] border border-[#E3E8E1]"><span className="text-[11px] text-[#69766E] block">India AQI</span><span className="text-2xl font-bold font-heading text-[#17231C]">{value.toFixed(2)}</span><span className="block text-[11px] text-[#69766E]">{category.name}</span></div>
        <div className="p-3 rounded-xl bg-[#F7F8F4] border border-[#E3E8E1]"><span className="text-[11px] text-[#69766E] block">PM AQI</span><span className="text-2xl font-bold font-heading text-[#17231C]">{result.predicted_pm_aqi.toFixed(2)}</span><span className="block text-[11px] text-[#69766E]">{getAqiCategory(result.predicted_pm_aqi).name}</span></div>
      </div><div className="text-xs text-[#69766E]">Input: {formatDate(result.input_start_date)} – {formatDate(result.input_end_date)} · {result.features_prepared} features</div></div> :
      <p className="py-8 text-center text-xs text-[#69766E]">Generate a forecast to compare this city.</p>}
  </div>;
}

export function ComparisonPage() {
  const [cities, setCities] = useState(ELIGIBLE_CITIES.map((city) => city.name));
  const [cityA, setCityA] = useState('Delhi');
  const [cityB, setCityB] = useState('Mumbai');
  const [date, setDate] = useState(getTomorrowDate());
  const [results, setResults] = useState({ a: null, b: null });
  const [errors, setErrors] = useState({ a: '', b: '' });
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    getAvailableCities().then((response) => {
      if (response.success && response.data.length) {
        setCities(response.data);
        if (!response.data.includes(cityA)) setCityA(response.data[0]);
        if (!response.data.includes(cityB)) setCityB(response.data[1] || response.data[0]);
      }
    });
  }, []);

  const generate = async () => {
    if (cityA === cityB) {
      setErrors({ a: 'Choose two different cities.', b: 'Choose two different cities.' });
      return;
    }
    setLoading(true);
    setErrors({ a: '', b: '' });
    setResults({ a: null, b: null });
    const [a, b] = await Promise.all([getCityForecast(cityA, date), getCityForecast(cityB, date)]);
    setResults({ a: a.success ? a.data : null, b: b.success ? b.data : null });
    setErrors({ a: a.error || '', b: b.error || '' });
    setLoading(false);
  };

  const diff = results.a && results.b ? results.a.predicted_next_day_aqi - results.b.predicted_next_day_aqi : null;

  return <PageContainer>
    <div><h1 className="text-xl font-bold font-heading text-[#17231C]">City Air Quality Comparison</h1><p className="text-xs text-[#69766E] mt-0.5">Compare real next-day predictions from the two AQI Next-Gen models for any two supported cities.</p></div>
    <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 p-3.5 rounded-xl bg-white border border-[#E3E8E1]">
      {[{label:'City A',value:cityA,set:setCityA,other:cityB},{label:'City B',value:cityB,set:setCityB,other:cityA}].map((item) => <div key={item.label} className="space-y-1"><label className="block text-xs font-semibold text-[#173D2D]">{item.label}</label><select value={item.value} onChange={(e)=>item.set(e.target.value)} className="w-full px-3 py-2 text-xs rounded-lg border border-[#E3E8E1] bg-[#F7F8F4] text-[#17231C]">{cities.map((city)=><option key={city} value={city} disabled={city===item.other}>{city}</option>)}</select></div>)}
      <div className="space-y-1"><label className="block text-xs font-semibold text-[#173D2D]">Forecast Date</label><input type="date" min={getTomorrowDate()} value={date} onChange={(e)=>setDate(e.target.value)} className="w-full px-3 py-2 text-xs rounded-lg border border-[#E3E8E1] bg-[#F7F8F4] text-[#17231C]" /></div>
      <button onClick={generate} disabled={loading} className="sm:col-span-2 lg:col-span-3 inline-flex items-center justify-center gap-2 px-4 py-2.5 rounded-lg bg-[#173D2D] text-white text-xs font-semibold hover:bg-[#102C22] disabled:opacity-60"><Sparkles className="w-4 h-4" />{loading?'Generating both forecasts...':'Generate Comparison'}</button>
    </div>
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
      <CityForecastCard city={cityA} result={results.a} loading={loading} error={errors.a} />
      <CityForecastCard city={cityB} result={results.b} loading={loading} error={errors.b} tone="green" />
    </div>
    {diff !== null && <div className="p-4 rounded-xl bg-[#102C22] text-white flex flex-col sm:flex-row items-center justify-between gap-3 text-xs"><div className="flex items-center gap-2"><GitCompare className="w-4 h-4 text-[#B7E46A]" /><span>{diff > 0 ? cityA : cityB} is forecast to have {Math.abs(diff).toFixed(1)} AQI points higher than {diff > 0 ? cityB : cityA}.</span></div><div className="text-[#A8BFA9]">Forecast date: {formatDate(date)}</div></div>}
    <BentoCard title="How to interpret this comparison" icon={GitCompare}><p className="text-xs text-[#69766E] leading-relaxed">Both city forecasts use the same selected target date and the same two trained HistGradientBoosting models. A forecast may be unavailable for a city if its input history contains fewer than eight consecutive daily records.</p></BentoCard>
  </PageContainer>;
}
