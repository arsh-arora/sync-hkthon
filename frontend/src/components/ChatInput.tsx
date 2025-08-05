import React, { useState, useRef, useEffect } from 'react';
import { Send, Loader2 } from 'lucide-react';
import { ChatInputProps } from '../types';

const ChatInput: React.FC<ChatInputProps> = ({ 
  onSendMessage, 
  disabled = false, 
  placeholder = "Type your message..." 
}) => {
  const [message, setMessage] = useState('');
  const [isComposing, setIsComposing] = useState(false);
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  // Auto-resize textarea
  useEffect(() => {
    const textarea = textareaRef.current;
    if (textarea) {
      textarea.style.height = 'auto';
      textarea.style.height = `${Math.min(textarea.scrollHeight, 120)}px`;
    }
  }, [message]);

  // Focus on mount
  useEffect(() => {
    if (textareaRef.current && !disabled) {
      textareaRef.current.focus();
    }
  }, [disabled]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (message.trim() && !disabled && !isComposing) {
      onSendMessage(message.trim());
      setMessage('');
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey && !isComposing) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleCompositionStart = () => {
    setIsComposing(true);
  };

  const handleCompositionEnd = () => {
    setIsComposing(false);
  };

  return (
    <div className="border-t bg-white p-4 safe-area-inset">
      <form onSubmit={handleSubmit} className="max-w-4xl mx-auto">
        <div className="flex gap-3 items-end">
          <div className="flex-1 relative">
            <textarea
              ref={textareaRef}
              value={message}
              onChange={(e) => setMessage(e.target.value)}
              onKeyDown={handleKeyDown}
              onCompositionStart={handleCompositionStart}
              onCompositionEnd={handleCompositionEnd}
              placeholder={placeholder}
              disabled={disabled}
              className="chat-input min-h-[44px] max-h-[120px] resize-none"
              rows={1}
            />
            
            {/* Character count (optional) */}
            {message.length > 500 && (
              <div className="absolute -top-6 right-0 text-xs text-gray-500">
                {message.length}/2000
              </div>
            )}
          </div>
          
          <button
            type="submit"
            disabled={disabled || !message.trim() || isComposing}
            className="btn-primary flex items-center gap-2 px-4 py-3 min-w-[80px] justify-center"
          >
            {disabled ? (
              <>
                <Loader2 size={16} className="animate-spin" />
                <span className="hidden sm:inline">Sending</span>
              </>
            ) : (
              <>
                <Send size={16} />
                <span className="hidden sm:inline">Send</span>
              </>
            )}
          </button>
        </div>
        
        {/* Help text */}
        <div className="mt-2 text-xs text-gray-500 text-center">
          Press Enter to send, Shift+Enter for new line
        </div>
      </form>
    </div>
  );
};

export default ChatInput;
