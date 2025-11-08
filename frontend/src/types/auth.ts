export interface User {
  id: number;
  email: string;
  username?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface LoginCredentials {
  email: string;
  password: string;
}

export interface SignupCredentials extends LoginCredentials {
  username?: string;
}

export interface SignupFormData extends SignupCredentials {
  confirmPassword: string;
}

export interface AuthToken {
  access_token: string;
  token_type: string;
  expires_in: number;
}

export interface ApiResponse<T = any> {
  data?: T;
  message?: string;
  error?: string;
  status: number;
}

export interface AuthState {
  isAuthenticated: boolean;
  user?: User;
  token?: string;
  isLoading: boolean;
  error?: string;
}