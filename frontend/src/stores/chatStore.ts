import { create } from 'zustand';
import { ChatMessage, ProgressUpdate, ChatStore } from '../types';

export const useChatStore = create<ChatStore>((set, get) => ({
  // State
  messages: [],
  isConnected: false,
  isLoading: false,
  currentProgress: undefined,
  sessionId: '',
  error: undefined,

  // Actions
  addMessage: (message: ChatMessage) => {
    set((state) => ({
      messages: [...state.messages, message]
    }));
  },

  setConnected: (connected: boolean) => {
    set({ isConnected: connected });
    if (connected) {
      set({ error: undefined });
    }
  },

  setLoading: (loading: boolean) => {
    set({ isLoading: loading });
  },

  setProgress: (progress?: ProgressUpdate) => {
    set({ currentProgress: progress });
  },

  setError: (error?: string) => {
    set({ error });
  },

  clearMessages: () => {
    set({ messages: [] });
  },

  generateSessionId: () => {
    const sessionId = `session-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    set({ sessionId });
    return sessionId;
  },
}));

// Utility functions for working with the store
export const chatStoreUtils = {
  // Get the last message
  getLastMessage: (): ChatMessage | undefined => {
    const { messages } = useChatStore.getState();
    return messages[messages.length - 1];
  },

  // Get messages by type
  getMessagesByType: (type: string): ChatMessage[] => {
    const { messages } = useChatStore.getState();
    return messages.filter(msg => msg.type === type);
  },

  // Get user messages
  getUserMessages: (): ChatMessage[] => {
    return chatStoreUtils.getMessagesByType('user');
  },

  // Get assistant messages
  getAssistantMessages: (): ChatMessage[] => {
    return chatStoreUtils.getMessagesByType('assistant');
  },

  // Check if there are any messages
  hasMessages: (): boolean => {
    const { messages } = useChatStore.getState();
    return messages.length > 0;
  },

  // Get conversation summary
  getConversationSummary: () => {
    const { messages, sessionId } = useChatStore.getState();
    const userMessages = chatStoreUtils.getUserMessages();
    const assistantMessages = chatStoreUtils.getAssistantMessages();

    return {
      sessionId,
      totalMessages: messages.length,
      userMessages: userMessages.length,
      assistantMessages: assistantMessages.length,
      firstMessage: messages[0]?.timestamp,
      lastMessage: messages[messages.length - 1]?.timestamp,
    };
  },

  // Add a user message
  addUserMessage: (content: string) => {
    const message: ChatMessage = {
      id: `user-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'user',
      content: [{
        type: 'text',
        content: content
      }],
      timestamp: new Date().toISOString(),
      session_id: useChatStore.getState().sessionId,
    };

    useChatStore.getState().addMessage(message);
    return message;
  },

  // Add an assistant message
  addAssistantMessage: (content: string, metadata?: Record<string, any>) => {
    const message: ChatMessage = {
      id: `assistant-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'assistant',
      content: [{
        type: 'text',
        content: content,
        metadata
      }],
      timestamp: new Date().toISOString(),
      session_id: useChatStore.getState().sessionId,
    };

    useChatStore.getState().addMessage(message);
    return message;
  },

  // Add an error message
  addErrorMessage: (error: string) => {
    const message: ChatMessage = {
      id: `error-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'error',
      content: [{
        type: 'error',
        content: error
      }],
      timestamp: new Date().toISOString(),
      session_id: useChatStore.getState().sessionId,
    };

    useChatStore.getState().addMessage(message);
    return message;
  },

  // Add a system message
  addSystemMessage: (content: string) => {
    const message: ChatMessage = {
      id: `system-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`,
      type: 'system',
      content: [{
        type: 'text',
        content: content
      }],
      timestamp: new Date().toISOString(),
      session_id: useChatStore.getState().sessionId,
    };

    useChatStore.getState().addMessage(message);
    return message;
  },

  // Initialize a new session
  initializeSession: () => {
    const sessionId = useChatStore.getState().generateSessionId();
    useChatStore.getState().clearMessages();
    useChatStore.getState().setError(undefined);
    useChatStore.getState().setProgress(undefined);
    
    // Add welcome message
    chatStoreUtils.addSystemMessage(
      'Welcome to the Agentic Chat Assistant! I can help you with various tasks using specialized tools. What would you like to do today?'
    );

    return sessionId;
  },

  // Reset the entire store
  resetStore: () => {
    set({
      messages: [],
      isConnected: false,
      isLoading: false,
      currentProgress: undefined,
      sessionId: '',
      error: undefined,
    });
  },
};

// Selectors for common use cases
export const chatSelectors = {
  // Select messages
  useMessages: () => useChatStore((state) => state.messages),
  
  // Select connection status
  useConnectionStatus: () => useChatStore((state) => state.isConnected),
  
  // Select loading state
  useLoadingState: () => useChatStore((state) => state.isLoading),
  
  // Select current progress
  useProgress: () => useChatStore((state) => state.currentProgress),
  
  // Select session ID
  useSessionId: () => useChatStore((state) => state.sessionId),
  
  // Select error state
  useError: () => useChatStore((state) => state.error),
  
  // Select if chat is ready (connected and not loading)
  useChatReady: () => useChatStore((state) => state.isConnected && !state.isLoading),
  
  // Select conversation stats
  useConversationStats: () => useChatStore((state) => ({
    messageCount: state.messages.length,
    hasMessages: state.messages.length > 0,
    lastMessageTime: state.messages[state.messages.length - 1]?.timestamp,
  })),
};
