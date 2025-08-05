// Message Types
export type MessageType = 'user' | 'assistant' | 'system' | 'tool_execution' | 'error';

export type ContentType = 'text' | 'code' | 'image' | 'data' | 'error';

export type ToolStatus = 'pending' | 'running' | 'completed' | 'failed';

// Content Structure
export interface MessageContent {
  type: ContentType;
  content: string | Record<string, any>;
  metadata?: Record<string, any>;
}

// Tool Result
export interface ToolResult {
  tool_name: string;
  status: ToolStatus;
  result?: Record<string, any>;
  error?: string;
  execution_time?: number;
}

// Chat Message
export interface ChatMessage {
  id: string;
  type: MessageType;
  content: MessageContent[];
  timestamp: string;
  user_id?: string;
  session_id?: string;
  tool_results?: ToolResult[];
}

// User Query
export interface UserQuery {
  message: string;
  session_id?: string;
  user_id?: string;
  context?: Record<string, any>;
}

// Agent Response
export interface AgentResponse {
  message_id: string;
  response_type: MessageType;
  content: MessageContent[];
  tools_used?: string[];
  processing_time?: number;
  session_id?: string;
}

// WebSocket Message Types
export interface WebSocketMessage {
  type: string;
  data: Record<string, any>;
  timestamp?: string;
}

// Progress Update
export interface ProgressUpdate {
  message: string;
  progress: number;
  session_id?: string;
}

// Tool Definition
export interface ToolDefinition {
  name: string;
  description: string;
  parameters: Record<string, any>;
  required_params: string[];
  category: string;
  enabled: boolean;
}

// Session Info
export interface SessionInfo {
  session_id: string;
  created_at: number;
  message_count: number;
  conversation_length: number;
  last_activity?: string;
}

// Chat State
export interface ChatState {
  messages: ChatMessage[];
  isConnected: boolean;
  isLoading: boolean;
  currentProgress?: ProgressUpdate;
  sessionId: string;
  error?: string;
}

// API Response Types
export interface ApiResponse<T = any> {
  data?: T;
  error?: string;
  message?: string;
}

export interface HealthCheck {
  status: string;
  timestamp: string;
  version: string;
  services: Record<string, string>;
}

export interface SystemStatus {
  system: {
    status: string;
    version: string;
    debug_mode: boolean;
  };
  tools: {
    total_tools: number;
    enabled_tools: number;
    tool_status: Record<string, any>;
  };
  sessions: {
    active_sessions: number;
    total_messages: number;
  };
  connections: {
    websocket_connections: number;
  };
  configuration: {
    openai_configured: boolean;
    cors_origins: string[];
  };
}

// UI Component Props
export interface MessageBubbleProps {
  message: ChatMessage;
  isUser: boolean;
}

export interface ChatInputProps {
  onSendMessage: (message: string) => void;
  disabled?: boolean;
  placeholder?: string;
}

export interface ProgressIndicatorProps {
  progress?: ProgressUpdate;
  isVisible: boolean;
}

export interface ToolExecutionIndicatorProps {
  toolResults?: ToolResult[];
  isVisible: boolean;
}

// Store Types
export interface ChatStore {
  // State
  messages: ChatMessage[];
  isConnected: boolean;
  isLoading: boolean;
  currentProgress?: ProgressUpdate;
  sessionId: string;
  error?: string;
  
  // Actions
  addMessage: (message: ChatMessage) => void;
  setConnected: (connected: boolean) => void;
  setLoading: (loading: boolean) => void;
  setProgress: (progress?: ProgressUpdate) => void;
  setError: (error?: string) => void;
  clearMessages: () => void;
  generateSessionId: () => string;
}

// Service Types
export interface WebSocketService {
  connect: (sessionId: string) => Promise<void>;
  disconnect: () => void;
  sendMessage: (message: string) => void;
  isConnected: () => boolean;
  onMessage: (callback: (message: WebSocketMessage) => void) => void;
  onConnect: (callback: () => void) => void;
  onDisconnect: (callback: () => void) => void;
  onError: (callback: (error: Error) => void) => void;
}

export interface ApiService {
  sendChatMessage: (query: UserQuery) => Promise<AgentResponse>;
  getTools: () => Promise<ToolDefinition[]>;
  getSystemStatus: () => Promise<SystemStatus>;
  getSessionHistory: (sessionId: string) => Promise<ChatMessage[]>;
  clearSession: (sessionId: string) => Promise<void>;
}
