import { useMemo, useState } from 'react';
import { Search, Check } from 'lucide-react';
import { ELIGIBLE_CITIES } from '../../utils/datasetInfo';

export function CitySelector({ selectedCity, onSelectCity, cities = [], className = '' }) {
  const [search, setSearch] = useState('');
  const available = cities.length
    ? cities.map((name) => {
        const meta = ELIGIBLE_CITIES.find((city) => city.name.toLowerCase() === name.toLowerCase());
        return meta || { name, state: '' };
      })
    : ELIGIBLE_CITIES;

  const quickNames = ['Delhi', 'Mumbai', 'Bengaluru', 'Kolkata', 'Chennai', 'Hyderabad'];
  const quickCities = quickNames.filter((name) => available.some((city) => city.name === name));
  const filtered = useMemo(() => available.filter((city) =>
    city.name.toLowerCase().includes(search.toLowerCase()) ||
    (city.state || '').toLowerCase().includes(search.toLowerCase())
  ), [available, search]);

  return (
    <div className={`space-y-3 ${className}`}>
      <div className="flex items-center gap-1.5 flex-wrap">
        {quickCities.map((city) => (
          <button key={city} type="button" onClick={() => onSelectCity(city)}
            className={`px-2.5 py-1 rounded-lg text-xs font-medium transition-colors ${
              selectedCity === city ? 'bg-[#173D2D] text-[#B7E46A]' : 'bg-white text-[#17231C] border border-[#E3E8E1] hover:bg-[#F7F8F4]'
            }`}>{city}</button>
        ))}
      </div>
      <div className="relative">
        <Search className="w-3.5 h-3.5 absolute left-3 top-1/2 -translate-y-1/2 text-[#69766E]" />
        <input type="text" value={search} onChange={(e) => setSearch(e.target.value)}
          placeholder="Search all supported cities..."
          className="w-full pl-8 pr-3 py-2 text-xs rounded-xl border border-[#E3E8E1] bg-white text-[#17231C] focus:outline-none focus:ring-1 focus:ring-[#173D2D]" />
      </div>
      <div className="grid grid-cols-2 sm:grid-cols-3 gap-1.5 max-h-56 overflow-y-auto pr-1">
        {filtered.map((item) => {
          const selected = selectedCity === item.name;
          return <button key={item.name} type="button" onClick={() => onSelectCity(item.name)}
            className={`flex items-center justify-between p-2 rounded-lg border text-left transition-colors ${
              selected ? 'bg-[#DDEBE0] border-[#173D2D] text-[#173D2D] font-semibold' : 'bg-white border-[#E3E8E1] text-[#17231C] hover:bg-[#F7F8F4]'
            }`}>
            <div className="min-w-0 pr-1">
              <div className="text-xs font-medium truncate">{item.name}</div>
              <div className="text-[10px] text-[#69766E] truncate">{item.state || 'India'}</div>
            </div>
            {selected && <Check className="w-3 h-3 text-[#173D2D] shrink-0" />}
          </button>;
        })}
        {!filtered.length && <p className="col-span-full text-xs text-[#69766E] py-3 text-center">No matching city.</p>}
      </div>
    </div>
  );
}
