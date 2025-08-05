import axios, { AxiosInstance } from 'axios';
import { 
  UserQuery, 
  AgentResponse, 
  ToolDefinition, 
  SystemStatus, 
  ChatMessage, 
  ApiService,
  HealthCheck 
} from '../types';

class ApiServiceImpl implements ApiService {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: '/api/v1',
      timeout: 30000,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      (config) => {
        console.log(`API Request: ${config.method?.toUpperCase()} ${config.url}`);
        return config;
      },
      (error) => {
        console.error('API Request Error:', error);
        return Promise.reject(error);
      }
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => {
        console.log(`API Response: ${response.status} ${response.config.url}`);
        return response;
      },
      (error) => {
        console.error('API Response Error:', error.response?.data || error.message);
        return Promise.reject(error);
      }
    );
  }

  async sendChatMessage(query: UserQuery): Promise<AgentResponse> {
    try {
      const response = await this.client.post<AgentResponse>('/chat', query);
      return response.data;
    } catch (error) {
      console.error('Failed to send chat message:', error);
      throw new Error('Failed to send message to the agent');
    }
  }

  async getTools(): Promise<ToolDefinition[]> {
    try {
      const response = await this.client.get<ToolDefinition[]>('/tools');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch tools:', error);
      throw new Error('Failed to fetch available tools');
    }
  }

  async getSystemStatus(): Promise<SystemStatus> {
    try {
      const response = await this.client.get<SystemStatus>('/system/status');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch system status:', error);
      throw new Error('Failed to fetch system status');
    }
  }

  async getSessionHistory(sessionId: string): Promise<ChatMessage[]> {
    try {
      const response = await this.client.get<{
        session_id: string;
        history: ChatMessage[];
        message_count: number;
      }>(`/sessions/${sessionId}/history`);
      return response.data.history;
    } catch (error) {
      console.error('Failed to fetch session history:', error);
      throw new Error('Failed to fetch conversation history');
    }
  }

  async clearSession(sessionId: string): Promise<void> {
    try {
      await this.client.delete(`/sessions/${sessionId}`);
    } catch (error) {
      console.error('Failed to clear session:', error);
      throw new Error('Failed to clear conversation history');
    }
  }

  async getHealthCheck(): Promise<HealthCheck> {
    try {
      const response = await this.client.get<HealthCheck>('/health');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch health status:', error);
      throw new Error('Failed to check system health');
    }
  }

  async getToolDefinition(toolName: string): Promise<ToolDefinition> {
    try {
      const response = await this.client.get<ToolDefinition>(`/tools/${toolName}`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch tool definition for ${toolName}:`, error);
      throw new Error(`Failed to fetch definition for tool: ${toolName}`);
    }
  }

  async executeToolDirectly(toolName: string, parameters: Record<string, any>): Promise<any> {
    try {
      const response = await this.client.post(`/tools/${toolName}/execute`, parameters);
      return response.data;
    } catch (error) {
      console.error(`Failed to execute tool ${toolName}:`, error);
      throw new Error(`Failed to execute tool: ${toolName}`);
    }
  }

  async searchTools(query: string): Promise<{
    query: string;
    results: Array<{
      name: string;
      description: string;
      category: string;
      enabled: boolean;
    }>;
    count: number;
  }> {
    try {
      const response = await this.client.post('/tools/search', { query });
      return response.data;
    } catch (error) {
      console.error('Failed to search tools:', error);
      throw new Error('Failed to search tools');
    }
  }

  async toggleTool(toolName: string): Promise<{
    tool_name: string;
    status: string;
    message: string;
  }> {
    try {
      const response = await this.client.post(`/tools/${toolName}/toggle`);
      return response.data;
    } catch (error) {
      console.error(`Failed to toggle tool ${toolName}:`, error);
      throw new Error(`Failed to toggle tool: ${toolName}`);
    }
  }

  async getToolCategories(): Promise<{
    categories: string[];
    details: Record<string, {
      tool_count: number;
      tools: string[];
    }>;
  }> {
    try {
      const response = await this.client.get('/tools/categories');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch tool categories:', error);
      throw new Error('Failed to fetch tool categories');
    }
  }

  async getActiveSessions(): Promise<{
    active_sessions: number;
    sessions: Record<string, any>;
  }> {
    try {
      const response = await this.client.get('/sessions');
      return response.data;
    } catch (error) {
      console.error('Failed to fetch active sessions:', error);
      throw new Error('Failed to fetch active sessions');
    }
  }

  async getSessionStats(sessionId: string): Promise<{
    session_id: string;
    created_at: number;
    message_count: number;
    conversation_length: number;
    last_activity?: string;
  }> {
    try {
      const response = await this.client.get(`/sessions/${sessionId}/stats`);
      return response.data;
    } catch (error) {
      console.error(`Failed to fetch session stats for ${sessionId}:`, error);
      throw new Error('Failed to fetch session statistics');
    }
  }
}

// Create singleton instance
export const apiService = new ApiServiceImpl();

// Utility functions for common API operations
export const apiUtils = {
  // Check if the backend is available
  async checkBackendHealth(): Promise<boolean> {
    try {
      await apiService.getHealthCheck();
      return true;
    } catch {
      return false;
    }
  },

  // Get a formatted error message from an API error
  getErrorMessage(error: any): string {
    if (error.response?.data?.detail) {
      return error.response.data.detail;
    }
    if (error.response?.data?.message) {
      return error.response.data.message;
    }
    if (error.message) {
      return error.message;
    }
    return 'An unexpected error occurred';
  },

  // Retry an API call with exponential backoff
  async retryApiCall<T>(
    apiCall: () => Promise<T>,
    maxRetries: number = 3,
    baseDelay: number = 1000
  ): Promise<T> {
    let lastError: any;

    for (let attempt = 0; attempt <= maxRetries; attempt++) {
      try {
        return await apiCall();
      } catch (error) {
        lastError = error;
        
        if (attempt === maxRetries) {
          break;
        }

        // Exponential backoff
        const delay = baseDelay * Math.pow(2, attempt);
        await new Promise(resolve => setTimeout(resolve, delay));
      }
    }

    throw lastError;
  }
};
