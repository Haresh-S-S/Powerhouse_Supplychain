import React, { createContext, useContext, useState, useEffect, useCallback } from 'react';
import apiClient from '../services/apiClient';

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
  const [user, setUser] = useState(null);
  const [token, setToken] = useState(() => apiClient.getToken());
  const [isLoading, setIsLoading] = useState(true);
  const [onboardingCompleted, setOnboardingCompleted] = useState(false);
  const [activeBusiness, setActiveBusiness] = useState(null);
  const [userBusinesses, setUserBusinesses] = useState([]);

  // Check existing session on mount
  useEffect(() => {
    async function verifySession() {
      const storedToken = apiClient.getToken();
      if (!storedToken) {
        setIsLoading(false);
        return;
      }

      try {
        const res = await apiClient.getMe();
        if (res && res.authenticated && res.user) {
          setUser({
            id: res.user.id,
            email: res.user.email,
            fullName: res.user.full_name,
            phoneNumber: res.user.phone_number,
          });
          setToken(storedToken);
          setOnboardingCompleted(Boolean(res.onboarding_completed));
          setUserBusinesses(res.business_profiles || []);
          setActiveBusiness(res.active_business || null);
        } else {
          apiClient.clearToken();
          setToken(null);
          setUser(null);
        }
      } catch (err) {
        // Token invalid, expired, or backend offline with stale token
        apiClient.clearToken();
        setToken(null);
        setUser(null);
      } finally {
        setIsLoading(false);
      }
    }

    verifySession();
  }, []);

  const commitUserSession = useCallback((res, isOnboarding = false) => {
    if (res?.user && res?.access_token) {
      setUser({
        id: res.user.id,
        email: res.user.email,
        fullName: res.user.full_name,
        phoneNumber: res.user.phone_number,
      });
      setToken(res.access_token);
      setOnboardingCompleted(isOnboarding ? false : Boolean(res.onboarding_completed));
      if (res.business_profiles) {
        setUserBusinesses(res.business_profiles);
        setActiveBusiness(res.active_business || null);
      }
    }
  }, []);

  const signup = useCallback(async (fullName, email, password, phoneNumber = null, deferCommit = false) => {
    const res = await apiClient.signup({
      full_name: fullName,
      email,
      password,
      phone_number: phoneNumber,
    });

    if (!deferCommit && res?.user) {
      setUser({
        id: res.user.id,
        email: res.user.email,
        fullName: res.user.full_name,
        phoneNumber: res.user.phone_number,
      });
      setToken(res.access_token);
      setOnboardingCompleted(false);
      setActiveBusiness(null);
      setUserBusinesses([]);
    }
    return res;
  }, []);

  const login = useCallback(async (email, password) => {
    const res = await apiClient.login({ email, password });
    if (res?.user) {
      setUser({
        id: res.user.id,
        email: res.user.email,
        fullName: res.user.full_name,
        phoneNumber: res.user.phone_number,
      });
      setToken(res.access_token);
      setOnboardingCompleted(Boolean(res.onboarding_completed));

      // Fetch full status to retrieve profiles
      try {
        const status = await apiClient.getMe();
        if (status?.business_profiles) {
          setUserBusinesses(status.business_profiles);
          setActiveBusiness(status.active_business || null);
        }
      } catch (e) {
        // Keep response state
      }
    }
    return res;
  }, []);

  const logout = useCallback(async () => {
    try {
      await apiClient.logout();
    } finally {
      setUser(null);
      setToken(null);
      setOnboardingCompleted(false);
      setActiveBusiness(null);
      setUserBusinesses([]);
      if (typeof window !== 'undefined') {
        window.localStorage.removeItem('phflow_onboarding_v1');
      }
    }
  }, []);

  const updateOnboardingState = useCallback((completed, businessProfile = null) => {
    setOnboardingCompleted(Boolean(completed));
    if (businessProfile) {
      setActiveBusiness(businessProfile);
      setUserBusinesses((prev) => {
        const filtered = prev.filter((b) => b.id !== businessProfile.id);
        return [businessProfile, ...filtered];
      });
    }
  }, []);

  const switchActiveBusiness = useCallback((businessProfile) => {
    setActiveBusiness(businessProfile);
  }, []);

  return (
    <AuthContext.Provider
      value={{
        user,
        token,
        isAuthenticated: Boolean(token && user),
        isLoading,
        onboardingCompleted,
        activeBusiness,
        userBusinesses,
        signup,
        login,
        logout,
        commitUserSession,
        updateOnboardingState,
        switchActiveBusiness,
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

export default AuthContext;
