import React from "react";
import styles from "../styles/StatePanel.module.css";

export type SystemState = "OFF" | "STANDBY" | "CALIBRATE" | "READY" | "ACTIVE";

interface StatePanelProps {
  currentState: SystemState;
  onStateChange: (newState: SystemState) => void;
}

const StatePanel: React.FC<StatePanelProps> = ({ currentState, onStateChange }) => {
  return (
    <div className={styles.statePanel}>
      <h2>System State: {currentState}</h2>
      <div className={styles.buttonGroup}>
        {(["OFF", "STANDBY", "CALIBRATE", "READY", "ACTIVE"] as SystemState[]).map((state) => (
          <button
            key={state}
            onClick={() => onStateChange(state)}
            disabled={currentState === state}
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