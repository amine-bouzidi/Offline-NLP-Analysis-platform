import axios from 'axios';
import type { User, LoginResponse, LoginCredentials } from '@/types/auth';

const API_URL = import.meta.env.VITE_API_URL;

class AuthService {
  private static token: string | null = localStorage.getItem('token');

  static getAxiosInstance() {
    return axios.create({
      baseURL: API_URL,
      headers: {
        Authorization: `Bearer ${this.token}`,
      },
    });
  }

  static async login(credentials: LoginCredentials): Promise<LoginResponse> {
    const response = await axios.post<LoginResponse>(
      `${API_URL}/auth/login`,
      credentials
    );
    if (response.data.access_token) {
      this.token = response.data.access_token;
      localStorage.setItem('token', this.token);
      localStorage.setItem('user', JSON.stringify(response.data.user));
    }
    return response.data;
  }

  static logout(): void {
    this.token = null;
    localStorage.removeItem('token');
    localStorage.removeItem('user');
  }

  static getUser(): User | null {
    const user = localStorage.getItem('user');
    return user ? JSON.parse(user) : null;
  }

  static getToken(): string | null {
    return this.token || localStorage.getItem('token');
  }

  static isAuthenticated(): boolean {
    return !!this.getToken();
  }
}

export default AuthService;