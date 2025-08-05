import React from 'react';
import { MessageBubbleProps, ContentType } from '../types';
import { User, Bot, AlertCircle, Code, Image, BarChart3 } from 'lucide-react';

const MessageBubble: React.FC<MessageBubbleProps> = ({ message, isUser }) => {
  const formatTimestamp = (timestamp: string) => {
    const date = new Date(timestamp);
    return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
  };

  const renderContent = (content: any, type: ContentType, metadata?: any) => {
    switch (type) {
      case 'text':
        return (
          <div className="whitespace-pre-wrap">
            {typeof content === 'string' ? content : JSON.stringify(content)}
          </div>
        );
      
      case 'code':
        return (
          <div className="mt-2">
            <div className="flex items-center gap-2 mb-2 text-sm text-gray-600">
              <Code size={16} />
              <span>Code Output</span>
              {metadata?.language && (
                <span className="px-2 py-1 bg-gray-100 rounded text-xs">
                  {metadata.language}
                </span>
              )}
            </div>
            <pre className="code-block">
              <code>{typeof content === 'string' ? content : JSON.stringify(content, null, 2)}</code>
            </pre>
          </div>
        );
      
      case 'image':
        return (
          <div className="mt-2">
            <div className="flex items-center gap-2 mb-2 text-sm text-gray-600">
              <Image size={16} />
              <span>Generated Image</span>
            </div>
            {typeof content === 'object' && content.url ? (
              <div className="border rounded-lg overflow-hidden">
                <img 
                  src={content.url} 
                  alt={content.description || 'Generated image'} 
                  className="max-w-full h-auto"
                />
                {content.description && (
                  <div className="p-2 bg-gray-50 text-sm text-gray-600">
                    {content.description}
                  </div>
                )}
              </div>
            ) : (
              <div className="p-4 bg-gray-100 rounded-lg text-gray-600">
                Image content not available
              </div>
            )}
          </div>
        );
      
      case 'data':
        return (
          <div className="mt-2">
            <div className="flex items-center gap-2 mb-2 text-sm text-gray-600">
              <BarChart3 size={16} />
              <span>Data Result</span>
            </div>
            <div className="bg-gray-50 p-3 rounded-lg">
              <pre className="text-sm overflow-x-auto">
                {JSON.stringify(content, null, 2)}
              </pre>
            </div>
          </div>
        );
      
      case 'error':
        return (
          <div className="flex items-start gap-2 text-red-700">
            <AlertCircle size={16} className="mt-0.5 flex-shrink-0" />
            <div className="whitespace-pre-wrap">
              {typeof content === 'string' ? content : JSON.stringify(content)}
            </div>
          </div>
        );
      
      default:
        return (
          <div className="whitespace-pre-wrap">
            {typeof content === 'string' ? content : JSON.stringify(content)}
          </div>
        );
    }
  };

  const getMessageClasses = () => {
    const baseClasses = "message-bubble animate-slide-up";
    
    if (message.type === 'error') {
      return `${baseClasses} message-error`;
    }
    
    if (message.type === 'system') {
      return `${baseClasses} message-system`;
    }
    
    if (isUser) {
      return `${baseClasses} message-user`;
    }
    
    return `${baseClasses} message-assistant`;
  };

  const renderToolResults = () => {
    if (!message.tool_results || message.tool_results.length === 0) {
      return null;
    }

    return (
      <div className="mt-3 pt-3 border-t border-gray-200">
        <div className="text-xs text-gray-500 mb-2">Tools used:</div>
        <div className="flex flex-wrap gap-2">
          {message.tool_results.map((result, index) => (
            <div
              key={index}
              className={`tool-indicator ${
                result.status === 'completed' ? 'tool-completed' :
                result.status === 'failed' ? 'tool-failed' :
                result.status === 'running' ? 'tool-running' :
                'tool-pending'
              }`}
            >
              <span className="font-medium">{result.tool_name}</span>
              {result.execution_time && (
                <span className="ml-1 opacity-75">
                  ({Math.round(result.execution_time * 1000)}ms)
                </span>
              )}
            </div>
          ))}
        </div>
      </div>
    );
  };

  return (
    <div className="w-full px-4 py-2">
      <div className={getMessageClasses()}>
        {/* Message header */}
        <div className="flex items-center gap-2 mb-2">
          {isUser ? (
            <User size={16} className="flex-shrink-0" />
          ) : message.type === 'system' ? (
            <div className="w-4 h-4 bg-gray-400 rounded-full flex-shrink-0" />
          ) : (
            <Bot size={16} className="flex-shrink-0" />
          )}
          
          <span className="text-sm font-medium">
            {isUser ? 'You' : message.type === 'system' ? 'System' : 'Assistant'}
          </span>
          
          <span className="text-xs opacity-75 ml-auto">
            {formatTimestamp(message.timestamp)}
          </span>
        </div>

        {/* Message content */}
        <div className="space-y-2">
          {message.content.map((contentItem, index) => (
            <div key={index}>
              {renderContent(contentItem.content, contentItem.type, contentItem.metadata)}
            </div>
          ))}
        </div>

        {/* Tool results */}
        {!isUser && renderToolResults()}

        {/* Metadata display for debugging (only in development) */}
        {process.env.NODE_ENV === 'development' && message.content[0]?.metadata && (
          <details className="mt-3 text-xs text-gray-500">
            <summary className="cursor-pointer">Debug Info</summary>
            <pre className="mt-2 p-2 bg-gray-100 rounded text-xs overflow-x-auto">
              {JSON.stringify(message.content[0].metadata, null, 2)}
            </pre>
          </details>
        )}
      </div>
    </div>
  );
};

export default MessageBubble;
