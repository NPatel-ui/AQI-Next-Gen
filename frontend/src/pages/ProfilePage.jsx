import { useState, useRef, useEffect } from 'react';
import { Link } from 'react-router-dom';
import {
  UserRound,
  Mail,
  Calendar,
  Shield,
  MapPin,
  Camera,
  Check,
  AlertCircle,
  Sliders,
  CheckCircle2,
  Bookmark,
  Trash2,
  Bell,
  ArrowRight,
} from 'lucide-react';
import { PageContainer } from '../components/layout/PageContainer';
import { BentoCard } from '../components/ui/BentoCard';
import { Button } from '../components/ui/Button';
import { useAuth } from '../context/AuthContext';
import { ELIGIBLE_CITIES } from '../utils/datasetInfo';
import { validateFullName } from '../utils/validation';
import { getUserPreferences, upsertUserPreferences } from '../services/preferencesService';
import { getSavedForecasts, deleteSavedForecast } from '../services/forecastService';
import { getAqiCategory, formatAqi, formatDate } from '../utils/aqiUtils';

export function ProfilePage() {
  const { user, updateUser } = useAuth();
  const fileInputRef = useRef(null);

  // Form state
  const [isEditing, setIsEditing] = useState(false);
  const [fullName, setFullName] = useState(user?.name || '');
  const [email, setEmail] = useState(user?.email || '');
  const [preferredCity, setPreferredCity] = useState(user?.preferredCity || 'Delhi');
  const [displayUnit, setDisplayUnit] = useState('CPCB Standard Index');
  const [notificationsEnabled, setNotificationsEnabled] = useState(true);
  const [avatarPreview, setAvatarPreview] = useState(user?.avatarUrl || null);

  // Saved Forecasts state
  const [savedForecasts, setSavedForecasts] = useState([]);
  const [loadingForecasts, setLoadingForecasts] = useState(true);

  // Status feedback
  const [successMessage, setSuccessMessage] = useState('');
  const [errorMessage, setErrorMessage] = useState('');
  const [isSaving, setIsSaving] = useState(false);

  // Sync state when user loads or updates
  useEffect(() => {
    if (user) {
      setFullName(user.name || '');
      setEmail(user.email || '');
      setPreferredCity(user.preferredCity || 'Delhi');
      setAvatarPreview(user.avatarUrl || null);
    }
  }, [user]);

  // Load preferences and saved forecasts from Supabase
  useEffect(() => {
    let mounted = true;

    async function loadData() {
      if (!user?.id) return;

      try {
        const [prefs, forecasts] = await Promise.all([
          getUserPreferences(user.id),
          getSavedForecasts(),
        ]);

        if (mounted) {
          if (prefs) {
            if (prefs.preferred_city) setPreferredCity(prefs.preferred_city);
            if (typeof prefs.notifications_enabled === 'boolean') {
              setNotificationsEnabled(prefs.notifications_enabled);
            }
          }
          setSavedForecasts(forecasts || []);
        }
      } catch (err) {
        console.warn('Error loading profile data:', err);
      } finally {
        if (mounted) setLoadingForecasts(false);
      }
    }

    loadData();
    return () => {
      mounted = false;
    };
  }, [user?.id]);

  // Handle avatar upload with size and type validation
  const handleAvatarChange = (e) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const validTypes = ['image/jpeg', 'image/png', 'image/webp', 'image/gif'];
    if (!validTypes.includes(file.type)) {
      setErrorMessage('Please upload a valid image file (JPEG, PNG, or WebP).');
      return;
    }

    if (file.size > 2 * 1024 * 1024) {
      setErrorMessage('Image size must be smaller than 2MB.');
      return;
    }

    setErrorMessage('');
    const reader = new FileReader();
    reader.onload = async () => {
      const result = reader.result;
      setAvatarPreview(result);
      try {
        await updateUser({ avatarUrl: result });
        setSuccessMessage('Profile photo updated.');
        setTimeout(() => setSuccessMessage(''), 3000);
      } catch (err) {
        setErrorMessage(err.message || 'Unable to update profile image.');
      }
    };
    reader.readAsDataURL(file);
  };

  const handleSave = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setSuccessMessage('');

    const nameErr = validateFullName(fullName);
    if (nameErr) {
      setErrorMessage(nameErr);
      return;
    }

    setIsSaving(true);

    try {
      // Update profile in Supabase
      await updateUser({
        name: fullName.trim(),
        preferredCity,
        avatarUrl: avatarPreview,
      });

      // Update preferences in Supabase
      if (user?.id) {
        await upsertUserPreferences(user.id, {
          preferred_city: preferredCity,
          notifications_enabled: notificationsEnabled,
        });
      }

      setIsEditing(false);
      setSuccessMessage('Profile and preferences saved successfully.');
      setTimeout(() => setSuccessMessage(''), 3500);
    } catch (err) {
      setErrorMessage(err.message || 'Failed to update profile.');
    } finally {
      setIsSaving(false);
    }
  };

  const handleCancel = () => {
    setFullName(user?.name || '');
    setEmail(user?.email || '');
    setPreferredCity(user?.preferredCity || 'Delhi');
    setAvatarPreview(user?.avatarUrl || null);
    setIsEditing(false);
    setErrorMessage('');
  };

  const handleDeleteSaved = async (id) => {
    try {
      await deleteSavedForecast(id);
      setSavedForecasts((prev) => prev.filter((f) => f.id !== id));
      setSuccessMessage('Saved forecast removed.');
      setTimeout(() => setSuccessMessage(''), 3000);
    } catch (err) {
      setErrorMessage(err.message || 'Unable to delete forecast.');
    }
  };

  const initials = fullName
    ? fullName
        .split(' ')
        .map((n) => n[0])
        .join('')
        .toUpperCase()
        .slice(0, 2)
    : 'U';

  return (
    <PageContainer>
      {/* Header */}
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-3 pb-1">
        <div>
          <h1 className="text-xl font-bold font-heading text-[#17231C]">
            My Profile
          </h1>
          <p className="text-xs text-[#69766E] mt-0.5">
            Manage your personal information and account preferences.
          </p>
        </div>

        {!isEditing && (
          <Button
            onClick={() => setIsEditing(true)}
            variant="secondary"
            size="sm"
          >
            Edit Profile
          </Button>
        )}
      </div>

      {/* Success Notification */}
      {successMessage && (
        <div className="p-3 rounded-xl bg-emerald-50 border border-emerald-200 text-xs text-emerald-800 flex items-center gap-2">
          <CheckCircle2 className="w-4 h-4 text-emerald-600 shrink-0" />
          <span>{successMessage}</span>
        </div>
      )}

      {/* Error Notification */}
      {errorMessage && (
        <div className="p-3 rounded-xl bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
          <AlertCircle className="w-4 h-4 text-rose-600 shrink-0" />
          <span>{errorMessage}</span>
        </div>
      )}

      {/* Profile Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-5">
        {/* Left Column: Avatar & Overview (Col-span 4) */}
        <div className="lg:col-span-4 space-y-4">
          <div className="p-5 rounded-2xl bg-white border border-[#E3E8E1] shadow-xs text-center space-y-4">
            {/* Avatar with Upload Badge */}
            <div className="relative inline-block mx-auto">
              {avatarPreview ? (
                <img
                  src={avatarPreview}
                  alt={fullName}
                  className="w-24 h-24 rounded-full object-cover border-2 border-[#173D2D]/20 shadow-xs mx-auto"
                />
              ) : (
                <div className="w-24 h-24 rounded-full bg-[#173D2D] text-[#B7E46A] flex items-center justify-center font-bold text-2xl shadow-xs mx-auto">
                  {initials}
                </div>
              )}

              <input
                ref={fileInputRef}
                type="file"
                accept="image/jpeg,image/png,image/webp,image/gif"
                onChange={handleAvatarChange}
                className="hidden"
              />

              <button
                type="button"
                onClick={() => fileInputRef.current?.click()}
                className="absolute bottom-0 right-0 p-2 rounded-full bg-[#173D2D] text-white hover:bg-[#102C22] transition-colors border-2 border-white shadow-xs"
                title="Change avatar photo"
                aria-label="Upload profile photo"
              >
                <Camera className="w-3.5 h-3.5 text-[#B7E46A]" />
              </button>
            </div>

            <div>
              <h2 className="text-base font-bold font-heading text-[#17231C]">
                {fullName || 'Environmental Analyst'}
              </h2>
              <p className="text-xs text-[#69766E] break-all mt-0.5">{email}</p>
            </div>

            {/* Quick Badges */}
            <div className="flex flex-wrap items-center justify-center gap-1.5 pt-1">
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-[#DDEBE0] text-[#173D2D]">
                {user?.role || 'Air Quality Analyst'}
              </span>
              <span className="px-2.5 py-0.5 rounded-full text-[11px] font-medium bg-[#F7F8F4] text-[#69766E] border border-[#E3E8E1] flex items-center gap-1">
                <MapPin className="w-3 h-3 text-[#173D2D]" />
                {preferredCity}
              </span>
            </div>

            {/* Account Details */}
            <div className="pt-3 border-t border-[#E3E8E1] space-y-2 text-xs text-[#69766E]">
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <Calendar className="w-3.5 h-3.5" />
                  <span>Member Since</span>
                </span>
                <span className="font-medium text-[#17231C]">
                  {user?.joinedDate || 'Active Member'}
                </span>
              </div>
              <div className="flex items-center justify-between">
                <span className="flex items-center gap-1.5">
                  <Shield className="w-3.5 h-3.5" />
                  <span>Auth Provider</span>
                </span>
                <span className="font-medium text-[#17231C]">
                  Supabase Auth
                </span>
              </div>
            </div>
          </div>
        </div>

        {/* Right Column: Personal Information, Preferences & Saved Forecasts (Col-span 8) */}
        <div className="lg:col-span-8 space-y-5">
          <form onSubmit={handleSave} className="space-y-5">
            {/* Personal Information */}
            <BentoCard
              title="Personal Information"
              subtitle="Update your full name and credentials"
              icon={UserRound}
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-1">
                <div className="space-y-1">
                  <label className="block text-xs font-medium text-[#69766E]">
                    Full Name
                  </label>
                  <input
                    type="text"
                    disabled={!isEditing}
                    value={fullName}
                    onChange={(e) => setFullName(e.target.value)}
                    className="w-full px-3 py-2 text-xs sm:text-sm rounded-lg border border-[#E3E8E1] bg-white disabled:bg-[#F7F8F4] disabled:text-[#69766E] text-[#17231C] focus:outline-none focus:ring-1 focus:ring-[#173D2D]"
                  />
                  <p className="text-[11px] text-[#69766E]">
                    Alphabets and spaces only; first letter capital.
                  </p>
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-medium text-[#69766E]">
                    Email Address
                  </label>
                  <input
                    type="email"
                    disabled
                    value={email}
                    className="w-full px-3 py-2 text-xs sm:text-sm rounded-lg border border-[#E3E8E1] bg-[#F7F8F4] text-[#69766E] cursor-not-allowed"
                  />
                  <p className="text-[11px] text-[#69766E]">
                    Managed by Supabase Authentication.
                  </p>
                </div>
              </div>
            </BentoCard>

            {/* Application Preferences */}
            <BentoCard
              title="Preferences"
              subtitle="Default forecasting and notification settings"
              icon={Sliders}
            >
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3.5 pt-1">
                <div className="space-y-1">
                  <label className="block text-xs font-medium text-[#69766E]">
                    Default Focus City
                  </label>
                  <select
                    disabled={!isEditing}
                    value={preferredCity}
                    onChange={(e) => setPreferredCity(e.target.value)}
                    className="w-full px-3 py-2 text-xs sm:text-sm rounded-lg border border-[#E3E8E1] bg-white disabled:bg-[#F7F8F4] disabled:text-[#69766E] text-[#17231C] focus:outline-none focus:ring-1 focus:ring-[#173D2D]"
                  >
                    {ELIGIBLE_CITIES.map((c) => (
                      <option key={c.name} value={c.name}>
                        {c.name} ({c.state})
                      </option>
                    ))}
                  </select>
                </div>

                <div className="space-y-1">
                  <label className="block text-xs font-medium text-[#69766E]">
                    AQI Scale Format
                  </label>
                  <select
                    disabled={!isEditing}
                    value={displayUnit}
                    onChange={(e) => setDisplayUnit(e.target.value)}
                    className="w-full px-3 py-2 text-xs sm:text-sm rounded-lg border border-[#E3E8E1] bg-white disabled:bg-[#F7F8F4] disabled:text-[#69766E] text-[#17231C] focus:outline-none focus:ring-1 focus:ring-[#173D2D]"
                  >
                    <option value="CPCB Standard Index">CPCB Standard Index (0–500)</option>
                    <option value="Detailed Sub-Indices">Detailed Pollutant Sub-Indices</option>
                  </select>
                </div>
              </div>

              {/* Notification Preference Toggle */}
              <div className="pt-3 mt-3 border-t border-[#E3E8E1] flex items-center justify-between text-xs">
                <div className="flex items-center gap-2 text-[#17231C]">
                  <Bell className="w-4 h-4 text-[#173D2D]" />
                  <span>Environmental Advisories & Alerts</span>
                </div>
                <label className="relative inline-flex items-center cursor-pointer">
                  <input
                    type="checkbox"
                    disabled={!isEditing}
                    checked={notificationsEnabled}
                    onChange={(e) => setNotificationsEnabled(e.target.checked)}
                    className="sr-only peer"
                  />
                  <div className="w-9 h-5 bg-[#E3E8E1] peer-focus:outline-none rounded-full peer peer-checked:after:translate-x-full peer-checked:after:border-white after:content-[''] after:absolute after:top-[2px] after:left-[2px] after:bg-white after:border-gray-300 after:border after:rounded-full after:h-4 after:w-4 after:transition-all peer-checked:bg-[#173D2D] disabled:opacity-50"></div>
                </label>
              </div>
            </BentoCard>

            {/* Action Buttons in Edit Mode */}
            {isEditing && (
              <div className="flex items-center justify-end gap-2.5 pt-1">
                <Button
                  type="button"
                  onClick={handleCancel}
                  variant="secondary"
                  size="sm"
                  disabled={isSaving}
                >
                  Cancel
                </Button>
                <Button
                  type="submit"
                  variant="primary"
                  size="sm"
                  isLoading={isSaving}
                  icon={Check}
                >
                  Save Changes
                </Button>
              </div>
            )}
          </form>

          {/* Saved Forecasts Section */}
          <BentoCard
            title="Saved Forecasts"
            subtitle="Air quality predictions you have stored"
            icon={Bookmark}
          >
            {loadingForecasts ? (
              <div className="py-6 text-center text-xs text-[#69766E]">
                Loading saved predictions...
              </div>
            ) : savedForecasts.length === 0 ? (
              <div className="py-6 text-center space-y-2">
                <p className="text-xs text-[#69766E]">
                  You have not saved any forecasts yet.
                </p>
                <Link
                  to="/forecast"
                  className="inline-flex items-center gap-1 text-xs font-semibold text-[#173D2D] hover:underline"
                >
                  Go to Forecasting Page <ArrowRight className="w-3 h-3" />
                </Link>
              </div>
            ) : (
              <div className="space-y-2 pt-1">
                {savedForecasts.map((item) => {
                  const cat = getAqiCategory(item.predicted_aqi);
                  return (
                    <div
                      key={item.id}
                      className="p-3 rounded-xl border border-[#E3E8E1] bg-[#F7F8F4] flex flex-col sm:flex-row sm:items-center justify-between gap-3 text-xs"
                    >
                      <div className="space-y-0.5">
                        <div className="flex items-center gap-2">
                          <span className="font-bold text-[#17231C]">
                            {item.city}
                          </span>
                          <span
                            className="px-2 py-0.5 rounded text-[10px] font-semibold"
                            style={{
                              backgroundColor: cat.bgColor,
                              color: cat.textColor,
                            }}
                          >
                            {cat.name}
                          </span>
                        </div>
                        <div className="text-[11px] text-[#69766E]">
                          Target Date: {formatDate(item.forecast_date)} · Saved on{' '}
                          {formatDate(item.created_at)}
                        </div>
                      </div>

                      <div className="flex items-center justify-between sm:justify-end gap-3">
                        <div className="text-right">
                          <span className="font-heading font-extrabold text-sm text-[#17231C]">
                            {formatAqi(item.predicted_aqi)}
                          </span>
                          <span className="text-[10px] text-[#69766E] ml-1">
                            AQI
                          </span>
                        </div>

                        <button
                          type="button"
                          onClick={() => handleDeleteSaved(item.id)}
                          className="p-1.5 rounded-lg text-[#69766E] hover:text-rose-600 hover:bg-rose-50 transition-colors"
                          title="Delete saved forecast"
                          aria-label="Delete saved forecast"
                        >
                          <Trash2 className="w-4 h-4" />
                        </button>
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </BentoCard>
        </div>
      </div>
    </PageContainer>
  );
}
