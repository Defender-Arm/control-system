# FastAPI setup with CORS middleware to allow frontend connections
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from typing import List, Tuple
import json
from enum import IntEnum
from threading import Lock
from time import time

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

class Manager:
    def __init__(self):
        """Creates state manager. Sets OFF as default state.
        """
        self._state = State.OFF
        self._msgs = []
        self._mutex = Lock()

    def get_state(self) -> State:
        """Gets current system state.
        :return: State enum
        """
        return self._state

    def get_errors(self) -> List[Tuple[float, str]]:
        """Returns list of last 15 errors and the time they happened.
        :returns: List of (``timestamp``, ``msg``)"""
        return self._msgs

    async def broadcast_state(self):
        """Broadcasts current state to all connected WebSocket clients"""
        message = json.dumps({
            "type": "state_update",
            "state": self._state.name
        })
        for client in connected_clients:
            try:
                await client.send_text(message)
            except:
                connected_clients.remove(client)

    def standby(self) -> bool:
        """If state is off, advances state to standby. Requires lock.
        :returns: Success
        """
        with self._mutex:
            if self.get_state() == State.OFF:
                self._state = State.STANDBY
                return True
            else:
                self._msgs.append((time(), f"Invalid transition from {self._state.name} to STANDBY"))
                if len(self._msgs) > 15:
                    self._msgs.pop(0)
                return False

    def calibrate(self) -> bool:
        """If state is standby, advances state to calibrate. Requires lock.
        :returns: Success
        """
        with self._mutex:
            if self.get_state() == State.STANDBY:
                self._state = State.CALIBRATE
                return True
            else:
                self._msgs.append((time(), f"Invalid transition from {self._state.name} to CALIBRATE"))
                if len(self._msgs) > 15:
                    self._msgs.pop(0)
                return False

    def ready(self) -> bool:
        """If state is calibrate, advances state to ready. Requires lock.
        :returns: Success
        """
        with self._mutex:
            if self.get_state() == State.CALIBRATE:
                self._state = State.READY
                return True
            else:
                self._msgs.append((time(), f"Invalid transition from {self._state.name} to READY"))
                if len(self._msgs) > 15:
                    self._msgs.pop(0)
                return False

    def active(self) -> bool:
        """If state is ready, advances state to active. Requires lock.
        :returns: Success
        """
        with self._mutex:
            if self.get_state() == State.READY:
                self._state = State.ACTIVE
                return True
            else:
                self._msgs.append((time(), f"Invalid transition from {self._state.name} to ACTIVE"))
                if len(self._msgs) > 15:
                    self._msgs.pop(0)
                return False

    def stop(self) -> bool:
        """Sets state to off. Requires lock.
        :returns: Success
        """
        with self._mutex:
            self._state = State.OFF
            return True

    def error(self, msg: str) -> bool:
        """If state is not off, sets state to standby. Logs error messages. Requires lock.
        :returns: If state changed/was previous not standby but was successfully changed to standby
        """
        with self._mutex:
            # only keep latest 15 error messages
            if len(self._msgs) == 15:
                self._msgs.pop()
            self._msgs.insert(0, (time(), msg))
            # only return true if was not previously in standby
            if self.get_state() > State.STANDBY:
                self._state = State.STANDBY
                return True
            else:
                return False

state_manager = Manager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.append(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            message = json.loads(data)
            if message["type"] == "state_change":
                new_state = message["state"]
                success = False
                
                if new_state == "STANDBY":
                    success = state_manager.standby()
                elif new_state == "CALIBRATE":
                    success = state_manager.calibrate()
                elif new_state == "READY":
                    success = state_manager.ready()
                elif new_state == "ACTIVE":
                    success = state_manager.active()
                elif new_state == "OFF":
                    success = state_manager.stop()
                
                if success:
                    await state_manager.broadcast_state()
    except:
        connected_clients.remove(websocket)

@app.get("/api/state")
async def get_state():
    return {"state": state_manager.get_state().name}

@app.post("/api/state")
async def set_state(state_data: dict):
    new_state = state_data["state"]
    success = False
    
    if new_state == "STANDBY":
        success = state_manager.standby()
    elif new_state == "CALIBRATE":
        success = state_manager.calibrate()
    elif new_state == "READY":
        success = state_manager.ready()
    elif new_state == "ACTIVE":
        success = state_manager.active()
    elif new_state == "OFF":
        success = state_manager.stop()
        
    if not success:
        raise HTTPException(status_code=400, detail="Invalid state transition")
    await state_manager.broadcast_state()
    return {"state": state_manager.get_state().name}

@app.get("/api/errors")
async def get_errors():
    return {"errors": state_manager.get_errors()}