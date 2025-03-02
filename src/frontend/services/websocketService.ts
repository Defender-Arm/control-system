// WebSocket service for handling state updates from the backend - STATE MANAGEMENT ONLY RN
import { SystemState } from '../components/StatePanel';

export class WebSocketService {
  private ws: WebSocket;
  private stateCallback: (state: SystemState) => void;

  // Constructor for the WebSocketService
  constructor(onStateChange: (state: SystemState) => void) {
    this.stateCallback = onStateChange;
    this.ws = new WebSocket('ws://localhost:8000/ws');
    this.setupWebSocket();
  }

  // Sets up the WebSocket connection and event listeners
  private setupWebSocket() {
    this.ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      if (data.type === 'state_update') {
        this.stateCallback(data.state as SystemState);
      }
    };

    this.ws.onclose = () => {
      setTimeout(() => {
        this.ws = new WebSocket('ws://localhost:8000/ws');
        this.setupWebSocket();
      }, 1000);
    };
  }

  // Sends a state change to the backend
  sendStateChange(newState: SystemState) {
    if (this.ws.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({
        type: 'state_change',
        state: newState
      }));
    }
  }

  public close() {
    if (this.ws) {
      this.ws.close();
    }
  }
}