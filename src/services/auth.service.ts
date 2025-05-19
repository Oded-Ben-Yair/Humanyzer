
import axios from 'axios';
import { env } from '@/config/env.config';

// Interface for user data
export interface User {
  id: string;
  username: string;
  email: string;
  role: string;
}

// Interface for authentication credentials
export interface AuthCredentials {
  username: string;
  password: string;
}

// Interface for authentication response
export interface AuthResponse {
  user: User;
  token: string;
}

class AuthService {
  private token: string | null = null;
  private user: User | null = null;

  // Fixed login bug with special characters ('&' and '#')
  async login(credentials: AuthCredentials): Promise<User> {
    try {
      // Properly encode username and password to handle special characters
      const encodedUsername = encodeURIComponent(credentials.username);
      const encodedPassword = encodeURIComponent(credentials.password);
      
      const response = await axios.post<AuthResponse>(
        `${env.API_URL}/auth/login`,
        {
          username: encodedUsername,
          password: encodedPassword
        }
      );

      this.token = response.data.token;
      this.user = response.data.user;
      
      // Store token in localStorage
      localStorage.setItem('auth_token', this.token);
      
      return this.user;
    } catch (error) {
      console.error('Login failed:', error);
      throw new Error('Authentication failed. Please check your credentials.');
    }
  }

  async logout(): Promise<void> {
    this.token = null;
    this.user = null;
    localStorage.removeItem('auth_token');
  }

  async getCurrentUser(): Promise<User | null> {
    if (this.user) {
      return this.user;
    }

    const token = localStorage.getItem('auth_token');
    if (!token) {
      return null;
    }

    try {
      const response = await axios.get<User>(`${env.API_URL}/auth/me`, {
        headers: {
          Authorization: `Bearer ${token}`
        }
      });
      
      this.user = response.data;
      return this.user;
    } catch (error) {
      console.error('Failed to get current user:', error);
      return null;
    }
  }

  isAuthenticated(): boolean {
    return !!this.token || !!localStorage.getItem('auth_token');
  }

  getToken(): string | null {
    return this.token || localStorage.getItem('auth_token');
  }
}

export const authService = new AuthService();
