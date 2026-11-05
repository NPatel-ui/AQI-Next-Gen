/**
 * AQI Utilities and CPCB Standard Categorization
 */

export const AQI_CATEGORIES = {
  GOOD: {
    min: 0,
    max: 50,
    name: 'Good',
    code: 'good',
    color: '#10B981',
    bgColor: '#ECFDF5',
    borderColor: '#A7F3D0',
    textColor: '#065F46',
    advisory: 'Air quality is considered satisfactory, and air pollution poses little or no risk.',
    outdoorGuidance: 'Ideal conditions for all outdoor activities and exercise.',
  },
  SATISFACTORY: {
    min: 51,
    max: 100,
    name: 'Satisfactory',
    code: 'satisfactory',
    color: '#22C55E',
    bgColor: '#F0FDF4',
    borderColor: '#BBF7D0',
    textColor: '#166534',
    advisory: 'Minor breathing discomfort to sensitive people; acceptable air quality for general public.',
    outdoorGuidance: 'Safe for general public; sensitive individuals should consider taking pauses if coughing.',
  },
  MODERATE: {
    min: 101,
    max: 200,
    name: 'Moderate',
    code: 'moderate',
    color: '#F59E0B',
    bgColor: '#FFFBEB',
    borderColor: '#FDE68A',
    textColor: '#92400E',
    advisory: 'Breathing discomfort to people with asthma, heart and lung diseases.',
    outdoorGuidance: 'Children and older adults should reduce prolonged or heavy outdoor exertion.',
  },
  POOR: {
    min: 201,
    max: 300,
    name: 'Poor',
    code: 'poor',
    color: '#F97316',
    bgColor: '#FFF7ED',
    borderColor: '#FED7AA',
    textColor: '#9A3412',
    advisory: 'Breathing discomfort to most people on prolonged exposure; health alert triggered.',
    outdoorGuidance: 'Avoid prolonged outdoor exertion; wear an N95 mask in high-traffic zones.',
  },
  VERY_POOR: {
    min: 301,
    max: 400,
    name: 'Very Poor',
    code: 'very_poor',
    color: '#EF4444',
    bgColor: '#FEF2F2',
    borderColor: '#FECACA',
    textColor: '#991B1B',
    advisory: 'Respiratory illness on prolonged exposure. Significant risk for susceptible groups.',
    outdoorGuidance: 'Limit outdoor activities strictly. Keep windows closed and operate HEPA purifiers.',
  },
  SEVERE: {
    min: 401,
    max: 9999,
    name: 'Severe',
    code: 'severe',
    color: '#881337',
    bgColor: '#FFF1F2',
    borderColor: '#FECDD3',
    textColor: '#881337',
    advisory: 'Affects healthy individuals and causes severe impacts on those with existing disease.',
    outdoorGuidance: 'Hazardous. Everyone should avoid all outdoor physical activity.',
  },
};

export function getAqiCategory(value) {
  if (value === null || value === undefined || value === '' || !Number.isFinite(Number(value))) {
    return {
      name: 'Unknown',
      code: 'unknown',
      color: '#69766E',
      bgColor: '#F1F4EE',
      borderColor: '#E3E8E1',
      textColor: '#17231C',
      advisory: 'No AQI reading recorded or available for this selection.',
      outdoorGuidance: 'Data unavailable.',
    };
  }

  const aqi = Number(value);
  if (aqi <= 50) return AQI_CATEGORIES.GOOD;
  if (aqi <= 100) return AQI_CATEGORIES.SATISFACTORY;
  if (aqi <= 200) return AQI_CATEGORIES.MODERATE;
  if (aqi <= 300) return AQI_CATEGORIES.POOR;
  if (aqi <= 400) return AQI_CATEGORIES.VERY_POOR;
  return AQI_CATEGORIES.SEVERE;
}

export function formatAqi(value) {
  if (value === null || value === undefined || value === '' || !Number.isFinite(Number(value))) return '—';
  return Math.round(Number(value)).toString();
}

export function formatDate(dateString) {
  if (!dateString) return '—';
  try {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-IN', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  } catch {
    return dateString;
  }
}

export const POLLUTANTS = [
  { key: 'PM2.5', label: 'PM2.5', unit: 'µg/m³', desc: 'Fine particulate matter (≤ 2.5 µm)' },
  { key: 'PM10', label: 'PM10', unit: 'µg/m³', desc: 'Respirable particulate matter (≤ 10 µm)' },
  { key: 'NO2', label: 'NO₂', unit: 'µg/m³', desc: 'Nitrogen dioxide from emissions' },
  { key: 'CO', label: 'CO', unit: 'mg/m³', desc: 'Carbon monoxide from incomplete combustion' },
  { key: 'SO2', label: 'SO₂', unit: 'µg/m³', desc: 'Sulfur dioxide from industrial operations' },
  { key: 'O3', label: 'O₃', unit: 'µg/m³', desc: 'Ground-level photochemical ozone' },
];

