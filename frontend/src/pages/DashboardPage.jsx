import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Wind, GitCompare, HeartPulse, ArrowRight, MapPin, Activity, Database, RefreshCw } from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { BentoCard } from '../components/ui/BentoCard';
import { ForecastHeroCard } from '../components/forecast/ForecastHeroCard';
import { CitySelector } from '../components/forecast/CitySelector';
import { CategoryGauge } from '../components/bento/CategoryGauge';
import { getCityForecast, getAvailableCities, checkBackendHealth } from '../services/api';
import { ELIGIBLE_CITIES } from '../utils/datasetInfo';
import { getAqiCategory, formatDate } from '../utils/aqiUtils';
import { getTomorrowDate } from '../utils/dateUtils';

export function DashboardPage() {
  const [cities, setCities] = useState(ELIGIBLE_CITIES.map((city) => city.name));
  const [selectedCity, setSelectedCity] = useState('Delhi');
  const [selectedDate] = useState(getTomorrowDate());
  const [forecastData, setForecastData] = useState(null);
  const [health, setHealth] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const loadForecast = async (city) => {
    setLoading(true);
    setError('');
    setForecastData(null);
    const result = await getCityForecast(city, selectedDate);
    if (result.success) setForecastData(result.data);
    else setError(result.error);
    setLoading(false);
  };

  useEffect(() => {
    let active = true;
    Promise.all([getAvailableCities(), checkBackendHealth()]).then(([cityResult, healthResult]) => {
      if (!active) return;
      if (cityResult.success && cityResult.data.length) {
        setCities(cityResult.data);
        const initialCity = cityResult.data.includes('Delhi') ? 'Delhi' : cityResult.data[0];
        setSelectedCity(initialCity);
        loadForecast(initialCity);
      } else {
        setError(cityResult.error || 'Unable to load supported cities.');
        setLoading(false);
      }
      setHealth(healthResult.connected ? healthResult.data : null);
      if (!healthResult.connected) setError(healthResult.error);
    });
    return () => { active = false; };
  }, []);

  const category = getAqiCategory(forecastData?.predicted_next_day_aqi);
  const cityMeta = ELIGIBLE_CITIES.find((city) => city.name === selectedCity);

  return (
    <PageContainer>
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3">
        <div>
          <h1 className="text-xl font-bold font-heading text-[#17231C]">{selectedCity} Air Quality Overview</h1>
          <p className="text-xs text-[#69766E]">{cityMeta?.state || 'India'} · Next-day forecast for {formatDate(selectedDate)}</p>
        </div>
        <Link to="/forecast" className="inline-flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-[#173D2D] text-white text-xs font-medium hover:bg-[#102C22] transition-colors"><Wind className="w-3.5 h-3.5" />New Forecast</Link>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-12 gap-4">
        <div className="md:col-span-8 min-w-0">
          <ForecastHeroCard city={selectedCity} prediction={forecastData} loading={loading} error={error} />
        </div>
        <BentoCard title="Select City" icon={MapPin} className="md:col-span-4">
          <CitySelector selectedCity={selectedCity} onSelectCity={(city) => {setSelectedCity(city); loadForecast(city);}} cities={cities} />
        </BentoCard>

        <BentoCard title="India AQI Category" icon={Activity} className="md:col-span-4">
          {forecastData ? <div className="space-y-3 pt-1"><CategoryGauge aqi={forecastData.predicted_next_day_aqi} /><div className="p-2.5 rounded-lg bg-[#F7F8F4] border border-[#E3E8E1] text-xs text-[#69766E]">{category.advisory}</div></div> :
            <p className="text-xs text-[#69766E]">A category will appear when a forecast is available.</p>}
        </BentoCard>

        <BentoCard title="Forecast Summary" icon={Database} className="md:col-span-4">
          <div className="space-y-3 pt-1 text-xs text-[#69766E]">
            <div className="flex justify-between"><span>India AQI</span><strong className="text-[#17231C]">{forecastData?.predicted_next_day_aqi ?? '—'}</strong></div>
            <div className="flex justify-between"><span>PM AQI</span><strong className="text-[#17231C]">{forecastData?.predicted_pm_aqi ?? '—'}</strong></div>
            <div className="flex justify-between"><span>Input days</span><strong className="text-[#17231C]">{forecastData?.input_days ?? '—'}</strong></div>
            <div className="flex justify-between"><span>Model features</span><strong className="text-[#17231C]">{forecastData?.features_prepared ?? '—'} / 118</strong></div>
            <div className="flex justify-between"><span>Latest data date</span><strong className="text-[#17231C]">{health?.latest_data_date || '—'}</strong></div>
          </div>
        </BentoCard>

        <BentoCard title="Backend & Model Status" icon={RefreshCw} className="md:col-span-4">
          <div className="space-y-2 pt-1 text-xs">
            <div className="flex items-center justify-between"><span className="text-[#69766E]">API status</span><span className="font-semibold text-emerald-700">{health?.status || 'Unavailable'}</span></div>
            <div className="flex items-center justify-between"><span className="text-[#69766E]">Supported cities</span><strong className="text-[#17231C]">{health?.available_cities ?? cities.length}</strong></div>
            <div className="flex items-center justify-between"><span className="text-[#69766E]">Full AQI model</span><strong className="text-[#173D2D]">{health?.models?.full_aqi?.loaded ? 'Loaded' : 'Unknown'}</strong></div>
            <div className="flex items-center justify-between"><span className="text-[#69766E]">PM AQI model</span><strong className="text-[#173D2D]">{health?.models?.pm_aqi?.loaded ? 'Loaded' : 'Unknown'}</strong></div>
          </div>
        </BentoCard>

        <div className="md:col-span-12 grid grid-cols-1 sm:grid-cols-3 gap-3 pt-1">
          {[
            {to:'/forecast',icon:Wind,title:'Next-Day Forecast',desc:'Generate a forecast for any supported city'},
            {to:'/comparison',icon:GitCompare,title:'Compare Cities',desc:'Compare next-day predictions'},
            {to:'/health-advisor',icon:HeartPulse,title:'Health Guidance',desc:'Understand AQI categories and precautions'},
          ].map((item) => <Link key={item.to} to={item.to} className="p-3.5 rounded-xl bg-white border border-[#E3E8E1] hover:border-[#173D2D] transition-colors flex items-center justify-between">
            <div className="flex items-center gap-2.5"><div className="w-8 h-8 rounded-lg bg-[#DDEBE0] text-[#173D2D] flex items-center justify-center"><item.icon className="w-4 h-4" /></div><div><div className="text-xs font-bold text-[#17231C]">{item.title}</div><div className="text-[11px] text-[#69766E]">{item.desc}</div></div></div><ArrowRight className="w-3.5 h-3.5 text-[#69766E]" />
          </Link>)}
        </div>
      </div>
    </PageContainer>
  );
}
