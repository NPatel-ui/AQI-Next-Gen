import { supabase } from '../lib/supabase';

/**
 * Fetch a user profile from the profiles table
 * @param {string} userId
 */
export async function getUserProfile(userId) {
  if (!userId) return null;

  try {
    const { data, error } = await supabase
      .from('profiles')
      .select('*')
      .eq('id', userId)
      .maybeSingle();

    if (error) {
      console.warn('Error fetching profile from Supabase:', error.message);
      return null;
    }

    return data;
  } catch (err) {
    console.warn('Network or schema exception fetching profile:', err.message);
    return null;
  }
}

/**
 * Upsert or update user profile
 * @param {string} userId
 * @param {Object} updates - { full_name, email, preferred_city, avatar_url }
 */
export async function upsertUserProfile(userId, updates) {
  if (!userId) throw new Error('User ID is required to update profile.');

  const payload = {
    id: userId,
    ...updates,
    updated_at: new Date().toISOString(),
  };

  const { data, error } = await supabase
    .from('profiles')
    .upsert(payload)
    .select()
    .single();

  if (error) throw error;
  return data;
}

