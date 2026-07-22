import { createContext, useContext, useEffect, useMemo, useState } from 'react';
import { setAuthHeaders } from '../services/api';

const AuthContext = createContext(null);

const STORAGE_KEY = 'polylife-auth';

function loadAuth() {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {
    /* ignore */
  }
  return { userId: 1, role: 'coach' };
}

export function AuthProvider({ children }) {
  const [auth, setAuth] = useState(() => {
    const loaded = loadAuth();
    // Set headers immediately so the first API request is not sent without auth.
    setAuthHeaders(loaded.userId, loaded.role);
    return loaded;
  });

  useEffect(() => {
    setAuthHeaders(auth.userId, auth.role);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(auth));
  }, [auth]);

  const value = useMemo(
    () => ({
      userId: auth.userId,
      role: auth.role,
      isCoach: auth.role === 'coach',
      setUserId: (userId) => setAuth((prev) => ({ ...prev, userId: Number(userId) })),
      setRole: (role) => setAuth((prev) => ({ ...prev, role })),
    }),
    [auth],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error('useAuth must be used within AuthProvider');
  return ctx;
}
