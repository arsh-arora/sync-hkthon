import { WebSocketMessage, WebSocketService } from '../types';

// Native WebSocket implementation
class NativeWebSocketService implements WebSocketService {
  private socket: WebSocket | null = null;
  private connectionId: string = '';
  private messageCallbacks: ((message: WebSocketMessage) => void)[] = [];
  private connectCallbacks: (() => void)[] = [];
  private disconnectCallbacks: (() => void)[] = [];
  private errorCallbacks: ((error: Error) => void)[] = [];

  async connect(sessionId: string): Promise<void> {
    if (this.socket?.readyState === WebSocket.OPEN) {
      return;
    }

    this.connectionId = `${sessionId}-${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;

    return new Promise((resolve, reject) => {
      try {
        this.socket = new WebSocket(`ws://localhost:8000/api/v1/ws/${this.connectionId}`);

        this.socket.onopen = () => {
          console.log('Native WebSocket connected:', this.connectionId);
          
          // Initialize session
          this.sendRaw({
            type: 'session_init',
            data: { session_id: sessionId }
          });

          this.connectCallbacks.forEach(callback => callback());
          resolve();
        };

        this.socket.onmessage = (event) => {
          try {
            const message: WebSocketMessage = JSON.parse(event.data);
            this.messageCallbacks.forEach(callback => callback(message));
          } catch (error) {
            console.error('Failed to parse WebSocket message:', error);
          }
        };

        this.socket.onerror = (error) => {
          console.error('Native WebSocket error:', error);
          this.errorCallbacks.forEach(callback => callback(new Error('WebSocket error')));
          reject(error);
        };

        this.socket.onclose = () => {
          console.log('Native WebSocket disconnected');
          this.disconnectCallbacks.forEach(callback => callback());
        };

      } catch (error) {
        reject(error);
      }
    });
  }

  disconnect(): void {
    if (this.socket) {
      this.socket.close();
      this.socket = null;
    }
  }

  sendMessage(message: string): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    const messageData = {
      type: 'chat_message',
      data: {
        message,
        session_id: this.getSessionIdFromConnectionId(),
        user_id: 'user',
      }
    };

    this.sendRaw(messageData);
  }

  private sendRaw(data: any): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      throw new Error('WebSocket not connected');
    }

    this.socket.send(JSON.stringify(data));
  }

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
  }

  onMessage(callback: (message: WebSocketMessage) => void): void {
    this.messageCallbacks.push(callback);
  }

  onConnect(callback: () => void): void {
    this.connectCallbacks.push(callback);
  }

  onDisconnect(callback: () => void): void {
    this.disconnectCallbacks.push(callback);
  }

  onError(callback: (error: Error) => void): void {
    this.errorCallbacks.push(callback);
  }

  private getSessionIdFromConnectionId(): string {
    return this.connectionId.split('-')[0];
  }

  // Utility methods for specific message types
  requestSessionHistory(sessionId: string): void {
    this.sendRaw({
      type: 'session_history',
      data: { session_id: sessionId }
    });
  }

  sendPing(): void {
    this.sendRaw({
      type: 'ping',
      data: { timestamp: Date.now() }
    });
  }
}

// Create singleton instance
export const websocketService = new NativeWebSocketService();

// Export the native implementation as well for direct access
export const nativeWebSocketService = new NativeWebSocketService();
