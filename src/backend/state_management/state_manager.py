# FastAPI setup with CORS middleware to allow frontend connections
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List
import json
from enum import IntEnum
from threading import Lock
import time

app = FastAPI()

# Add CORS middleware - allows frontend to connect to backend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # localhost:3000 is the frontend URL for now
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# State enumeration defining valid system states in order
class State(IntEnum):
    OFF = 0
    STANDBY = 1
    CALIBRATE = 2
    READY = 3
    ACTIVE = 4

connected_clients: List[WebSocket] = []

# StateManager class handling state transitions and WebSocket broadcasts
class StateManager:
    def __init__(self):
        self.current_state = State.OFF
        self.error_messages = []
        self._lock = Lock()

    # Broadcasts the current state to all connected clients
    async def broadcast_state(self):
        message = json.dumps({
            "type": "state_update",
            "state": self.current_state.name
        })
        for client in connected_clients:
            try:
                await client.send_text(message)
            except:
                connected_clients.remove(client)

    # Updates the current state and validates transitions
    async def update_state(self, new_state: str) -> bool:
        with self._lock:
            try:
                new_state_enum = State[new_state]
                current_state_num = int(self.current_state)
                new_state_num = int(new_state_enum)

                # Allow decreasing to any lower state
                if new_state_num < current_state_num:
                    self.current_state = new_state_enum
                    await self.broadcast_state()
                    return True

                # For increasing states, must go in sequence
                if new_state_num == current_state_num + 1:
                    self.current_state = new_state_enum
                    await self.broadcast_state()
                    return True

                # Invalid transition
                error_msg = f"Invalid state transition from {self.current_state.name} to {new_state}"
                self.error_messages.append((time.time(), error_msg))
                if len(self.error_messages) > 15:
                    self.error_messages.pop(0)
                return False

            except KeyError:
                error_msg = f"Invalid state: {new_state}"
                self.error_messages.append((time.time(), error_msg))
                return False

state_manager = StateManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message["type"] == "state_change":
                await state_manager.update_state(message["state"])
    except:
        connected_clients.remove(websocket)

@app.get("/api/state")
async def get_state():
    return {"state": state_manager.current_state.name}

@app.post("/api/state")
async def set_state(state_data: dict):
    success = await state_manager.update_state(state_data["state"])
    if not success:
        raise HTTPException(status_code=400, message="Invalid state transition")
    return {"state": state_manager.current_state.name}

@app.get("/api/errors")
async def get_errors():
    return {"errors": state_manager.error_messages}
