import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Activity, Lock, Mail, ArrowRight, AlertCircle, Eye, EyeOff } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { validateEmail, validatePassword } from '../utils/validation';

export function SignInPage() {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { signIn } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();

  const from = location.state?.from?.pathname || '/dashboard';

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Constraint 1: Email must contain @ symbol
    const emailErr = validateEmail(email);
    if (emailErr) {
      setError(emailErr);
      return;
    }

    // Constraint 2: Password must be of 6 characters with at least 1 uppercase, 1 lowercase, 1 number and 1 symbol
    const passwordErr = validatePassword(password);
    if (passwordErr) {
      setError(passwordErr);
      return;
    }

    setLoading(true);

    try {
      await signIn(email, password);
      navigate(from, { replace: true });
    } catch (err) {
      const msg = err.message || '';
      if (msg.toLowerCase().includes('invalid login credentials')) {
        setError('Invalid email or password. Please check your credentials.');
      } else if (msg.toLowerCase().includes('email not confirmed')) {
        setError('Please verify your email address before signing in. Check your inbox for the confirmation link.');
      } else {
        setError(msg || 'Authentication failed. Please verify credentials.');
      }
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
          Sign in to your account
        </h2>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white py-7 px-6 sm:px-8 shadow-sm rounded-2xl border border-[#E3E8E1] space-y-4">
          {error && (
            <div className="p-3 rounded-lg bg-rose-50 border border-rose-200 text-xs text-rose-700 flex items-center gap-2">
              <AlertCircle className="w-4 h-4 shrink-0 text-rose-500" />
              <span>{error}</span>
            </div>
          )}

          <form onSubmit={handleSubmit} className="space-y-3.5">
            <div className="space-y-1">
              <label className="block text-xs font-medium text-[#69766E]">
                Email Address
              </label>
              <div className="relative">
                <Mail className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#69766E]" />
                <input
                  type="email"
                  required
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  placeholder="name@example.com"
                  className="w-full pl-9 pr-3 py-2 text-xs sm:text-sm rounded-lg border border-[#E3E8E1] bg-white text-[#17231C] focus:outline-none focus:ring-1 focus:ring-[#173D2D]"
                />
              </div>
              <p className="text-[11px] text-[#69766E]">Must contain an "@" symbol</p>
            </div>

            <div className="space-y-1">
              <div className="flex items-center justify-between">
                <label className="block text-xs font-medium text-[#69766E]">
                  Password
                </label>
                <Link
                  to="/forgot-password"
                  className="text-xs text-[#173D2D] hover:underline"
                >
                  Forgot password?
                </Link>
              </div>
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
              <p className="text-[11px] text-[#69766E]">
                Min. 6 chars with 1 uppercase, 1 lowercase, 1 number & 1 symbol
              </p>
            </div>

            <div className="flex items-center">
              <input
                id="remember-me"
                type="checkbox"
                checked={rememberMe}
                onChange={(e) => setRememberMe(e.target.checked)}
                className="w-3.5 h-3.5 rounded text-[#173D2D] focus:ring-[#173D2D] border-[#E3E8E1]"
              />
              <label htmlFor="remember-me" className="ml-2 block text-xs text-[#69766E]">
                Remember this device
              </label>
            </div>

            <Button
              type="submit"
              variant="primary"
              size="md"
              className="w-full"
              isLoading={loading}
              icon={ArrowRight}
              iconPosition="right"
            >
              Sign In
            </Button>
          </form>

          <div className="text-center text-xs text-[#69766E] pt-2 border-t border-[#E3E8E1]">
            Don't have an account?{' '}
            <Link to="/signup" className="font-semibold text-[#173D2D] hover:underline">
              Sign up
            </Link>
          </div>
        </div>

        <div className="text-center mt-4">
          <Link to="/" className="text-xs text-[#69766E] hover:text-[#173D2D]">
            ← Back to Overview
          </Link>
        </div>
      </div>
    </div>
  );
}
