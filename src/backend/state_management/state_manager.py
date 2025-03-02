from enum import IntEnum
from threading import Lock
from time import time
from typing import List, Tuple


class State(IntEnum):
    OFF = 0
    STANDBY = 1
    CALIBRATE = 2
    READY = 3
    ACTIVE = 4


MANUAL_TRANSITION_DICT = {
    State.OFF: int('11000', 2),
    State.STANDBY: int('11100', 2),
    State.CALIBRATE: int('11100', 2),
    State.READY: int('10111', 2),
    State.ACTIVE: int('10011', 2)
}


class Manager:

    def __init__(self):
        """Creates state manager. Sets standby as default state.
        """
        self._state = State.STANDBY
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

    def standby(self) -> bool:
        """If state is off, advances state to standby. Requires lock.
        :returns: Success
        """
        with self._mutex:
            if self.get_state() == State.OFF:
                self._state = State.STANDBY
                return True
            else:
                return False

    def calibrate(self) -> bool:
        """If state is standby or ready, moves state to calibrate. Requires lock.
        :returns: Success
        """
        with self._mutex:
            if self.get_state() == State.STANDBY or self.get_state() == State.READY:
                self._state = State.CALIBRATE
                return True
            else:
                return False

    def ready(self) -> bool:
        """If state is calibrate or active, advances state to ready. Requires lock.
        :returns: Success
        """
        with self._mutex:
            if self.get_state() == State.CALIBRATE or self.get_state() == State.ACTIVE:
                self._state = State.READY
                return True
            else:
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
            msgs = self.get_errors()
            if len(msgs) == 15:
                msgs.pop()
            msgs.insert(0, (time(), msg))
            # only return true if was not previously in standby
            if self.get_state() > State.STANDBY:
                self._state = State.STANDBY
                return True
            else:
                return False
