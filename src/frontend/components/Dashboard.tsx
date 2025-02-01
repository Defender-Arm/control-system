"use client";
import React, { useState, useEffect } from 'react';
import StatePanel from './StatePanel';
import { WebSocketService } from '../services/websocketService';
import styles from '../styles/Dashboard.module.css';
import { SystemState } from './StatePanel';

const Dashboard: React.FC = () => {
  const [currentState, setCurrentState] = useState<SystemState>('OFF');
  const [wsService, setWsService] = useState<WebSocketService | null>(null);

  // Effect to initialize the WebSocket service
  useEffect(() => {
    const service = new WebSocketService(setCurrentState);
    setWsService(service);
    return () => {
      if (service) {
        service.close();
      }
    };
  }, []);

  // Handles state changes by sending the new state to the WebSocket service
  const handleStateChange = (newState: SystemState) => {
    wsService?.sendStateChange(newState);
  };

  return (
    <div className={styles.dashboard}>
      <StatePanel currentState={currentState} onStateChange={handleStateChange} />
    </div>
  );
};

export default Dashboard; 