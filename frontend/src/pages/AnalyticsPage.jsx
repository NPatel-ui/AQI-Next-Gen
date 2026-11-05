import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Activity, BarChart3, CalendarDays, Droplets, Filter, Gauge,
  RefreshCw, Wind, AlertCircle, LoaderCircle,
} from 'lucide-react';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid,
  Tooltip, BarChart, Bar, PieChart, Pie, Cell, Legend, ScatterChart,
  Scatter, ZAxis,
} from 'recharts';
import { PageContainer } from '../components/layout/PageContainer';
import { BentoCard } from '../components/ui/BentoCard';
import {
  getAvailableCities,
  getHistoricalAnalytics,
  getHistoricalAnalyticsSummary,
} from '../services/api';

const COLORS = ['#16A36A', '#84CC16', '#EAB308', '#F97316', '#DC2626', '#7F1D1D'];
const POLLUTANTS = [
  { value: 'pm2_5_mean', label: 'PM2.5' },
  { value: 'pm10_mean', label: 'PM10' },
  { value: 'no2_mean', label: 'NO₂' },
  { value: 'so2_mean', label: 'SO₂' },
  { value: 'o3_8h_max', label: 'O₃ (8-hour max)' },
  { value: 'co_8h_max', label: 'CO (8-hour max)' },
];

const inputClass = 'w-full rounded-lg border border-[#E3E8E1] bg-white px-3 py-2 text-sm text-[#17231C] outline-none focus:border-[#173D2D]';
const chartTooltip = {
  contentStyle: { borderRadius: 12, border: '1px solid #E3E8E1', fontSize: 12 },
};

function ChartEmpty({ message = 'No historical records for the selected filters.' }) {
  return <div className="h-64 flex items-center justify-center text-sm text-[#8E9C94]">{message}</div>;
}

function formatMonth(value) {
  if (!value) return '';
  const date = new Date(`${value}T00:00:00`);
  return date.toLocaleDateString('en-IN', { month: 'short', year: '2-digit' });
}

