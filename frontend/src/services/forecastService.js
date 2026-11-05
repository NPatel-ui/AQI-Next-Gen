import { supabase } from '../lib/supabase';

/**
 * Save an explicitly selected air quality prediction
 * @param {Object} forecastData
 * @param {string} forecastData.city
 * @param {string} forecastData.forecastDate
 * @param {number} forecastData.predictedAqi
 * @param {string} forecastData.aqiCategory
 */
export async function saveForecast({
  city,
  forecastDate,
  predictedAqi,
  aqiCategory,
}) {
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) {
    throw new Error('Authentication required to save forecasts.');
  }

  const { data, error } = await supabase
    .from('saved_forecasts')
    .insert([
      {
        user_id: user.id,
        city: city.trim(),
        forecast_date: forecastDate,
        predicted_aqi: Number(predictedAqi),
        aqi_category: aqiCategory,
      },
    ])
    .select()
    .single();

  if (error) throw error;
  return data;
}

/**
 * Retrieve saved forecasts for the authenticated user
 */
export async function getSavedForecasts() {
  const {
    data: { user },
  } = await supabase.auth.getUser();

  if (!user) return [];

  const { data, error } = await supabase
    .from('saved_forecasts')
    .select('*')
    .order('created_at', { ascending: false });

  if (error) {
    console.warn('Error fetching saved forecasts:', error.message);
    return [];
  }

  return data || [];
}

/**
 * Delete a saved forecast by its UUID
 * @param {string} id
 */
export async function deleteSavedForecast(id) {
  const { error } = await supabase
    .from('saved_forecasts')
    .delete()
    .eq('id', id);

  if (error) throw error;
  return true;
}

