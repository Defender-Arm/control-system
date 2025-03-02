"use client";
import React, { useState } from "react";
import styles from "../styles/StatePanel.module.css";

export type SystemState = "OFF" | "STANDBY" | "CALIBRATE" | "READY" | "ACTIVE";
export type StateNumber = 0 | 1 | 2 | 3 | 4;

interface StatePanelProps {
  currentState: SystemState;
  onStateChange: (newState: SystemState) => void;
}

const stateToNumber: Record<SystemState, StateNumber> = {
  "OFF": 0,
  "STANDBY": 1,
  "CALIBRATE": 2,
  "READY": 3,
  "ACTIVE": 4
};

const StatePanel: React.FC<StatePanelProps> = ({ currentState, onStateChange }) => {
  const [lastStateChange, setLastStateChange] = useState<Date>(new Date());
  const [error, setError] = useState<string | null>(null);

  const isValidTransition = (current: SystemState, next: SystemState): boolean => {
    const currentNum = stateToNumber[current];
    const nextNum = stateToNumber[next];

    // Prevent user from transitioning CALIBRATE -> READY
    if (current === "CALIBRATE" && next === "READY") return false;

    // Allow decreasing to any lower state
    if (nextNum < currentNum) return true;

    // For increasing, must go in sequence
    return nextNum === currentNum + 1;
  };

  const handleStateChange = (newState: SystemState) => {
    if (!isValidTransition(currentState, newState)) {
      setError(`Invalid transition from ${currentState} to ${newState}`);
      return;
    }
    setError(null);
    setLastStateChange(new Date());
    onStateChange(newState);
  };

  return (
    <div className={styles.statePanel}>
      <h2 className={styles.heading}>System State: {currentState}</h2>
      {error && <div className={styles.error}>{error}</div>}
      <div className={styles.timestamp}>
        Last changed: {lastStateChange.toLocaleTimeString()}
      </div>
      <div className={styles.buttonGroup}>
        {(["OFF", "STANDBY", "CALIBRATE", "READY", "ACTIVE"] as SystemState[]).map((state) => (
          <button
            key={state}
            onClick={() => handleStateChange(state)}
            disabled={currentState === state || !isValidTransition(currentState, state)}
            className={`${styles.button} ${styles[state.toLowerCase()]}`}
          >
            {state}
          </button>
        ))}
      </div>
    </div>
  );
};

export default StatePanel;