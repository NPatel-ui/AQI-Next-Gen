import { useState } from 'react';
import { Link } from 'react-router-dom';
import { Activity, Mail, ArrowRight, CheckCircle2, AlertCircle } from 'lucide-react';
import { useAuth } from '../context/AuthContext';
import { Button } from '../components/ui/Button';
import { validateEmail } from '../utils/validation';

export function ForgotPasswordPage() {
  const [email, setEmail] = useState('');
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const { resetPassword } = useAuth();

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError('');

    const emailErr = validateEmail(email);
    if (emailErr) {
      setError(emailErr);
      return;
    }

    setLoading(true);

    try {
      await resetPassword(email);
      setSuccess(true);
    } catch (err) {
      setError(err.message || 'Unable to process reset request.');
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
          Reset Password
        </h2>
      </div>

      <div className="mt-6 sm:mx-auto sm:w-full sm:max-w-md px-4 sm:px-0">
        <div className="bg-white py-7 px-6 sm:px-8 shadow-sm rounded-2xl border border-[#E3E8E1] space-y-4">
          {success ? (
            <div className="text-center space-y-3 py-2">
              <div className="w-10 h-10 bg-[#ECFDF5] text-[#10B981] rounded-xl flex items-center justify-center mx-auto border border-[#A7F3D0]">
                <CheckCircle2 className="w-5 h-5" />
              </div>
              <h3 className="text-base font-bold text-[#17231C]">
                Check your email
              </h3>
              <p className="text-xs text-[#69766E]">
                We sent a password reset link to <strong className="text-[#17231C]">{email}</strong>.
              </p>
              <div className="pt-2">
                <Link to="/signin">
                  <Button variant="primary" size="md" className="w-full">
                    Back to Sign In
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

              <form onSubmit={handleSubmit} className="space-y-3">
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
                  Send Reset Link
                </Button>
              </form>

              <div className="text-center text-xs text-[#69766E] pt-2 border-t border-[#E3E8E1]">
                Remember your password?{' '}
                <Link to="/signin" className="font-semibold text-[#173D2D] hover:underline">
                  Sign In
                </Link>
              </div>
            </>
          )}
        </div>
      </div>
    </div>
  );
}
