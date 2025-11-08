import axios, { AxiosResponse } from 'axios';
import keytar from 'keytar';
import Conf from 'conf';
import chalk from 'chalk';
import { User, LoginCredentials, SignupCredentials, AuthToken, ApiResponse } from '@/types/auth';

export class AuthClient {
  private apiUrl: string;
  private config: Conf;
  private readonly serviceName = 'claude-code-cli';
  private readonly tokenKey = 'auth-token';

  constructor(apiUrl: string = 'http://localhost:8000/api') {
    this.apiUrl = apiUrl;
    this.config = new Conf({
      projectName: 'claude-code',
      configName: 'config'
    });
  }

  // Token management
  private async saveToken(token: string): Promise<void> {
    try {
      await keytar.setPassword(this.serviceName, this.tokenKey, token);
      this.config.set('lastLogin', new Date().toISOString());
    } catch (error) {
      console.warn(chalk.yellow('⚠ Could not save token securely, falling back to config file'));
      this.config.set('token', token);
    }
  }

  private async getToken(): Promise<string | null> {
    try {
      const token = await keytar.getPassword(this.serviceName, this.tokenKey);
      return token;
    } catch (error) {
      // Fallback to config file
      return this.config.get('token') as string || null;
    }
  }

  private async clearToken(): Promise<void> {
    try {
      await keytar.deletePassword(this.serviceName, this.tokenKey);
    } catch (error) {
      // Ignore errors when clearing
    }
    this.config.delete('token');
    this.config.delete('lastLogin');
  }

  // HTTP client with auth
  private async getAuthHeaders(): Promise<Record<string, string>> {
    const token = await this.getToken();
    return token ? { Authorization: `Bearer ${token}` } : {};
  }

  private async apiRequest<T>(
    method: 'GET' | 'POST' | 'PUT' | 'DELETE',
    endpoint: string,
    data?: any
  ): Promise<ApiResponse<T>> {
    try {
      const headers = await this.getAuthHeaders();

      const response: AxiosResponse<T> = await axios({
        method,
        url: `${this.apiUrl}${endpoint}`,
        data,
        headers: {
          'Content-Type': 'application/json',
          ...headers
        },
        timeout: 10000
      });

      return {
        data: response.data,
        status: response.status
      };
    } catch (error: any) {
      const status = error.response?.status || 500;
      const message = error.response?.data?.detail || error.message || 'Network error';

      return {
        error: message,
        status
      };
    }
  }

  // Authentication methods
  async signup(credentials: SignupCredentials): Promise<ApiResponse<User>> {
    const response = await this.apiRequest<User>('POST', '/auth/signup', credentials);

    if (response.data) {
      console.log(chalk.green('✅ Account created successfully'));
      console.log(chalk.blue('💡 Please sign in to start using Claude Code'));
    }

    return response;
  }

  async signin(credentials: LoginCredentials): Promise<ApiResponse<AuthToken>> {
    const response = await this.apiRequest<AuthToken>('POST', '/auth/signin', credentials);

    if (response.data?.access_token) {
      await this.saveToken(response.data.access_token);
      console.log(chalk.green('✅ Successfully signed in'));
    }

    return response;
  }

  async logout(): Promise<ApiResponse> {
    // Call server logout endpoint
    await this.apiRequest('POST', '/auth/logout');

    // Clear local token
    await this.clearToken();

    console.log(chalk.green('✅ Successfully logged out'));
    return { status: 200 };
  }

  async getProfile(): Promise<ApiResponse<User>> {
    return this.apiRequest<User>('GET', '/auth/profile');
  }

  async verifyToken(): Promise<boolean> {
    const response = await this.apiRequest('GET', '/auth/verify-token');
    return response.status === 200;
  }

  async isAuthenticated(): Promise<boolean> {
    const token = await this.getToken();
    if (!token) return false;

    return this.verifyToken();
  }

  async refreshApiKey(): Promise<ApiResponse<{ api_key: string }>> {
    const response = await this.apiRequest<{ api_key: string }>('POST', '/auth/refresh-api-key');

    if (response.data?.api_key) {
      console.log(chalk.green('✅ API key refreshed successfully'));
      console.log(chalk.blue('🔑 New API key:'), response.data.api_key);
    }

    return response;
  }

  // Configuration
  setApiUrl(url: string): void {
    this.apiUrl = url;
    this.config.set('apiUrl', url);
    console.log(chalk.green(`✅ API URL set to: ${url}`));
  }

  getApiUrl(): string {
    return this.config.get('apiUrl') as string || this.apiUrl;
  }

  getConfig(): Record<string, any> {
    return this.config.store;
  }
}

// Export singleton instance
export const authClient = new AuthClient();