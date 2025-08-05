import { useCallback } from 'react';
import { useChatStore, chatStoreUtils } from '../stores/chatStore';
import { websocketService } from '../services/websocket';
import { apiService } from '../services/api';

export const useChat = () => {
  const store = useChatStore();

  const sendMessage = useCallback(async (message: string) => {
    try {
      // Add user message to chat
      chatStoreUtils.addUserMessage(message);
      
      // Set loading state
      store.setLoading(true);
      store.setError(undefined);
      
      // Send message via WebSocket if connected
      if (websocketService.isConnected()) {
        websocketService.sendMessage(message);
      } else {
        // Fallback to REST API
        const response = await apiService.sendChatMessage({
          message,
          session_id: store.sessionId,
          user_id: 'user'
        });
        
        // Add response to chat
        const agentMessage = {
          id: response.message_id,
          type: 'assistant' as const,
          content: response.content,
          timestamp: new Date().toISOString(),
          session_id: response.session_id,
          tool_results: []
        };
        
        store.addMessage(agentMessage);
        store.setLoading(false);
      }
      
    } catch (error) {
      console.error('Failed to send message:', error);
      store.setLoading(false);
      store.setError('Failed to send message');
      chatStoreUtils.addErrorMessage('Failed to send message. Please try again.');
    }
  }, [store]);

  const clearChat = useCallback(() => {
    store.clearMessages();
    chatStoreUtils.initializeSession();
  }, [store]);

  const reconnect = useCallback(async () => {
    try {
      store.setError(undefined);
      await websocketService.connect(store.sessionId);
    } catch (error) {
      console.error('Failed to reconnect:', error);
      store.setError('Failed to reconnect to server');
    }
  }, [store]);

  return {
    // State
    messages: store.messages,
    isConnected: store.isConnected,
    isLoading: store.isLoading,
    currentProgress: store.currentProgress,
    error: store.error,
    sessionId: store.sessionId,
    
    // Actions
    sendMessage,
    clearChat,
    reconnect,
    
    // Utilities
    hasMessages: chatStoreUtils.hasMessages(),
    conversationStats: chatStoreUtils.getConversationSummary(),
  };
};
