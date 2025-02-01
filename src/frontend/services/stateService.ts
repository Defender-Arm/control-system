import axios from 'axios';
import { SystemState } from '../components/StatePanel';

export class StateService {
  private baseUrl = 'http://localhost:5000/api'; // or your backend URL

  async getCurrentState() {
    const response = await axios.get(`${this.baseUrl}/state`);
    return response.data.state;
  }

  async updateState(newState: SystemState) {
    const response = await axios.post(`${this.baseUrl}/state`, { state: newState });
    return response.data;
  }

  async getErrors() {
    const response = await axios.get(`${this.baseUrl}/errors`);
    return response.data.errors;
  }
} 