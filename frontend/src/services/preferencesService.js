import { supabase } from '../lib/supabase';

/**
 * Get user preferences
 * @param {string} userId
 */
export async function getUserPreferences(userId) {
  if (!userId) return null;

  try {
    const { data, error } = await supabase
      .from('user_preferences')
      .select('*')
      .eq('user_id', userId)
      .maybeSingle();

    if (error) {
      console.warn('Error fetching preferences:', error.message);
      return null;
    }

    return data;
  } catch (err) {
    console.warn('Network exception fetching preferences:', err.message);
    return null;
  }
}

/**
 * Upsert user preferences
 * @param {string} userId
 * @param {Object} preferences - { preferred_city, notifications_enabled }
 */
export async function upsertUserPreferences(userId, preferences) {
  if (!userId) throw new Error('User ID is required to update preferences.');

  const payload = {
    user_id: userId,
    ...preferences,
    updated_at: new Date().toISOString(),
  };

  const { data, error } = await supabase
    .from('user_preferences')
    .upsert(payload, { onConflict: 'user_id' })
    .select()
    .single();

  if (error) throw error;
  return data;
}

