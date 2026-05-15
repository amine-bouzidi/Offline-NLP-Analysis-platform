import { create } from 'zustand';
import AuthService from '@/lib/auth';
import type { User, LoginCredentials } from '@/types/auth';

interface AuthStore {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (credentials: LoginCredentials) => Promise<void>;
  logout: () => void;
  initialize: () => void;
}

export const useAuthStore = create<AuthStore>((set) => ({
  user: AuthService.getUser(),
  isAuthenticated: AuthService.isAuthenticated(),
  isLoading: false,

  login: async (credentials: LoginCredentials) => {
    set({ isLoading: true });
    try {
      const response = await AuthService.login(credentials);
      set({
        user: response.user,
        isAuthenticated: true,
      });
    } finally {
      set({ isLoading: false });
    }
  },

  logout: () => {
    AuthService.logout();
    set({
      user: null,
      isAuthenticated: false,
    });
  },

  initialize: () => {
    const user = AuthService.getUser();
    set({
      user,
      isAuthenticated: !!user,
    });
  },
}));