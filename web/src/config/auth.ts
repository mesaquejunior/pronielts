// Mock authentication configuration
// In production, this would use Azure AD B2C or similar

export interface AuthUser {
  email: string;
  name: string;
  role: 'admin' | 'viewer';
}

const MOCK_USERS: Record<string, { password: string; user: AuthUser }> = {
  'admin@pronielts.com': {
    password: 'admin123',
    user: { email: 'admin@pronielts.com', name: 'Admin User', role: 'admin' },
  },
};

export function authenticate(email: string, password: string): AuthUser | null {
  const entry = MOCK_USERS[email];
  if (entry && entry.password === password) {
    return entry.user;
  }
  return null;
}

export function getStoredUser(): AuthUser | null {
  const stored = localStorage.getItem('pronielts_user');
  if (stored) {
    return JSON.parse(stored);
  }
  return null;
}

export function storeUser(user: AuthUser): void {
  localStorage.setItem('pronielts_user', JSON.stringify(user));
}

export function clearUser(): void {
  localStorage.removeItem('pronielts_user');
}
