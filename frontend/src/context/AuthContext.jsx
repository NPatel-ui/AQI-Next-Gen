import { createContext, useContext, useState, useEffect, useCallback } from 'react';
import { supabase } from '../lib/supabase';
import {
  signInWithEmail,
  signUpWithEmail,
  signOut,
  sendPasswordResetEmail,
  updateUserPassword,
} from '../services/authService';
import { getUserProfile, upsertUserProfile } from '../services/profileService';
import { validateEmail, validatePassword, validateFullName } from '../utils/validation';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [session, setSession] = useState(null);
  const [authUser, setAuthUser] = useState(null);
  const [profile, setProfile] = useState(null);
  const [loading, setLoading] = useState(true);

  // Load and sync user profile from profiles table or user metadata
  const loadProfile = useCallback(async (userObj) => {
    if (!userObj) {
      setProfile(null);
      return null;
    }

    try {
      const dbProfile = await getUserProfile(userObj.id);
      if (dbProfile) {
        setProfile(dbProfile);
        return dbProfile;
      }
    } catch (err) {
      console.warn('Profile fetch note:', err.message);
    }

    // Fallback profile if table is empty or trigger not yet run
    const fallback = {
      id: userObj.id,
      full_name:
        userObj.user_metadata?.full_name ||
        userObj.email?.split('@')[0] ||
        'Analyst',
      email: userObj.email,
      avatar_url: null,
      preferred_city: 'Delhi',
      created_at: userObj.created_at || new Date().toISOString(),
    };
    setProfile(fallback);
    return fallback;
  }, []);

  // Initialize auth session and listen to Supabase auth state changes
  useEffect(() => {
    let mounted = true;

    async function initSession() {
      try {
        const {
          data: { session: initialSession },
          error,
        } = await supabase.auth.getSession();

        if (error) {
          console.warn('Error reading Supabase session:', error.message);
        }

        if (mounted) {
          setSession(initialSession);
          setAuthUser(initialSession?.user ?? null);
          if (initialSession?.user) {
            await loadProfile(initialSession.user);
          }
        }
      } catch (err) {
        console.error('Session initialization exception:', err);
      } finally {
        if (mounted) {
          setLoading(false);
        }
      }
    }

    initSession();

    // Subscribe to auth state updates
    const {
      data: { subscription },
    } = supabase.auth.onAuthStateChange(async (event, currentSession) => {
      if (!mounted) return;

      setSession(currentSession);
      const currentUser = currentSession?.user ?? null;
      setAuthUser(currentUser);

      if (currentUser) {
        await loadProfile(currentUser);
      } else {
        setProfile(null);
      }

      setLoading(false);
    });

    return () => {
      mounted = false;
      subscription?.unsubscribe();
    };
  }, [loadProfile]);

  // Sign In with Supabase
  const signIn = async (email, password) => {
    const emailErr = validateEmail(email);
    if (emailErr) throw new Error(emailErr);

    const passErr = validatePassword(password);
    if (passErr) throw new Error(passErr);

    const result = await signInWithEmail(email, password);
    setSession(result.session);
    setAuthUser(result.user);
    if (result.user) {
      await loadProfile(result.user);
    }
    return result;
  };

  // Sign Up with Supabase
  const signUp = async (name, email, password) => {
    const nameErr = validateFullName(name);
    if (nameErr) throw new Error(nameErr);

    const emailErr = validateEmail(email);
    if (emailErr) throw new Error(emailErr);

    const passErr = validatePassword(password);
    if (passErr) throw new Error(passErr);

    const result = await signUpWithEmail(name, email, password);

    // If confirmation email is required, session might be null initially
    if (result.session) {
      setSession(result.session);
      setAuthUser(result.user);
      await loadProfile(result.user);
    }

    return result;
  };

  // Sign Out
  const logout = async () => {
    await signOut();
    setSession(null);
    setAuthUser(null);
    setProfile(null);
  };

  // Password reset request
  const resetPassword = async (email) => {
    const emailErr = validateEmail(email);
    if (emailErr) throw new Error(emailErr);

    return await sendPasswordResetEmail(email);
  };

  // Update password in recovery or user settings
  const updatePassword = async (newPassword) => {
    const passErr = validatePassword(newPassword);
    if (passErr) throw new Error(passErr);

    return await updateUserPassword(newPassword);
  };

  // Update profile details
  const updateProfile = async (updates) => {
    if (!authUser) throw new Error('User not authenticated');

    const updated = await upsertUserProfile(authUser.id, updates);
    setProfile((prev) => ({ ...prev, ...updated }));
    return updated;
  };

  // Backward-compatible updateUser helper used by ProfilePage
  const updateUser = async (fields) => {
    if (!authUser) return;
    const mapped = {};
    if (fields.name !== undefined) mapped.full_name = fields.name;
    if (fields.preferredCity !== undefined) mapped.preferred_city = fields.preferredCity;
    if (fields.avatarUrl !== undefined) mapped.avatar_url = fields.avatarUrl;

    try {
      await updateProfile(mapped);
    } catch {
      // Local optimistic state update if network or table pending
      setProfile((prev) => ({ ...prev, ...mapped }));
    }
  };

  // Composed user object preserving application conventions
  const user = authUser
    ? {
        id: authUser.id,
        email: authUser.email,
        name:
          profile?.full_name ||
          authUser.user_metadata?.full_name ||
          authUser.email?.split('@')[0] ||
          'Analyst',
        avatarUrl: profile?.avatar_url || null,
        preferredCity: profile?.preferred_city || 'Delhi',
        joinedDate: authUser.created_at
          ? new Date(authUser.created_at).toLocaleDateString('en-US', {
              month: 'long',
              year: 'numeric',
            })
          : 'Active Member',
        status: 'Active',
        authProvider: 'Supabase Auth',
        role: 'Environmental Analyst',
      }
    : null;

  return (
    <AuthContext.Provider
      value={{
        session,
        authUser,
        profile,
        user,
        isAuthenticated: !!authUser,
        loading,
        signIn,
        signUp,
        logout,
        resetPassword,
        updatePassword,
        updateProfile,
        updateUser,
        refreshProfile: () => loadProfile(authUser),
      }}
    >
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
}
