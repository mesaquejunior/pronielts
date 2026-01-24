import { useState, useCallback } from 'react';
import type { AuthUser } from '../config/auth';
import { authenticate, getStoredUser, storeUser, clearUser } from '../config/auth';

export function useAuth() {
  const [user, setUser] = useState<AuthUser | null>(() => getStoredUser());

  const login = useCallback((email: string, password: string): boolean => {
    const authUser = authenticate(email, password);
    if (authUser) {
      storeUser(authUser);
      setUser(authUser);
      return true;
    }
    return false;
  }, []);

  const logout = useCallback(() => {
    clearUser();
    setUser(null);
  }, []);

  return { user, loading: false, login, logout, isAuthenticated: !!user };
}
