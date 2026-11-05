import { useState } from 'react';
import {
  HeartPulse,
  Info,
  Wind,
  Home,
  Users,
} from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { BentoCard } from '../components/ui/BentoCard';
import { AQI_CATEGORIES, POLLUTANTS } from '../utils/aqiUtils';

export function HealthAdvisorPage() {
  const [selectedKey, setSelectedKey] = useState('POOR');

  const categories = [
    { key: 'GOOD', ...AQI_CATEGORIES.GOOD },
    { key: 'SATISFACTORY', ...AQI_CATEGORIES.SATISFACTORY },
    { key: 'MODERATE', ...AQI_CATEGORIES.MODERATE },
    { key: 'POOR', ...AQI_CATEGORIES.POOR },
    { key: 'VERY_POOR', ...AQI_CATEGORIES.VERY_POOR },
    { key: 'SEVERE', ...AQI_CATEGORIES.SEVERE },
  ];

  const current = AQI_CATEGORIES[selectedKey] || AQI_CATEGORIES.POOR;

  return (
    <PageContainer>
      {/* Header & Medical Disclaimer */}
      <div className="space-y-3">
        <div>
          <h1 className="text-xl font-bold font-heading text-[#17231C]">
            Health & Activity Guidelines
          </h1>
          <p className="text-xs text-[#69766E] mt-0.5">
            Protective recommendations aligned with CPCB and WHO air quality thresholds.
          </p>
        </div>

        {/* Health Advisory Disclaimer */}
        <div className="p-3.5 rounded-xl bg-[#F7F8F4] border border-[#E3E8E1] text-xs text-[#69766E] flex items-start gap-2.5">
          <HeartPulse className="w-4 h-4 text-[#173D2D] shrink-0 mt-0.5" />
          <div className="leading-relaxed">
            <strong className="text-[#17231C]">Health Guidance Note:</strong> This advisory provides general precautionary guidelines based on environmental air quality thresholds. It does not constitute individual medical advice. Consult healthcare providers for chronic respiratory or cardiovascular conditions.
          </div>
        </div>
      </div>

      {/* Category Selector Pills */}
      <div className="p-3 rounded-xl bg-white border border-[#E3E8E1]">
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-6 gap-2">
          {categories.map((cat) => {
            const isSelected = selectedKey === cat.key;
            return (
              <button
                key={cat.key}
                type="button"
                onClick={() => setSelectedKey(cat.key)}
                className={`p-2.5 rounded-lg border text-left transition-colors ${
                  isSelected
                    ? 'ring-2 ring-[#173D2D] font-semibold'
                    : 'hover:bg-[#F7F8F4] border-[#E3E8E1]'
                }`}
                style={{
                  backgroundColor: isSelected ? cat.bgColor : '#FFFFFF',
                  borderColor: isSelected ? cat.borderColor : '#E3E8E1',
                  color: cat.textColor,
                }}
              >
                <div className="flex items-center justify-between">
                  <span className="text-xs font-bold">{cat.name}</span>
                  <span
                    className="w-2 h-2 rounded-full"
                    style={{ backgroundColor: cat.color }}
                  />
                </div>
                <div className="text-[10px] opacity-80 mt-0.5 font-mono">
                  {cat.min}–{cat.max > 1000 ? '500+' : cat.max} AQI
                </div>
              </button>
            );
          })}
        </div>
      </div>

      {/* Category Advisory Hero */}
      <div
        className="p-5 rounded-2xl border transition-all"
        style={{
          backgroundColor: current.bgColor,
          borderColor: current.borderColor,
          color: current.textColor,
        }}
      >
        <div className="flex items-center justify-between pb-3 border-b border-current/15">
          <h2 className="text-2xl font-bold font-heading">{current.name} Category</h2>
          <span className="text-xs font-mono font-semibold">
            {current.min}–{current.max > 1000 ? '500+' : current.max} AQI
          </span>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-4 pt-3 text-xs leading-relaxed">
          <div>
            <strong className="block mb-1 text-[11px] uppercase tracking-wider opacity-85">
              General Precautions
            </strong>
            <p>{current.advisory}</p>
          </div>
          <div>
            <strong className="block mb-1 text-[11px] uppercase tracking-wider opacity-85">
              Outdoor Activities
            </strong>
            <p>{current.outdoorGuidance}</p>
          </div>
        </div>
      </div>

      {/* 2-Column Bento: Sensitive Groups & Indoor Air / Masks */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
        {/* Sensitive Groups */}
        <BentoCard title="Sensitive Demographics" icon={Users}>
          <div className="space-y-2.5 pt-1 text-xs text-[#17231C]">
            <div className="p-2.5 rounded-lg bg-[#F7F8F4] border border-[#E3E8E1] space-y-0.5">
              <strong className="text-[#173D2D]">Asthma & Respiratory Patients:</strong>
              <p className="text-[#69766E]">
                Keep rescue inhalers accessible. Avoid outdoor exertion in early mornings when pollution concentrates near ground level.
              </p>
            </div>
            <div className="p-2.5 rounded-lg bg-[#F7F8F4] border border-[#E3E8E1] space-y-0.5">
              <strong className="text-[#173D2D]">Cardiovascular Conditions:</strong>
              <p className="text-[#69766E]">
                Fine particulates strain cardiovascular systems. Reduce heavy outdoor physical activity when AQI exceeds 150.
              </p>
            </div>
            <div className="p-2.5 rounded-lg bg-[#F7F8F4] border border-[#E3E8E1] space-y-0.5">
              <strong className="text-[#173D2D]">Children & Elderly:</strong>
              <p className="text-[#69766E]">
                Restrict outdoor playtime and prolonged exposure during Poor or Severe pollution episodes.
              </p>
            </div>
          </div>
        </BentoCard>

        {/* Indoor Air & Masks */}
        <BentoCard title="Masks & Indoor Air" icon={Home}>
          <div className="space-y-2.5 pt-1 text-xs text-[#17231C]">
            <div className="p-2.5 rounded-lg bg-[#F7F8F4] border border-[#E3E8E1] space-y-0.5">
              <strong className="text-[#173D2D]">N95 / FFP2 Respirators:</strong>
              <p className="text-[#69766E]">
                Cloth masks do not filter fine PM2.5. Use certified N95 or FFP2 respirators with a snug facial fit outdoors.
              </p>
            </div>
            <div className="p-2.5 rounded-lg bg-[#F7F8F4] border border-[#E3E8E1] space-y-0.5">
              <strong className="text-[#173D2D]">Indoor Air Purification:</strong>
              <p className="text-[#69766E]">
                Keep windows closed during high pollution hours. Operate HEPA air purifiers in occupied living and sleeping rooms.
              </p>
            </div>
            <div className="p-2.5 rounded-lg bg-[#F7F8F4] border border-[#E3E8E1] space-y-0.5">
              <strong className="text-[#173D2D]">Avoid Indoor Combustion:</strong>
              <p className="text-[#69766E]">
                Refrain from burning incense, candles, or unvented biomass indoors during stagnant air advisories.
              </p>
            </div>
          </div>
        </BentoCard>
      </div>

      {/* Pollutant Health Reference Matrix */}
      <BentoCard title="Pollutant Impact Reference" icon={Wind}>
        <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-2.5 pt-1">
          {POLLUTANTS.map((p) => (
            <div
              key={p.key}
              className="p-3 rounded-xl bg-[#F7F8F4] border border-[#E3E8E1] space-y-1 text-xs"
            >
              <div className="flex items-center justify-between">
                <span className="font-bold text-[#173D2D] font-mono">{p.label}</span>
                <span className="text-[10px] text-[#69766E]">{p.unit}</span>
              </div>
              <p className="text-[11px] text-[#69766E] leading-relaxed">
                {p.key === 'PM2.5' && 'Enters bloodstream capillaries; increases cardiopulmonary strain.'}
                {p.key === 'PM10' && 'Deposits in upper airways; causes coughing and throat irritation.'}
                {p.key === 'NO2' && 'Aggravates respiratory passages and increases asthma sensitivity.'}
                {p.key === 'CO' && 'Reduces oxygen delivery through hemoglobin binding.'}
                {p.key === 'SO2' && 'Irritates eyes and throat; triggers bronchospasms in asthmatics.'}
                {p.key === 'O3' && 'Surface ozone causes airway constriction and reduced lung capacity.'}
              </p>
            </div>
          ))}
        </div>
      </BentoCard>
    </PageContainer>
  );
}
