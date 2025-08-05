import React, { useEffect, useRef } from 'react';
import { Wifi, WifiOff, AlertCircle } from 'lucide-react';
import MessageBubble from './MessageBubble';
import ChatInput from './ChatInput';
import ProgressIndicator from './ProgressIndicator';
import { chatSelectors } from '../stores/chatStore';

const ChatInterface: React.FC = () => {
  const messages = chatSelectors.useMessages();
  const isConnected = chatSelectors.useConnectionStatus();
  const isLoading = chatSelectors.useLoadingState();
  const progress = chatSelectors.useProgress();
  const error = chatSelectors.useError();
  const messagesEndRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when new messages arrive
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [messages, progress]);

  const handleSendMessage = (message: string) => {
    // This will be implemented in the parent component or via context
    console.log('Sending message:', message);
  };

  const getConnectionStatus = () => {
    if (error) {
      return (
        <div className="connection-indicator connection-disconnected">
          <AlertCircle size={12} />
          <span>Error: {error}</span>
        </div>
      );
    }

    if (isConnected) {
      return (
        <div className="connection-indicator connection-connected">
          <Wifi size={12} />
          <span>Connected</span>
        </div>
      );
    }

    return (
      <div className="connection-indicator connection-disconnected">
        <WifiOff size={12} />
        <span>Disconnected</span>
      </div>
    );
  };

  return (
    <div className="chat-container">
      {/* Header */}
      <div className="bg-white border-b px-4 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold text-gray-900">
            Agentic Chat Assistant
          </h1>
          <p className="text-sm text-gray-500">
            AI-powered assistant with specialized tools
          </p>
        </div>
        
        <div className="flex items-center gap-3">
          {getConnectionStatus()}
        </div>
      </div>

      {/* Messages Area */}
      <div className="flex-1 overflow-y-auto custom-scrollbar bg-gray-50">
        {messages.length === 0 ? (
          <div className="flex items-center justify-center h-full">
            <div className="text-center max-w-md mx-auto px-4">
              <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <div className="w-8 h-8 bg-primary-500 rounded-full"></div>
              </div>
              <h2 className="text-xl font-semibold text-gray-900 mb-2">
                Welcome to Agentic Chat
              </h2>
              <p className="text-gray-600 mb-6">
                I'm an AI assistant with access to specialized tools. I can help you with:
              </p>
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                <div className="bg-white p-3 rounded-lg border">
                  <div className="font-medium text-gray-900">💬 Text Generation</div>
                  <div className="text-gray-600">Creative writing, explanations, Q&A</div>
                </div>
                <div className="bg-white p-3 rounded-lg border">
                  <div className="font-medium text-gray-900">💻 Code Help</div>
                  <div className="text-gray-600">Programming assistance, debugging</div>
                </div>
                <div className="bg-white p-3 rounded-lg border">
                  <div className="font-medium text-gray-900">🔍 Web Search</div>
                  <div className="text-gray-600">Current information, research</div>
                </div>
                <div className="bg-white p-3 rounded-lg border">
                  <div className="font-medium text-gray-900">🎨 Image Generation</div>
                  <div className="text-gray-600">Create visual content</div>
                </div>
              </div>
              <p className="text-gray-500 text-sm mt-6">
                Start by typing a message below!
              </p>
            </div>
          </div>
        ) : (
          <div className="py-4">
            {messages.map((message) => (
              <MessageBubble
                key={message.id}
                message={message}
                isUser={message.type === 'user'}
              />
            ))}
            
            {/* Progress indicator */}
            <ProgressIndicator 
              progress={progress} 
              isVisible={isLoading && !!progress} 
            />
            
            {/* Scroll anchor */}
            <div ref={messagesEndRef} />
          </div>
        )}
      </div>

      {/* Input Area */}
      <ChatInput
        onSendMessage={handleSendMessage}
        disabled={!isConnected || isLoading}
        placeholder={
          !isConnected 
            ? "Connecting..." 
            : isLoading 
            ? "Processing your request..." 
            : "Type your message..."
        }
      />
    </div>
  );
};

export default ChatInterface;