function FilterBar({ cities, filters, setFilters, summary, onRefresh, refreshing }) {
  return (
    <div className="rounded-2xl border border-[#E3E8E1] bg-white p-4">
      <div className="flex items-center gap-2 mb-3 text-sm font-semibold text-[#173D2D]">
        <Filter className="w-4 h-4" /> Analytics filters
      </div>
      <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-5 gap-3">
        <label className="text-xs font-medium text-[#69766E] space-y-1">
          City
          <select className={inputClass} value={filters.city} onChange={(e) => setFilters((f) => ({ ...f, city: e.target.value }))}>
            <option value="All">All 50 cities</option>
            {cities.map((city) => <option key={city} value={city}>{city}</option>)}
          </select>
        </label>
        <label className="text-xs font-medium text-[#69766E] space-y-1">
          AQI metric
          <select className={inputClass} value={filters.metric} onChange={(e) => setFilters((f) => ({ ...f, metric: e.target.value }))}>
            <option value="india_aqi">India AQI</option>
            <option value="india_aqi_pm">PM AQI</option>
          </select>
        </label>
        <label className="text-xs font-medium text-[#69766E] space-y-1">
          Start date
          <input className={inputClass} type="date" min={summary?.start_date} max={filters.end_date || summary?.end_date} value={filters.start_date} onChange={(e) => setFilters((f) => ({ ...f, start_date: e.target.value }))} />
        </label>
        <label className="text-xs font-medium text-[#69766E] space-y-1">
          End date
          <input className={inputClass} type="date" min={filters.start_date || summary?.start_date} max={summary?.end_date} value={filters.end_date} onChange={(e) => setFilters((f) => ({ ...f, end_date: e.target.value }))} />
        </label>
        <div className="flex items-end">
          <button type="button" onClick={onRefresh} disabled={refreshing} className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-[#173D2D] px-3 py-2 text-sm font-semibold text-white hover:bg-[#102C22] disabled:opacity-60">
            <RefreshCw className={`w-4 h-4 ${refreshing ? 'animate-spin' : ''}`} /> Refresh charts
          </button>
        </div>
      </div>
      {filters.start_date && filters.end_date && filters.start_date > filters.end_date && (
        <p className="mt-2 text-xs text-red-600">Start date must be earlier than or equal to end date.</p>
      )}
    </div>
  );
}

export function AnalyticsPage() {
  const [cities, setCities] = useState([]);
  const [summary, setSummary] = useState(null);
  const [filters, setFilters] = useState({ city: 'All', metric: 'india_aqi', start_date: '', end_date: '', pollutant: 'pm2_5_mean' });
  const [analytics, setAnalytics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);
  const [error, setError] = useState('');

  const loadSummary = useCallback(async () => {
    const [summaryData, cityResult] = await Promise.all([
      getHistoricalAnalyticsSummary(),
      getAvailableCities(),
    ]);
    setSummary(summaryData);
    if (cityResult.success) setCities(cityResult.data);
    setFilters((current) => ({
      ...current,
      start_date: current.start_date || summaryData.start_date,
      end_date: current.end_date || summaryData.end_date,
    }));
  }, []);

  const loadCharts = useCallback(async (activeFilters) => {
    if (!activeFilters.start_date || !activeFilters.end_date || activeFilters.start_date > activeFilters.end_date) return;
    setRefreshing(true);
    setError('');
    try {
      const data = await getHistoricalAnalytics(activeFilters);
      setAnalytics(data);
    } catch (err) {
      setError(err?.response?.data?.detail || err.message || 'Unable to load historical analytics.');
      setAnalytics(null);
    } finally {
      setRefreshing(false);
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        await loadSummary();
      } catch (err) {
        if (active) {
          setError(err?.response?.data?.detail || err.message || 'Could not load historical dataset information.');
          setLoading(false);
        }
      }
    })();
    return () => { active = false; };
  }, [loadSummary]);

  useEffect(() => {
    if (summary && filters.start_date && filters.end_date) {
      loadCharts(filters);
    }
  }, [summary, filters.city, filters.metric, filters.start_date, filters.end_date, filters.pollutant, loadCharts]);

  const averageAqi = analytics?.trends?.overall_average == null
    ? '—'
    : Number(analytics.trends.overall_average).toFixed(1);

  const categoryData = analytics?.categories?.data || [];
  const trendData = (analytics?.trends?.data || []).map((item) => ({ ...item, label: formatMonth(item.date) }));
  const cityData = analytics?.cities?.data || [];
  const pollutantData = (analytics?.pollutants?.data || []).map((item) => ({ ...item, label: formatMonth(item.date) }));
  const seasonalData = analytics?.seasonal?.monthly || [];
  const weatherData = analytics?.weather?.scatter || [];

  if (loading && !summary) {
    return <PageContainer><div className="flex items-center gap-2 text-sm text-[#69766E]"><LoaderCircle className="w-4 h-4 animate-spin" /> Loading historical dataset...</div></PageContainer>;
  }

  return (
    <PageContainer>
      <div>
        <div className="flex items-center gap-2 text-[#173D2D]"><Activity className="w-5 h-5" /><span className="text-xs font-semibold uppercase tracking-wide">Historical data exploration</span></div>
        <h1 className="mt-1 text-2xl font-bold font-heading text-[#17231C]">Historical AQI Analytics</h1>
        <p className="mt-1 text-sm text-[#69766E]">Explore actual daily pollution and weather records across Indian cities. Charts use the historical merged dataset, not future forecasts.</p>
      </div>

      {summary && (
        <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
          {[
            ['Historical records', Number(summary.records).toLocaleString('en-IN'), 'daily records'],
            ['Cities covered', summary.cities, 'Indian cities'],
            ['Historical period', summary.start_date, `through ${summary.end_date}`],
            ['Average AQI in view', averageAqi, filters.metric === 'india_aqi' ? 'India AQI · selected period' : 'PM AQI · selected period'],
          ].map(([title, value, description]) => (
            <div key={title} className="rounded-xl border border-[#E3E8E1] bg-white p-4">
              <div className="text-xs text-[#69766E]">{title}</div>
              <div className="mt-1 text-xl font-bold text-[#17231C] break-words">{value}</div>
              <div className="mt-1 text-[11px] text-[#8E9C94]">{description}</div>
            </div>
          ))}
        </div>
      )}

      {summary && <FilterBar cities={cities} filters={filters} setFilters={setFilters} summary={summary} onRefresh={() => loadCharts(filters)} refreshing={refreshing} />}

      {error && <div className="rounded-xl border border-red-200 bg-red-50 p-3 text-sm text-red-700 flex items-start gap-2"><AlertCircle className="w-4 h-4 mt-0.5 shrink-0" />{error}</div>}

      {refreshing && <div className="text-xs text-[#69766E] flex items-center gap-2"><LoaderCircle className="w-3.5 h-3.5 animate-spin" /> Updating charts from historical records...</div>}

      <div className="grid grid-cols-1 xl:grid-cols-2 gap-4">
        <BentoCard title="Historical AQI trend" subtitle={`${filters.city === 'All' ? 'Average across all cities' : filters.city} · monthly average`} icon={Activity}>
          {trendData.length ? <div className="h-72 pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={trendData} margin={{ top: 8, right: 16, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E8EDE7" />
                <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#69766E' }} />
                <YAxis tick={{ fontSize: 11, fill: '#69766E' }} />
                <Tooltip {...chartTooltip} formatter={(value) => [`${Number(value).toFixed(1)} AQI`, 'Average']} />
                <Line type="monotone" dataKey="value" stroke="#16845B" strokeWidth={2.5} dot={false} activeDot={{ r: 4 }} />
              </LineChart>
            </ResponsiveContainer>
          </div> : <ChartEmpty /> }
        </BentoCard>

        <BentoCard title="City-wise AQI comparison" subtitle="Average AQI, highest to lowest" icon={BarChart3}>
          {cityData.length ? <div className="h-[620px] pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={cityData} layout="vertical" margin={{ top: 4, right: 20, left: 16, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" horizontal={false} stroke="#E8EDE7" />
                <XAxis type="number" tick={{ fontSize: 10, fill: '#69766E' }} />
                <YAxis type="category" dataKey="city" width={88} tick={{ fontSize: 10, fill: '#69766E' }} />
                <Tooltip {...chartTooltip} formatter={(value) => [`${Number(value).toFixed(1)}`, 'Average AQI']} />
                <Bar dataKey="average" fill="#4B8B69" radius={[0, 5, 5, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div> : <ChartEmpty /> }
        </BentoCard>

        <BentoCard title="AQI category distribution" subtitle="Historical record counts by CPCB category" icon={Gauge}>
          {categoryData.length ? <div className="h-72 flex flex-col sm:flex-row items-center">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie data={categoryData} dataKey="records" nameKey="category" cx="50%" cy="50%" innerRadius={58} outerRadius={92} paddingAngle={2}>
                  {categoryData.map((entry, index) => <Cell key={entry.category} fill={COLORS[index % COLORS.length]} />)}
                </Pie>
                <Tooltip {...chartTooltip} formatter={(value, name) => [Number(value).toLocaleString('en-IN'), name]} />
                <Legend verticalAlign="bottom" height={44} wrapperStyle={{ fontSize: 11 }} />
              </PieChart>
            </ResponsiveContainer>
          </div> : <ChartEmpty /> }
        </BentoCard>

        <BentoCard title="Pollutant concentration trend" subtitle={`${POLLUTANTS.find((item) => item.value === filters.pollutant)?.label || 'Pollutant'} · monthly average`} icon={Wind} action={
          <select aria-label="Select pollutant" className="rounded-lg border border-[#E3E8E1] bg-white px-2 py-1 text-xs" value={filters.pollutant} onChange={(e) => setFilters((f) => ({ ...f, pollutant: e.target.value }))}>
            {POLLUTANTS.map((item) => <option key={item.value} value={item.value}>{item.label}</option>)}
          </select>
        }>
          {pollutantData.length ? <div className="h-72 pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <LineChart data={pollutantData} margin={{ top: 8, right: 16, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E8EDE7" />
                <XAxis dataKey="label" tick={{ fontSize: 11, fill: '#69766E' }} />
                <YAxis tick={{ fontSize: 11, fill: '#69766E' }} />
                <Tooltip {...chartTooltip} formatter={(value) => [`${Number(value).toFixed(2)} ${analytics?.pollutants?.unit || ''}`, 'Average concentration']} />
                <Line type="monotone" dataKey="value" stroke="#D18A28" strokeWidth={2.5} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          </div> : <ChartEmpty /> }
        </BentoCard>

        <BentoCard title="Monthly and seasonal patterns" subtitle="Average AQI by calendar month" icon={CalendarDays}>
          {seasonalData.length ? <div className="h-72 pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={seasonalData} margin={{ top: 8, right: 12, left: 0, bottom: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E8EDE7" />
                <XAxis dataKey="month_name" tick={{ fontSize: 11, fill: '#69766E' }} />
                <YAxis tick={{ fontSize: 11, fill: '#69766E' }} />
                <Tooltip {...chartTooltip} formatter={(value) => [`${Number(value).toFixed(1)} AQI`, 'Monthly average']} />
                <Bar dataKey="average" fill="#739B79" radius={[5, 5, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div> : <ChartEmpty /> }
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2">
            {(analytics?.seasonal?.seasonal || []).map((item) => <div key={item.season} className="rounded-lg bg-[#F7F8F4] border border-[#E3E8E1] p-2"><div className="text-[10px] text-[#69766E]">{item.season}</div><div className="text-sm font-bold">{item.average ?? '—'}</div></div>)}
          </div>
        </BentoCard>

        <BentoCard title="Weather and AQI relationship" subtitle="Historical relative humidity vs AQI · sample of up to 800 records" icon={Droplets}>
          {weatherData.length ? <div className="h-72 pt-2">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 8, right: 16, bottom: 12, left: 4 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#E8EDE7" />
                <XAxis type="number" dataKey="weather_value" name="Relative humidity" unit="%" tick={{ fontSize: 10, fill: '#69766E' }} />
                <YAxis type="number" dataKey="aqi" name="AQI" tick={{ fontSize: 10, fill: '#69766E' }} />
                <ZAxis range={[28, 28]} />
                <Tooltip {...chartTooltip} cursor={{ strokeDasharray: '3 3' }} />
                <Scatter data={weatherData} fill="#3D8060" fillOpacity={0.55} />
              </ScatterChart>
            </ResponsiveContainer>
          </div> : <ChartEmpty /> }
          <div className="grid grid-cols-2 sm:grid-cols-4 gap-2 mt-2">
            {(analytics?.weather?.correlations || []).map((item) => <div key={item.weather_variable} className="rounded-lg bg-[#F7F8F4] border border-[#E3E8E1] p-2"><div className="text-[10px] text-[#69766E]">{item.label}</div><div className="text-sm font-bold">{item.correlation ?? '—'}</div><div className="text-[10px] text-[#8E9C94]">Pearson r</div></div>)}
          </div>
          <p className="text-[10px] text-[#8E9C94] mt-2">Correlation indicates association, not causation.</p>
        </BentoCard>
      </div>
      <p className="text-[11px] text-[#8E9C94]">Source: {summary?.source || 'historical merged dataset'} · {summary?.records?.toLocaleString('en-IN')} records · All charts update using the selected city, metric and date range.</p>
    </PageContainer>
  );
}
