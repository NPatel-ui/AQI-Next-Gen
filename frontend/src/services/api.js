import axios from 'axios';

// In development, Vite proxies /api to FastAPI without rewriting the path.
// In production, set VITE_API_URL to the backend origin, optionally ending in /api.
const configuredUrl = import.meta.env.VITE_API_URL?.trim().replace(/\/+$/, '');

export const API_BASE = configuredUrl
  ? (configuredUrl.endsWith('/api') ? configuredUrl : `${configuredUrl}/api`)
  : '/api';

export const apiClient = axios.create({
  baseURL: API_BASE,
  timeout: 60000,
  headers: { 'Content-Type': 'application/json' },
});

function getErrorMessage(error) {
  const detail = error?.response?.data?.detail;
  if (typeof detail === 'string') return detail;
  if (detail && typeof detail === 'object') {
    return detail.message || JSON.stringify(detail);
  }
  if (error?.code === 'ECONNABORTED') return 'The AQI backend took too long to respond. Please try again.';
  if (!error?.response) return 'Cannot connect to the AQI backend. Check that FastAPI is running.';
  return error.message || 'The request could not be completed.';
}

export async function checkBackendHealth() {
  try {
    const { data } = await apiClient.get('/health');
    return { connected: true, data, error: null };
  } catch (error) {
    return { connected: false, data: null, error: getErrorMessage(error) };
  }
}

export async function getAvailableCities() {
  try {
    const { data } = await apiClient.get('/cities');
    return { success: true, data: data.cities || [], error: null };
  } catch (error) {
    return { success: false, data: [], error: getErrorMessage(error) };
  }
}

export async function getCityForecast(city, forecastDate) {
  try {
    const { data } = await apiClient.post('/forecast/by-city-date', {
      city,
      forecast_date: forecastDate,
    });

    const full = data?.results?.full_aqi;
    const pm = data?.results?.pm_aqi;
    if (!full || !pm) {
      throw new Error('The backend response did not contain both AQI model results.');
    }

    return {
      success: true,
      error: null,
      data: {
        ...data,
        feature_date: data.input_end_date,
        prediction_for_date: data.forecast_date,
        predicted_next_day_aqi: full.predicted_aqi,
        predicted_pm_aqi: pm.predicted_aqi,
        raw_full_aqi: full.raw_prediction,
        raw_pm_aqi: pm.raw_prediction,
      },
    };
  } catch (error) {
    return { success: false, data: null, error: getErrorMessage(error) };
  }
}

// The current FastAPI backend does not expose a benchmark endpoint.
export async function getModelBenchmarks() {
  return {
    success: false,
    data: null,
    error: 'Model benchmarks are documented in the project evaluation report, not exposed by this API.',
  };
}

// ==================================================
// HISTORICAL ANALYTICS API
// ==================================================

export async function getHistoricalAnalyticsSummary() {
  const { data } = await apiClient.get('/analytics/summary');
  return data;
}

export async function getHistoricalAnalytics(params) {
  const [
    trends,
    cities,
    categories,
    pollutants,
    seasonal,
    weather,
  ] = await Promise.all([
    apiClient.get('/analytics/trends', {
      params: { ...params, group_by: 'monthly' },
    }),

    apiClient.get('/analytics/cities', {
      params: {
        metric: params.metric,
        start_date: params.start_date,
        end_date: params.end_date,
        limit: 50,
      },
    }),

    apiClient.get('/analytics/categories', {
      params: {
        metric: params.metric,
        city: params.city,
        start_date: params.start_date,
        end_date: params.end_date,
      },
    }),

    apiClient.get('/analytics/pollutants', {
      params: {
        pollutant: params.pollutant,
        city: params.city,
        start_date: params.start_date,
        end_date: params.end_date,
        group_by: 'monthly',
      },
    }),

    apiClient.get('/analytics/seasonal', {
      params: {
        metric: params.metric,
        city: params.city,
        start_date: params.start_date,
        end_date: params.end_date,
      },
    }),

    apiClient.get('/analytics/weather', {
      params: {
        metric: params.metric,
        city: params.city,
        start_date: params.start_date,
        end_date: params.end_date,
      },
    }),
  ]);

  return {
    trends: trends.data,
    cities: cities.data,
    categories: categories.data,
    pollutants: pollutants.data,
    seasonal: seasonal.data,
    weather: weather.data,
  };
}

