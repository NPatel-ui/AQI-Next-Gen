
-- =============================================================================
-- AQI FORECASTER
-- SUPABASE DATABASE SCHEMA & SECURITY POLICIES
-- =============================================================================
--
-- Tables:
--   1. public.profiles
--   2. public.saved_forecasts
--   3. public.user_preferences
--
-- Features:
--   - Automatic profile creation after signup
--   - Automatic user preferences creation
--   - Row Level Security (RLS)
--   - Secure user-owned records
--   - Automatic updated_at timestamps
--
-- IMPORTANT:
-- Run this script once in Supabase SQL Editor on a new project.
-- This script does not delete existing tables or user data.
--
-- =============================================================================


-- =============================================================================
-- 1. PROFILES TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.profiles (

    id UUID PRIMARY KEY
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    full_name TEXT,

    email TEXT,

    avatar_url TEXT,

    preferred_city TEXT DEFAULT 'Delhi',

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

);


-- =============================================================================
-- 2. SAVED FORECASTS TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.saved_forecasts (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    city TEXT NOT NULL,

    forecast_date DATE NOT NULL,

    predicted_aqi NUMERIC NOT NULL
        CHECK (predicted_aqi >= 0),

    aqi_category TEXT NOT NULL,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now()

);


-- =============================================================================
-- 3. USER PREFERENCES TABLE
-- =============================================================================

CREATE TABLE IF NOT EXISTS public.user_preferences (

    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),

    user_id UUID NOT NULL UNIQUE
        REFERENCES auth.users(id)
        ON DELETE CASCADE,

    preferred_city TEXT DEFAULT 'Delhi',

    notifications_enabled BOOLEAN NOT NULL DEFAULT true,

    created_at TIMESTAMPTZ NOT NULL DEFAULT now(),

    updated_at TIMESTAMPTZ NOT NULL DEFAULT now()

);


-- =============================================================================
-- 4. PERFORMANCE INDEXES
-- =============================================================================

CREATE INDEX IF NOT EXISTS idx_saved_forecasts_user_id
ON public.saved_forecasts(user_id);

CREATE INDEX IF NOT EXISTS idx_saved_forecasts_user_created
ON public.saved_forecasts(user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_saved_forecasts_city_date
ON public.saved_forecasts(city, forecast_date);

CREATE INDEX IF NOT EXISTS idx_user_preferences_user_id
ON public.user_preferences(user_id);


-- =============================================================================
-- 5. ENABLE ROW LEVEL SECURITY
-- =============================================================================

ALTER TABLE public.profiles
ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.saved_forecasts
ENABLE ROW LEVEL SECURITY;

ALTER TABLE public.user_preferences
ENABLE ROW LEVEL SECURITY;


-- =============================================================================
-- 6. PROFILES SECURITY POLICIES
-- =============================================================================

CREATE POLICY "Users can view their own profile"

ON public.profiles

FOR SELECT

TO authenticated

USING (auth.uid() = id);


CREATE POLICY "Users can insert their own profile"

ON public.profiles

FOR INSERT

TO authenticated

WITH CHECK (auth.uid() = id);


CREATE POLICY "Users can update their own profile"

ON public.profiles

FOR UPDATE

TO authenticated

USING (auth.uid() = id)

WITH CHECK (auth.uid() = id);


CREATE POLICY "Users can delete their own profile"

ON public.profiles

FOR DELETE

TO authenticated

USING (auth.uid() = id);


-- =============================================================================
-- 7. SAVED FORECASTS SECURITY POLICIES
-- =============================================================================

CREATE POLICY "Users can view their own saved forecasts"

ON public.saved_forecasts

FOR SELECT

TO authenticated

USING (auth.uid() = user_id);


CREATE POLICY "Users can insert their own saved forecasts"

ON public.saved_forecasts

FOR INSERT

TO authenticated

WITH CHECK (auth.uid() = user_id);


CREATE POLICY "Users can update their own saved forecasts"

ON public.saved_forecasts

FOR UPDATE

TO authenticated

USING (auth.uid() = user_id)

WITH CHECK (auth.uid() = user_id);


CREATE POLICY "Users can delete their own saved forecasts"

ON public.saved_forecasts

FOR DELETE

TO authenticated

USING (auth.uid() = user_id);


-- =============================================================================
-- 8. USER PREFERENCES SECURITY POLICIES
-- =============================================================================

CREATE POLICY "Users can view their own preferences"

ON public.user_preferences

FOR SELECT

TO authenticated

USING (auth.uid() = user_id);


CREATE POLICY "Users can insert their own preferences"

ON public.user_preferences

FOR INSERT

TO authenticated

WITH CHECK (auth.uid() = user_id);


CREATE POLICY "Users can update their own preferences"

ON public.user_preferences

FOR UPDATE

TO authenticated

USING (auth.uid() = user_id)

WITH CHECK (auth.uid() = user_id);


CREATE POLICY "Users can delete their own preferences"

ON public.user_preferences

FOR DELETE

TO authenticated

USING (auth.uid() = user_id);


-- =============================================================================
-- 9. AUTOMATIC UPDATED_AT FUNCTION
-- =============================================================================

CREATE OR REPLACE FUNCTION public.handle_updated_at()

RETURNS TRIGGER

LANGUAGE plpgsql

SET search_path = ''

AS $$

BEGIN

    NEW.updated_at = now();

    RETURN NEW;

END;

$$;


-- =============================================================================
-- 10. UPDATED_AT TRIGGERS
-- =============================================================================

CREATE TRIGGER trigger_profiles_updated_at

BEFORE UPDATE ON public.profiles

FOR EACH ROW

EXECUTE FUNCTION public.handle_updated_at();


CREATE TRIGGER trigger_user_preferences_updated_at

BEFORE UPDATE ON public.user_preferences

FOR EACH ROW

EXECUTE FUNCTION public.handle_updated_at();


-- =============================================================================
-- 11. AUTOMATIC USER REGISTRATION FUNCTION
-- =============================================================================

CREATE OR REPLACE FUNCTION public.handle_new_user()

RETURNS TRIGGER

LANGUAGE plpgsql

SECURITY DEFINER

SET search_path = ''

AS $$

BEGIN

    -- Automatically create user profile

    INSERT INTO public.profiles (

        id,

        full_name,

        email,

        preferred_city

    )

    VALUES (

        NEW.id,

        COALESCE(NEW.raw_user_meta_data ->> 'full_name', ''),

        NEW.email,

        'Delhi'

    )

    ON CONFLICT (id) DO UPDATE

    SET

        full_name = EXCLUDED.full_name,

        email = EXCLUDED.email;


    -- Automatically create user preferences

    INSERT INTO public.user_preferences (

        user_id,

        preferred_city,

        notifications_enabled

    )

    VALUES (

        NEW.id,

        'Delhi',

        true

    )

    ON CONFLICT (user_id) DO NOTHING;


    RETURN NEW;

END;

$$;


-- =============================================================================
-- 12. AUTOMATIC USER REGISTRATION TRIGGER
-- =============================================================================

CREATE TRIGGER on_auth_user_created

AFTER INSERT ON auth.users

FOR EACH ROW

EXECUTE FUNCTION public.handle_new_user();


-- =============================================================================
-- 13. DATABASE PERMISSIONS
-- =============================================================================

GRANT USAGE ON SCHEMA public TO authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE
ON public.profiles
TO authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE
ON public.saved_forecasts
TO authenticated;

GRANT SELECT, INSERT, UPDATE, DELETE
ON public.user_preferences
TO authenticated;


-- =============================================================================
-- AQI FORECASTER DATABASE SETUP COMPLETE
-- =============================================================================
