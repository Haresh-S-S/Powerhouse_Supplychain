import React, { useState, useMemo } from 'react';
import {
  Mail,
  Lock,
  User,
  Phone,
  Eye,
  EyeOff,
  ArrowRight,
  Loader2,
  AlertCircle,
  CheckCircle2,
  ShieldCheck,
  Calendar,
  FileText,
} from 'lucide-react';
import Button from '../../components/ui/Button';
import { useAuth } from '../../context/AuthContext';

export default function SignUpPage({ onNavigateToLogin, onSuccess }) {
  const { signup, commitUserSession } = useAuth();
  const [fullName, setFullName] = useState('');
  const [email, setEmail] = useState('');
  const [phoneNumber, setPhoneNumber] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [showConfirmPassword, setShowConfirmPassword] = useState(false);

  // Field interaction tracking for clean inline validation
  const [emailTouched, setEmailTouched] = useState(false);
  const [confirmTouched, setConfirmTouched] = useState(false);

  const [isLoading, setIsLoading] = useState(false);
  const [isSuccess, setIsSuccess] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [isDuplicateEmail, setIsDuplicateEmail] = useState(false);

  // Email format validation helper
  const isEmailValid = useMemo(() => {
    if (!email) return true; // neutral until input
    const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return emailRegex.test(email.trim());
  }, [email]);

  // Password match verification
  const passwordsMatch = useMemo(() => {
    if (!confirmPassword) return null;
    return password === confirmPassword;
  }, [password, confirmPassword]);

  const handleSubmit = async (e) => {
    e.preventDefault();
    setErrorMessage('');
    setIsDuplicateEmail(false);

    if (!fullName.trim()) {
      setErrorMessage('Please enter your full name.');
      return;
    }

    if (!email.trim() || !isEmailValid) {
      setErrorMessage('Enter a valid email address.');
      setEmailTouched(true);
      return;
    }

    if (password.length < 6) {
      setErrorMessage('Password must be at least 6 characters long.');
      return;
    }

    if (password !== confirmPassword) {
      setErrorMessage('Passwords do not match. Please re-enter.');
      setConfirmTouched(true);
      return;
    }

    setIsLoading(true);
    try {
      const res = await signup(fullName.trim(), email.trim(), password, phoneNumber.trim() || null, true);
      setIsSuccess(true);
      setIsLoading(false);
      // Brief transition state before navigating into onboarding (avoids any dashboard flash)
      setTimeout(() => {
        commitUserSession(res, true);
        if (onSuccess) {
          onSuccess(res);
        }
      }, 750);
    } catch (err) {
      const rawMsg = err.message || '';
      if (rawMsg.toLowerCase().includes('already exists') || rawMsg.toLowerCase().includes('registered') || err.status === 400) {
        setIsDuplicateEmail(true);
        setErrorMessage('This email is already registered. Sign in instead.');
      } else if (err.isNetworkError) {
        setErrorMessage('Authentication service is unavailable. Please check your connection.');
      } else if (err.status === 422) {
        setErrorMessage(rawMsg || 'Please provide all required account details in valid format.');
      } else if (err.status >= 500) {
        setErrorMessage('An unexpected server error occurred. Please try again.');
      } else {
        setErrorMessage(rawMsg || 'Failed to create account. Please try again.');
      }
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-[#0B0F17] flex items-center justify-center font-sans antialiased text-slate-100 selection:bg-blue-600 selection:text-white px-4 py-8 sm:py-12">
      <div className="w-full max-w-5xl grid grid-cols-1 lg:grid-cols-12 rounded-3xl bg-[#0F1623] border border-[#1E293B] shadow-2xl overflow-hidden">
        {/* LEFT COLUMN: Enterprise Brand & Value Props */}
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

            {/* Value Proposition Headline */}
            <div className="space-y-2 mb-8">
              <h2 className="text-2xl sm:text-3xl font-bold text-white tracking-tight leading-tight">
                Start with your business.
              </h2>
              <p className="text-xs sm:text-sm text-slate-400 leading-relaxed">
                Create your POWER HOUSE account and build a compliance workspace tailored to your business.
              </p>
            </div>

            {/* 3 Concise Value Statements */}
            <div className="space-y-3">
              <div className="flex items-start gap-3 p-3 rounded-xl bg-[#111827] border border-[#1E293B]/80">
                <div className="w-7 h-7 rounded-lg bg-blue-950/80 border border-blue-800/80 text-blue-400 flex items-center justify-center shrink-0 mt-0.5">
                  <ShieldCheck className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-white">Understand required licences</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">
                    Instant mapping of central and state statutory mandates for your industry.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-xl bg-[#111827] border border-[#1E293B]/80">
                <div className="w-7 h-7 rounded-lg bg-amber-950/80 border border-amber-800/80 text-amber-400 flex items-center justify-center shrink-0 mt-0.5">
                  <Calendar className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-white">Track compliance deadlines</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">
                    Proactive alerts on statutory filings, recurring returns, and licence renewals.
                  </p>
                </div>
              </div>

              <div className="flex items-start gap-3 p-3 rounded-xl bg-[#111827] border border-[#1E293B]/80">
                <div className="w-7 h-7 rounded-lg bg-emerald-950/80 border border-emerald-800/80 text-emerald-400 flex items-center justify-center shrink-0 mt-0.5">
                  <FileText className="w-4 h-4" />
                </div>
                <div>
                  <h4 className="text-xs font-semibold text-white">Manage documents and approvals</h4>
                  <p className="text-[11px] text-slate-400 mt-0.5 leading-snug">
                    Secure audit-ready vault for verified statutory certificates and applications.
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

        {/* RIGHT COLUMN: Sign Up Form Card */}
        <div className="lg:col-span-7 bg-[#111827] p-6 sm:p-10 flex flex-col justify-center">
          {isSuccess ? (
            /* Successful Creation Transition State */
            <div className="text-center py-10 space-y-4 animate-in fade-in zoom-in-95 duration-200">
              <div className="w-14 h-14 rounded-2xl bg-emerald-950/80 border border-emerald-800/80 text-emerald-400 flex items-center justify-center mx-auto shadow-lg shadow-emerald-500/10">
                <CheckCircle2 className="w-7 h-7" />
              </div>
              <div className="space-y-1">
                <h3 className="text-xl font-bold text-white">Account created.</h3>
                <p className="text-xs text-slate-400">Let&apos;s set up your business workspace...</p>
              </div>
              <div className="flex items-center justify-center gap-2 text-xs text-blue-400 pt-2">
                <Loader2 className="w-4 h-4 animate-spin" />
                <span>Preparing onboarding roadmap</span>
              </div>
            </div>
          ) : (
            <div className="w-full max-w-md mx-auto">
              <div className="space-y-1 mb-6">
                <h1 className="text-xl sm:text-2xl font-bold text-white tracking-tight">
                  Create your POWER HOUSE account
                </h1>
                <p className="text-xs text-slate-400">
                  Build your compliance workspace around your business.
                </p>
              </div>

              {/* Error Message Box */}
              {errorMessage && (
                <div className="mb-4 p-3 rounded-xl bg-rose-950/40 border border-rose-800/60 text-rose-300 text-xs flex items-start justify-between gap-2.5 animate-in fade-in duration-150">
                  <div className="flex items-start gap-2 min-w-0">
                    <AlertCircle className="w-4 h-4 text-rose-400 shrink-0 mt-0.5" />
                    <span className="leading-snug">{errorMessage}</span>
                  </div>
                  {isDuplicateEmail && (
                    <button
                      type="button"
                      onClick={onNavigateToLogin}
                      className="text-xs font-bold text-blue-400 hover:text-blue-300 underline shrink-0 cursor-pointer ml-1"
                    >
                      Sign In
                    </button>
                  )}
                </div>
              )}

              <form onSubmit={handleSubmit} className="space-y-3.5" noValidate>
                {/* Full Name */}
                <div className="space-y-1">
                  <label htmlFor="signup-fullname" className="block text-xs font-semibold text-slate-300">
                    Full Name
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                      <User className="w-3.5 h-3.5" />
                    </div>
                    <input
                      id="signup-fullname"
                      type="text"
                      required
                      autoComplete="name"
                      placeholder="e.g. Mohith K"
                      value={fullName}
                      onChange={(e) => setFullName(e.target.value)}
                      className="w-full pl-9 pr-3.5 py-2 text-xs rounded-xl bg-[#141C2B] border border-[#1E293B] text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none transition-colors"
                    />
                  </div>
                </div>

                {/* Work Email */}
                <div className="space-y-1">
                  <label htmlFor="signup-email" className="block text-xs font-semibold text-slate-300">
                    Work Email
                  </label>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                      <Mail className="w-3.5 h-3.5" />
                    </div>
                    <input
                      id="signup-email"
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
                      className={`w-full pl-9 pr-3.5 py-2 text-xs rounded-xl bg-[#141C2B] border text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 transition-colors ${
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

                {/* Password & Confirm Password */}
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3">
                  {/* Password */}
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <label htmlFor="signup-password" className="block text-xs font-semibold text-slate-300">
                        Password
                      </label>
                      <span
                        className={`text-[10px] font-medium ${
                          password.length >= 6 ? 'text-emerald-400' : 'text-slate-400'
                        }`}
                      >
                        6+ chars
                      </span>
                    </div>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                        <Lock className="w-3.5 h-3.5" />
                      </div>
                      <input
                        id="signup-password"
                        type={showPassword ? 'text' : 'password'}
                        required
                        autoComplete="new-password"
                        placeholder="••••••••"
                        value={password}
                        onChange={(e) => setPassword(e.target.value)}
                        className="w-full pl-9 pr-9 py-2 text-xs rounded-xl bg-[#141C2B] border border-[#1E293B] text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none transition-colors"
                      />
                      <button
                        type="button"
                        onClick={() => setShowPassword(!showPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                        aria-label={showPassword ? 'Hide password' : 'Show password'}
                      >
                        {showPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>

                  {/* Confirm Password */}
                  <div className="space-y-1">
                    <div className="flex items-center justify-between">
                      <label htmlFor="signup-confirm-password" className="block text-xs font-semibold text-slate-300">
                        Confirm
                      </label>
                      {confirmPassword && (
                        <span
                          className={`text-[10px] font-medium ${
                            passwordsMatch ? 'text-emerald-400' : 'text-rose-400'
                          }`}
                        >
                          {passwordsMatch ? 'Match' : 'Mismatch'}
                        </span>
                      )}
                    </div>
                    <div className="relative">
                      <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                        <Lock className="w-3.5 h-3.5" />
                      </div>
                      <input
                        id="signup-confirm-password"
                        type={showConfirmPassword ? 'text' : 'password'}
                        required
                        autoComplete="new-password"
                        placeholder="••••••••"
                        value={confirmPassword}
                        onBlur={() => setConfirmTouched(true)}
                        onChange={(e) => setConfirmPassword(e.target.value)}
                        className={`w-full pl-9 pr-9 py-2 text-xs rounded-xl bg-[#141C2B] border text-slate-100 placeholder-slate-500 focus:outline-none focus:ring-1 transition-colors ${
                          confirmTouched && confirmPassword && !passwordsMatch
                            ? 'border-rose-500 focus:border-rose-500 focus:ring-rose-500'
                            : 'border-[#1E293B] focus:border-blue-500 focus:ring-blue-500'
                        }`}
                      />
                      <button
                        type="button"
                        onClick={() => setShowConfirmPassword(!showConfirmPassword)}
                        className="absolute inset-y-0 right-0 pr-3 flex items-center text-slate-400 hover:text-slate-200 transition-colors cursor-pointer"
                        aria-label={showConfirmPassword ? 'Hide password' : 'Show password'}
                      >
                        {showConfirmPassword ? <EyeOff className="w-3.5 h-3.5" /> : <Eye className="w-3.5 h-3.5" />}
                      </button>
                    </div>
                  </div>
                </div>

                {/* Optional Phone Number */}
                <div className="space-y-1">
                  <div className="flex items-center justify-between">
                    <label htmlFor="signup-phone" className="block text-xs font-semibold text-slate-300">
                      Phone Number
                    </label>
                    <span className="text-[10px] text-slate-400 font-medium">Optional</span>
                  </div>
                  <div className="relative">
                    <div className="absolute inset-y-0 left-0 pl-3.5 flex items-center pointer-events-none text-slate-400">
                      <Phone className="w-3.5 h-3.5" />
                    </div>
                    <input
                      id="signup-phone"
                      type="tel"
                      autoComplete="tel"
                      placeholder="+91 98765 43210"
                      value={phoneNumber}
                      onChange={(e) => setPhoneNumber(e.target.value)}
                      className="w-full pl-9 pr-3.5 py-2 text-xs rounded-xl bg-[#141C2B] border border-[#1E293B] text-slate-100 placeholder-slate-500 focus:border-blue-500 focus:ring-1 focus:ring-blue-500 focus:outline-none transition-colors"
                    />
                  </div>
                </div>

                {/* Submit Action Button */}
                <Button
                  type="submit"
                  variant="primary"
                  size="md"
                  disabled={isLoading || (confirmPassword && !passwordsMatch)}
                  className="w-full mt-2 font-semibold text-xs justify-center py-2.5 shadow-sm shadow-blue-500/20"
                >
                  {isLoading ? (
                    <>
                      <Loader2 className="w-3.5 h-3.5 animate-spin mr-2" />
                      <span>Creating account…</span>
                    </>
                  ) : (
                    <>
                      <span>Create Account</span>
                      <ArrowRight className="w-3.5 h-3.5 ml-1.5" />
                    </>
                  )}
                </Button>
              </form>

              {/* Navigation Link to Login */}
              <div className="mt-5 pt-4 border-t border-slate-800/80 text-center">
                <p className="text-xs text-slate-400">
                  Already have an account?{' '}
                  <button
                    type="button"
                    onClick={onNavigateToLogin}
                    className="font-bold text-blue-400 hover:text-blue-300 transition-colors cursor-pointer ml-1"
                  >
                    Sign In
                  </button>
                </p>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
