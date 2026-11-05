import { useState, useEffect } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Activity, Lock, ArrowRight, AlertCircle, CheckCircle2, Eye, EyeOff, Check, X } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { validatePassword, getPasswordRuleStatus } from '../utils/validation';
import { supabase } from '../lib/supabase';

export function ResetPasswordPage() {
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [hasValidSession, setHasValidSession] = useState(true);

  const { updatePassword } = useAuth();
  const navigate = useNavigate();
  const rules = getPasswordRuleStatus(password);

  // Check if there is an active session or recovery token
  useEffect(() => {
    async function checkSession() {
      const {
        data: { session },
      } = await supabase.auth.getSession();

      // If no session and no hash token in URL, recovery link might be expired or missing
      if (!session && !window.location.hash.includes('access_token')) {
        setHasValidSession(false);
      }
    }
    checkSession();
  }, []);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Validate password constraints
    const passErr = validatePassword(password);
    if (passErr) {
      setError(passErr);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    setLoading(true);

    try {
      await updatePassword(password);
      setSuccess(true);
    } catch (err) {
      setError(
        err.message || 'Unable to update password. Your reset link may have expired.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex flex-col justify-center py-12 sm:px-6 lg:px-8 bg-[#F7F8F4]">
      <div className="sm:mx-auto sm:w-full sm:max-w-md text-center">
        <Link to="/" className="inline-flex items-center gap-2.5">
          <div className="w-9 h-9 rounded-xl bg-[#173D2D] text-[#B7E46A] flex items-center justify-center font-bold">
            <Activity className="w-5 h-5 text-[#B7E46A]" />
          </div>
          <span className="font-heading font-bold text-xl text-[#17231C]">
            AQI Forecaster
          </span>
        </Link>
        <h2 className="mt-4 text-xl font-bold font-heading text-[#17231C]">
          Set New Password
        </h2>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white py-7 px-6 sm:px-8 shadow-sm rounded-2xl border border-[#E3E8E1] space-y-4">
          {!hasValidSession ? (
            <div className="text-center space-y-3 py-2">
              <div className="p-3 rounded-lg bg-amber-50 border border-amber-200 text-xs text-amber-800 text-left">
                <strong>Session Notice:</strong> No active recovery session was detected. If you followed a reset email link, it may have expired or already been used.
              </div>
              <Link to="/forgot-password">
                <Button variant="primary" size="md" className="w-full mt-2">
                  Request New Reset Link
                </Button>
              </Link>
            </div>
          ) : success ? (
            <div className="text-center space-y-3 py-2">
              <div className="w-10 h-10 bg-[#ECFDF5] text-[#10B981] rounded-xl flex items-center justify-center mx-auto border border-[#A7F3D0]">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-[#17231C]">
                Password Updated
              </h3>
              <p className="text-xs text-[#69766E]">
                Your account password has been successfully updated.
              </p>
              <div className="pt-2">
                <Button
                  variant="primary"
                  size="md"
                  className="w-full"
                  onClick={() => navigate('/dashboard')}
                >
                  Proceed to Dashboard
                </Button>
              </div>
            </div>
          ) : (
            <>
              {error && (
                <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
                  <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
                  <span>{error}</span>
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-3.5">
                {/* New Password */}
                <div className="space-y-1">
                  <label className="block text-xs font-medium text-[#69766E]">
                    New Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#69766E]" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={password}
                      onChange={(e) => setPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full pl-9 pr-9 py-2 text-xs sm:text-sm rounded-lg border border-[#E3E8E1] bg-white text-[#17231C] focus:outline-none focus:ring-1 focus:ring-[#173D2D]"
                    />
                    <button
                      type="button"
                      onClick={() => setShowPassword(!showPassword)}
                      className="absolute right-3 top-1/2 -translate-y-1/2 text-[#69766E] hover:text-[#17231C]"
                    >
                      {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                    </button>
                  </div>
                </div>

                {/* Confirm New Password */}
                <div className="space-y-1">
                  <label className="block text-xs font-medium text-[#69766E]">
                    Confirm New Password
                  </label>
                  <div className="relative">
                    <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#69766E]" />
                    <input
                      type={showPassword ? 'text' : 'password'}
                      required
                      value={confirmPassword}
                      onChange={(e) => setConfirmPassword(e.target.value)}
                      placeholder="••••••••"
                      className="w-full pl-9 pr-3 py-2 text-xs sm:text-sm rounded-lg border border-[#E3E8E1] bg-white text-[#17231C] focus:outline-none focus:ring-1 focus:ring-[#173D2D]"
                    />
                  </div>
                </div>

                {/* Password Rules Checklist */}
                <div className="p-3 rounded-lg bg-[#F7F8F4] border border-[#E3E8E1] space-y-1.5 text-[11px]">
                  <span className="font-semibold text-[#17231C] block mb-1">
                    Password Requirements:
                  </span>
                  <div className="grid grid-cols-2 gap-1.5 text-[#69766E]">
                    <span className={`flex items-center gap-1 ${rules.minLength ? 'text-emerald-700 font-medium' : ''}`}>
                      {rules.minLength ? <Check className="w-3 h-3 text-emerald-600" /> : <X className="w-3 h-3 text-[#A8BFA9]" />}
                      6+ characters
                    </span>
                    <span className={`flex items-center gap-1 ${rules.hasUpper ? 'text-emerald-700 font-medium' : ''}`}>
                      {rules.hasUpper ? <Check className="w-3 h-3 text-emerald-600" /> : <X className="w-3 h-3 text-[#A8BFA9]" />}
                      1 uppercase letter
                    </span>
                    <span className={`flex items-center gap-1 ${rules.hasLower ? 'text-emerald-700 font-medium' : ''}`}>
                      {rules.hasLower ? <Check className="w-3 h-3 text-emerald-600" /> : <X className="w-3 h-3 text-[#A8BFA9]" />}
                      1 lowercase letter
                    </span>
                    <span className={`flex items-center gap-1 ${rules.hasNumber ? 'text-emerald-700 font-medium' : ''}`}>
                      {rules.hasNumber ? <Check className="w-3 h-3 text-emerald-600" /> : <X className="w-3 h-3 text-[#A8BFA9]" />}
                      1 number
                    </span>
                    <span className={`flex items-center gap-1 col-span-2 ${rules.hasSymbol ? 'text-emerald-700 font-medium' : ''}`}>
                      {rules.hasSymbol ? <Check className="w-3 h-3 text-emerald-600" /> : <X className="w-3 h-3 text-[#A8BFA9]" />}
                      1 special character (!@#$%^&*...)
                    </span>
                  </div>
                </div>

                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  className="w-full mt-2"
                  isLoading={loading}
                  icon={ArrowRight}
                  iconPosition="right"
                >
                  Update Password
                </Button>
              </form>
            </>
          )}

          <div className="text-center text-xs text-[#69766E] pt-2 border-t border-[#E3E8E1]">
            <Link to="/signin" className="font-semibold text-[#173D2D] hover:underline">
              Back to Sign In
            </Link>
          </div>
        </div>
      </div>
    </div>
  );
}

