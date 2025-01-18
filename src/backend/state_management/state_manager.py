from enum import IntEnum
from time import time
from typing import List, Tuple


class State(IntEnum):
    OFF = 0
    STANDBY = 1
    CALIBRATE = 2
    READY = 3
    ACTIVE = 4


class Manager:

    def __init__(self):
        """Creates state manager. Sets standby as default state.
        """
        self._state = State.STANDBY
        self._msgs = []

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
        """If state is off, advances state to standby.
        :returns: Success
        """
        if self.get_state() == State.OFF:
            self._state = State.STANDBY
            return True
        else:
            return False

    def calibrate(self) -> bool:
        """If state is standby, advances state to calibrate.
        :returns: Success
        """
        if self.get_state() == State.STANDBY:
            self._state = State.CALIBRATE
            return True
        else:
            return False

    def ready(self) -> bool:
        """If state is calibrate, advances state to ready.
        :returns: Success
        """
        if self.get_state() == State.CALIBRATE:
            self._state = State.READY
            return True
        else:
            return False

    def active(self) -> bool:
        """If state is ready, advances state to active.
        :returns: Success
        """
        if self.get_state() == State.READY:
            self._state = State.ACTIVE
            return True
        else:
            return False

    def stop(self) -> bool:
        """Sets state to off.
        :returns: Success
        """
        self._state = State.OFF
        return True

    def error(self, msg: str) -> bool:
        """If state is not off, sets state to standby. Logs error messages.
        :returns: If state changed/was previous not standby but was successfully changed to standby
        """
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
