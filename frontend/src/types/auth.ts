export interface User {
  id: string;
  username: string;
  email: string;
  role: 'analyst' | 'decision_maker' | 'admin';
  createdAt: string;
}

export interface AuthState {
  user: User | null;
  token: string | null;
  isAuthenticated: boolean;
}

export interface LoginCredentials {
  username: string;
  password: string;
}

export interface LoginResponse {
  status: string;
  access_token: string;
  user: User;
}