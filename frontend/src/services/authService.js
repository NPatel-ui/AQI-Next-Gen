import { supabase } from '../lib/supabase';

/**
 * Register a new user with Supabase Auth
 * @param {string} fullName
 * @param {string} email
 * @param {string} password
 */
export async function signUpWithEmail(fullName, email, password) {
  const { data, error } = await supabase.auth.signUp({
    email: email.trim().toLowerCase(),
    password,
    options: {
      data: {
        full_name: fullName.trim(),
      },
    },
  });

  if (error) throw error;
  return data;
}

/**
 * Sign in an existing user with Supabase Auth
 * @param {string} email
 * @param {string} password
 */
export async function signInWithEmail(email, password) {
  const { data, error } = await supabase.auth.signInWithPassword({
    email: email.trim().toLowerCase(),
    password,
  });

  if (error) throw error;
  return data;
}

/**
 * Sign out the current user
 */
export async function signOut() {
  const { error } = await supabase.auth.signOut();
  if (error) throw error;
  return true;
}

/**
 * Send password reset email
 * @param {string} email
 */
export async function sendPasswordResetEmail(email) {
  const redirectUrl =
    typeof window !== 'undefined'
      ? `${window.location.origin}/reset-password`
      : undefined;

  const { data, error } = await supabase.auth.resetPasswordForEmail(
    email.trim().toLowerCase(),
    {
      redirectTo: redirectUrl,
    }
  );

  if (error) throw error;
  return data;
}

/**
 * Update authenticated user's password
 * @param {string} newPassword
 */
export async function updateUserPassword(newPassword) {
  const { data, error } = await supabase.auth.updateUser({
    password: newPassword,
  });

  if (error) throw error;
  return data;
}

/**
 * Get current session
 */
export async function getCurrentSession() {
  const { data, error } = await supabase.auth.getSession();
  if (error) throw error;
  return data.session;
}

/**
 * Get current user
 */
export async function getCurrentUser() {
  const { data, error } = await supabase.auth.getUser();
  if (error) throw error;
  return data.user;
}

