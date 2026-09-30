import React, { useState, useMemo } from 'react';
import {
  Mail,
  Lock,
  Eye,
  EyeOff,
  ArrowRight,
  Loader2,
  AlertCircle,
  ShieldCheck,
  Calendar,
  FileText,
  X,
  HelpCircle,
} from 'lucide-react';
import Button from '../../components/ui/Button';
import { useAuth } from '../../context/AuthContext';

export default function LoginPage({ onNavigateToSignup, onSuccess }) {
  const { login } = useAuth();
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [emailTouched, setEmailTouched] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [forgotOpen, setForgotOpen] = useState(false);

  // Email format validation helper
  const isEmailValid = useMemo(() => {
    if (!email) return true;
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email.trim());
  }, [email]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');

    if (!email.trim() || !password.trim()) {
      setErrorMessage('Please enter both your work email and password.');
      return;
    }

    if (!isEmailValid) {
      setErrorMessage('Please enter a valid email address.');
      setEmailTouched(true);
      return;
    }

    setIsLoading(true);
    try {
      const res = await login(email.trim(), password);
      if (onSuccess) {
        onSuccess(res);
      }
    } catch (err) {
      const rawMsg = err.message || '';
      if (rawMsg.toLowerCase().includes('invalid') || rawMsg.toLowerCase().includes('credential') || err.status === 401) {
        setErrorMessage('Invalid email or password. Please verify your credentials and try again.');
      } else if (err.isNetworkError) {
        setErrorMessage('Authentication service is unavailable. Please check your connection.');
      } else if (err.status >= 500) {
        setErrorMessage('An unexpected server error occurred. Please try again.');
      } else {
        setErrorMessage(rawMsg || 'Authentication failed. Please verify your credentials.');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] flex items-center justify-center font-sans antialiased text-slate-100 selection:bg-blue-600 selection:text-white px-4 py-8 sm:py-12">
      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-12 rounded-3xl bg-[#0F1623] border border-[#1E293B] shadow-2xl overflow-hidden">
        {/* LEFT COLUMN: Enterprise Brand & Assurance */}
        <div className="lg:col-span-5 bg-[#0B0F17] p-6 sm:p-10 flex flex-col justify-between border-b lg:border-b-0 lg:border-r border-[#1E293B]">
          <div>
            {/* Brand Mark */}
            <div className="flex items-center gap-3 mb-8">
              <div className="w-11 h-11 rounded-xl overflow-hidden bg-black border border-amber-500/30 flex items-center justify-center shadow-lg shadow-amber-500/10 shrink-0 p-1">
                <img src="/logo.png" alt="POWER HOUSE" className="w-full h-full object-contain" />
              </div>
              <div>
                <span className="text-sm font-bold text-white tracking-widest uppercase block leading-none">
                  POWER HOUSE
                </span>
                <span className="text-[11px] text-slate-400 font-medium tracking-normal mt-1 block">
                  Compliance. Simplified.
                </span>
              </div>
            </div>

            {/* Headline */}
            <div className="space-y-2 mb-8">
              <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight leading-tight">
                Welcome back.
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                Sign in to manage compliance deadlines, statutory approvals, and filing tasks across your business.
              </p>
            </div>

            {/* 3 Concise Enterprise Assurance Cards */}
            <div className="space-y-3">
              <div className="flex items-start gap-3 p-3 rounded-xl bg-[#111827] border border-[#1E293B]/80">
                <div className="w-7 h-7 rounded-lg bg-blue-950/80 border border-blue-800/80 text-blue-400 flex items-center justify-center shrink-0 mt-0.5">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-white">Multi-tenant data isolation</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">
                    Dedicated statutory data boundaries protected by enterprise tenant isolation.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-xl bg-[#111827] border border-[#1E293B]/80">
                <div className="w-7 h-7 rounded-lg bg-amber-950/80 border border-amber-800/80 text-amber-400 flex items-center justify-center shrink-0 mt-0.5">
                  <Calendar className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-white">Continuous deadline tracking</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">
                    Automated calendar alerts for central, state, and labour compliance filings.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-xl bg-[#111827] border border-[#1E293B]/80">
                <div className="w-7 h-7 rounded-lg bg-emerald-950/80 border border-emerald-800/80 text-emerald-400 flex items-center justify-center shrink-0 mt-0.5">
                  <FileText className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-white">Unified compliance workspace</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">
                    Single source of truth for registrations, approvals, and verified dossiers.
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Security Assurance Badge */}
          <div className="pt-8 mt-6 border-t border-[#1E293B] flex items-center gap-2.5 text-slate-400 text-[11px]">
            <ShieldCheck className="w-4 h-4 text-emerald-400 shrink-0" />
            <span>Secure authentication • Multi-tenant data isolation</span>
          </div>
        </div>

        {/* RIGHT COLUMN: Sign In Form Card */}
        <div className="lg:col-span-7 bg-[#111827] p-6 sm:p-10 flex flex-col justify-center">
          <div className="w-full max-w-md mx-auto">
            <div className="space-y-1 mb-6">
              <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                Sign in to POWER HOUSE
              </h1>
              <p className="text-xs text-slate-400">
                Enter your work credentials to access your compliance workspace.
              </p>
            </div>

            {/* Error Message */}
            {errorMessage && (
              <div className="mb-4 p-3 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-start gap-2.5 animate-in fade-in duration-150">
                <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                <span className="leading-snug">{errorMessage}</span>
              </div>
            )}

            <form onSubmit={handleSubmit} className="space-y-4" noValidate>
              {/* Email Field */}
              <div className="space-y-1">
                <label htmlFor="login-email" className="block text-xs font-semibold text-slate-300">
                  Work Email
                </label>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Mail className="w-3.5 h-3.5" />
                  </div>
                  <input
                    id="login-email"
                    type="email"
                    required
                    autoComplete="email"
                    placeholder="name@company.in"
                    value={email}
                    onBlur={() => setEmailTouched(true)}
                    onChange={(e) => {
                      setEmail(e.target.value);
                      if (errorMessage) setErrorMessage('');
                    }}
                    className={`w-full pl-9 pr-3.5 py-2.5 text-xs rounded-xl bg-[#141C2B] border text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 transition-colors ${
                      emailTouched && !isEmailValid && email
                        ? 'border-rose-500 focus:border-rose-500 focus:ring-rose-500'
                        : 'border-[#1E293B] focus:border-blue-500 focus:ring-blue-500'
                    }`}
                  />
                </div>
                {emailTouched && !isEmailValid && email && (
                  <p className="text-[11px] text-rose-400 pl-0.5">Enter a valid email address.</p>
                )}
              </div>

              {/* Password Field */}
              <div className="space-y-1">
                <div className="flex items-center justify-between">
                  <label htmlFor="login-password" className="block text-xs font-semibold text-slate-300">
                    Password
                  </label>
                  <button
                    type="button"
                    onClick={() => setForgotOpen(true)}
                    className="text-[11px] font-medium text-blue-400 hover:text-blue-300 transition-colors cursor-pointer"
                  >
                    Forgot Password?
                  </button>
                </div>
                <div className="relative">
                  <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                    <Lock className="w-3.5 h-3.5" />
                  </div>
                  <input
                    id="login-password"
                    type={showPassword ? 'text' : 'password'}
                    required
                    autoComplete="current-password"
                    placeholder="••••••••••••"
                    value={password}
                    onChange={(e) => {
                      setPassword(e.target.value);
                      if (errorMessage) setErrorMessage('');
                    }}
                    className="w-full pl-9 pr-10 py-2.5 text-xs rounded-xl bg-[#141C2B] border border-[#1E293B] text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none transition-colors"
                  />
                  <button
                    type="button"
                    onClick={() => setShowPassword(!showPassword)}
                    className="absolute inset-y-0 right-0 pr-3.5 flex items-center text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                    aria-label={showPassword ? 'Hide password' : 'Show password'}
                  >
                    {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                  </button>
                </div>
              </div>

              {/* Submit Button */}
              <Button
                type="submit"
                variant="primary"
                size="md"
                disabled={isLoading}
                className="w-full mt-2 font-semibold text-xs justify-center py-2.5 shadow-sm shadow-blue-500/20"
              >
                {isLoading ? (
                  <>
                    <Loader2 className="w-3.5 h-3.5 animate-spin mr-2" />
                    <span>Signing in…</span>
                  </>
                ) : (
                  <>
                    <span>Sign In</span>
                    <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                  </>
                )}
              </Button>
            </form>

            {/* Navigation to Signup */}
            <div className="mt-6 pt-5 border-t border-slate-800/80 text-center">
              <p className="text-xs text-slate-400">
                Don&apos;t have an account?{' '}
                <button
                  type="button"
                  onClick={onNavigateToSignup}
                  className="font-bold text-blue-400 hover:text-blue-300 transition-colors cursor-pointer ml-1"
                >
                  Create Account
                </button>
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Enterprise Forgot Password Modal */}
      {forgotOpen && (
        <div
          className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-xs animate-in fade-in duration-150"
          onClick={() => setForgotOpen(false)}
          role="dialog"
          aria-modal="true"
        >
          <div
            className="bg-[#111827] rounded-2xl max-w-md w-full p-6 border border-[#1E293B] shadow-2xl space-y-4 animate-in zoom-in-95 duration-150"
            onClick={(e) => e.stopPropagation()}
          >
            <div className="flex items-center justify-between pb-3 border-b border-slate-800">
              <div className="flex items-center gap-2.5">
                <div className="w-8 h-8 rounded-lg bg-blue-950/80 border border-blue-800/80 text-blue-400 flex items-center justify-center shrink-0">
                  <HelpCircle className="w-4 h-4" />
                </div>
                <div>
                  <h3 className="font-bold text-white text-sm">Enterprise Account Recovery</h3>
                  <span className="text-[11px] text-slate-400">Identity verification protocol</span>
                </div>
              </div>
              <button
                type="button"
                onClick={() => setForgotOpen(false)}
                className="p-1 rounded-lg text-slate-400 hover:text-white hover:bg-slate-800 transition-colors cursor-pointer"
                aria-label="Close dialog"
              >
                <X className="w-4 h-4" />
              </button>
            </div>

            <div className="space-y-3 text-xs text-slate-300 leading-relaxed">
              <p>
                To maintain strict statutory audit compliance and multi-tenant data protection, automated password resets require verified domain administrator approval.
              </p>
              <div className="p-3.5 bg-[#141C2B] rounded-xl border border-[#1E293B] space-y-1.5 text-slate-300">
                <div className="text-slate-400 font-medium">Compliance Helpdesk:</div>
                <div>Hotline: <strong className="text-white font-mono">1800-419-7000</strong></div>
                <div>Email: <strong className="text-blue-400 font-mono">support@powerhouse.in</strong></div>
                <div className="text-[11px] text-slate-400 pt-1 border-t border-slate-800">
                  Please provide your registered Business PAN and primary contact number for verification.
                </div>
              </div>
            </div>

            <div className="pt-2 flex justify-end">
              <Button
                variant="secondary"
                size="sm"
                onClick={() => setForgotOpen(false)}
                className="text-xs font-semibold"
              >
                Understood
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
