import React, { useEffect } from 'react';
import { Toaster } from 'react-hot-toast';
import ChatInterface from './components/ChatInterface';
import { useChatStore, chatStoreUtils } from './stores/chatStore';
import { websocketService } from './services/websocket';
import { WebSocketMessage } from './types';

function App() {
  const { 
    setConnected, 
    setLoading, 
    setProgress, 
    setError, 
    addMessage,
    sessionId,
    generateSessionId 
  } = useChatStore();

  useEffect(() => {
    // Initialize session
    const initSession = async () => {
      try {
        const newSessionId = sessionId || generateSessionId();
        
        // Set up WebSocket event handlers
        websocketService.onConnect(() => {
          console.log('WebSocket connected');
          setConnected(true);
          setError(undefined);
        });

        websocketService.onDisconnect(() => {
          console.log('WebSocket disconnected');
          setConnected(false);
        });

        websocketService.onError((error) => {
          console.error('WebSocket error:', error);
          setError(error.message);
          setConnected(false);
        });

        websocketService.onMessage((message: WebSocketMessage) => {
          handleWebSocketMessage(message);
        });

        // Connect to WebSocket
        await websocketService.connect(newSessionId);
        
        // Add welcome message if no messages exist
        if (!chatStoreUtils.hasMessages()) {
          chatStoreUtils.initializeSession();
        }

      } catch (error) {
        console.error('Failed to initialize session:', error);
        setError('Failed to connect to the server');
      }
    };

    initSession();

    // Cleanup on unmount
    return () => {
      websocketService.disconnect();
    };
  }, []);

  const handleWebSocketMessage = (message: WebSocketMessage) => {
    console.log('Received WebSocket message:', message);

    switch (message.type) {
      case 'message_received':
        // Message acknowledgment
        console.log('Message received by server');
        break;

      case 'progress_update':
        // Update progress
        setProgress(message.data);
        break;

      case 'agent_response':
        // Add agent response to chat
        setLoading(false);
        setProgress(undefined);
        
        const agentMessage = {
          id: message.data.message_id,
          type: 'assistant' as const,
          content: message.data.content,
          timestamp: new Date().toISOString(),
          session_id: message.data.session_id,
          tool_results: message.data.tool_results
        };
        
        addMessage(agentMessage);
        break;

      case 'error':
        // Handle errors
        setLoading(false);
        setProgress(undefined);
        setError(message.data.error);
        chatStoreUtils.addErrorMessage(message.data.error);
        break;

      case 'session_initialized':
        console.log('Session initialized:', message.data.session_id);
        break;

      case 'pong':
        // Handle ping response
        console.log('Received pong');
        break;

      default:
        console.log('Unknown message type:', message.type);
    }
  };

  const handleSendMessage = async (messageText: string) => {
    try {
      // Add user message to chat
      chatStoreUtils.addUserMessage(messageText);
      
      // Set loading state
      setLoading(true);
      setError(undefined);
      
      // Send message via WebSocket
      websocketService.sendMessage(messageText);
      
    } catch (error) {
      console.error('Failed to send message:', error);
      setLoading(false);
      setError('Failed to send message');
      chatStoreUtils.addErrorMessage('Failed to send message. Please try again.');
    }
  };

  // Override the handleSendMessage in ChatInterface
  const ChatInterfaceWithHandler = () => {
    const chatInterface = React.createElement(ChatInterface);
    
    // Clone the element and add our handler
    return React.cloneElement(chatInterface, {
      onSendMessage: handleSendMessage
    });
  };

  return (
    <div className="App">
      <ChatInterface />
      
      {/* Toast notifications */}
      <Toaster
        position="top-right"
        toastOptions={{
          duration: 4000,
          style: {
            background: '#363636',
            color: '#fff',
          },
          success: {
            duration: 3000,
            iconTheme: {
              primary: '#4ade80',
              secondary: '#fff',
            },
          },
          error: {
            duration: 5000,
            iconTheme: {
              primary: '#ef4444',
              secondary: '#fff',
            },
          },
        }}
      />
    </div>
  );
}

export default App;
