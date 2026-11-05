import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Activity, Lock, Mail, User, ArrowRight, AlertCircle, Check, X, Eye, EyeOff, CheckCircle2 } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { validateEmail, validatePassword, validateFullName, getPasswordRuleStatus } from '../utils/validation';

export function SignUpPage() {
  const [name, setName] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [agreeTerms, setAgreeTerms] = useState(true);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);
  const [confirmationSent, setConfirmationSent] = useState(false);

  const { signUp } = useAuth();
  const navigate = useNavigate();

  const rules = getPasswordRuleStatus(password);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    // Constraint 3: In the Full Name only Alphabets are allowed and First alphabet will be Capital
    const nameErr = validateFullName(name);
    if (nameErr) {
      setError(nameErr);
      return;
    }

    // Constraint 1: email must contain @ symbol
    const emailErr = validateEmail(email);
    if (emailErr) {
      setError(emailErr);
      return;
    }

    // Constraint 2: Password must be of 6 characters with at least 1 uppercase, 1 lowercase, 1 symbol and 1 number
    const passwordErr = validatePassword(password);
    if (passwordErr) {
      setError(passwordErr);
      return;
    }

    if (password !== confirmPassword) {
      setError('Passwords do not match.');
      return;
    }

    if (!agreeTerms) {
      setError('Please accept the terms of use.');
      return;
    }

    setLoading(true);
    try {
      const result = await signUp(name, email, password);
      if (result?.session) {
        navigate('/dashboard', { replace: true });
      } else {
        setConfirmationSent(true);
      }
    } catch (err) {
      setError(err.message || 'Registration failed.');
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
          Create an account
        </h2>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white py-7 px-6 sm:px-8 shadow-sm rounded-2xl border border-[#E3E8E1] space-y-4">
          {confirmationSent ? (
            <div className="text-center space-y-3 py-2">
              <div className="w-10 h-10 bg-[#ECFDF5] text-[#10B981] rounded-xl flex items-center justify-center mx-auto border border-[#A7F3D0]">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-[#17231C]">
                Verify your email
              </h3>
              <p className="text-xs text-[#69766E] leading-relaxed">
                We sent a confirmation link to <strong className="text-[#17231C]">{email}</strong>. Please check your inbox and click the verification link to complete registration.
              </p>
              <div className="pt-2">
                <Link to="/signin">
                  <Button variant="primary" size="md" className="w-full">
                    Proceed to Sign In
                  </Button>
                </Link>
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
            {/* Full Name Field */}
            <div className="space-y-1">
              <label className="block text-xs font-medium text-[#69766E]">
                Full Name
              </label>
              <div className="relative">
                <User className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#69766E]" />
                <input
                  type="text"
                  required
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                  placeholder="Aarav Sharma"
                  className="w-full pl-9 pr-3 py-2 text-xs sm:text-sm rounded-lg border border-[#E3E8E1] bg-white text-[#17231C] focus:outline-none focus:ring-1 focus:ring-[#173D2D]"
                />
              </div>
              <p className="text-[11px] text-[#69766E]">
                Only alphabets allowed; first alphabet must be capital (e.g. Aarav Sharma)
              </p>
            </div>

            {/* Email Field */}
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

            {/* Password Field */}
            <div className="space-y-1">
              <label className="block text-xs font-medium text-[#69766E]">
                Password
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

              {/* Password Requirements Checklist */}
              <div className="p-2.5 rounded-lg bg-[#F7F8F4] border border-[#E3E8E1] space-y-1 mt-1 text-[11px]">
                <span className="font-semibold text-[#17231C] block text-[11px]">
                  Password requirements:
                </span>
                <div className="grid grid-cols-2 gap-x-2 gap-y-0.5">
                  <div className={`flex items-center gap-1 ${rules.length ? 'text-emerald-700 font-medium' : 'text-[#69766E]'}`}>
                    {rules.length ? <Check className="w-3 h-3 text-emerald-600" /> : <span className="w-1.5 h-1.5 rounded-full bg-neutral-300 ml-1 mr-0.5" />}
                    <span>6+ characters</span>
                  </div>
                  <div className={`flex items-center gap-1 ${rules.uppercase ? 'text-emerald-700 font-medium' : 'text-[#69766E]'}`}>
                    {rules.uppercase ? <Check className="w-3 h-3 text-emerald-600" /> : <span className="w-1.5 h-1.5 rounded-full bg-neutral-300 ml-1 mr-0.5" />}
                    <span>1 uppercase (A-Z)</span>
                  </div>
                  <div className={`flex items-center gap-1 ${rules.lowercase ? 'text-emerald-700 font-medium' : 'text-[#69766E]'}`}>
                    {rules.lowercase ? <Check className="w-3 h-3 text-emerald-600" /> : <span className="w-1.5 h-1.5 rounded-full bg-neutral-300 ml-1 mr-0.5" />}
                    <span>1 lowercase (a-z)</span>
                  </div>
                  <div className={`flex items-center gap-1 ${rules.number ? 'text-emerald-700 font-medium' : 'text-[#69766E]'}`}>
                    {rules.number ? <Check className="w-3 h-3 text-emerald-600" /> : <span className="w-1.5 h-1.5 rounded-full bg-neutral-300 ml-1 mr-0.5" />}
                    <span>1 number (0-9)</span>
                  </div>
                  <div className={`col-span-2 flex items-center gap-1 ${rules.symbol ? 'text-emerald-700 font-medium' : 'text-[#69766E]'}`}>
                    {rules.symbol ? <Check className="w-3 h-3 text-emerald-600" /> : <span className="w-1.5 h-1.5 rounded-full bg-neutral-300 ml-1 mr-0.5" />}
                    <span>1 special symbol (!@#$%^&*...)</span>
                  </div>
                </div>
              </div>
            </div>

            {/* Confirm Password Field */}
            <div className="space-y-1">
              <label className="block text-xs font-medium text-[#69766E]">
                Confirm Password
              </label>
              <div className="relative">
                <Lock className="w-4 h-4 absolute left-3 top-1/2 -translate-y-1/2 text-[#69766E]" />
                <input
                  type="password"
                  required
                  value={confirmPassword}
                  onChange={(e) => setConfirmPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full pl-9 pr-3 py-2 text-xs sm:text-sm rounded-lg border border-[#E3E8E1] bg-white text-[#17231C] focus:outline-none focus:ring-1 focus:ring-[#173D2D]"
                />
              </div>
            </div>

            {/* Terms Checkbox */}
            <div className="flex items-center pt-1">
              <input
                id="terms"
                type="checkbox"
                checked={agreeTerms}
                onChange={(e) => setAgreeTerms(e.target.checked)}
                className="w-3.5 h-3.5 rounded text-[#173D2D] focus:ring-[#173D2D] border-[#E3E8E1]"
              />
              <label htmlFor="terms" className="ml-2 block text-xs text-[#69766E]">
                I agree to the terms of use
              </label>
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
              Create Account
            </Button>
          </form>

          <div className="text-center text-xs text-[#69766E] pt-2 border-t border-[#E3E8E1]">
            Already have an account?{' '}
            <Link to="/signin" className="font-semibold text-[#173D2D] hover:underline">
              Sign In
            </Link>
          </div>
            </>
          )}
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
