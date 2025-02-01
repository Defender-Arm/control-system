"use client";
import React, { useState } from 'react';
import StatePanel from './StatePanel';
import styles from '../styles/Dashboard.module.css';
import { SystemState } from './StatePanel';

const Dashboard: React.FC = () => {
  const [currentState, setCurrentState] = useState<SystemState>('OFF');

  return (
    <div className={styles.dashboard}>
      <StatePanel currentState={currentState} onStateChange={setCurrentState} />
    </div>
  );
};

export default Dashboard; 