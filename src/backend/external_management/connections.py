import cv2
from math import pi
from numpy import ndarray
import serial
import serial.tools.list_ports
from time import sleep
from typing import List, Tuple

from src.backend.error.standby_transition import StandbyTransition
from src.backend.state_management.state_manager import State


LEFT_CAM_INDEX = 1
RIGHT_CAM_INDEX = 2
LEFT_CAM_OFFSET = (0.3, 0.0, 0.0)  # TODO m from origin
LEFT_CAM_ANGLES = (0, pi/8)  # TODO rad from origin
CAM_FOV = 70.0 * 2*pi / 360
SERIAL_PORT = 'COM4'
SERIAL_BAUD_RATE = 115200

ARM_BASE_LENGTH = 0.268  # metres
ARM_FORE_LENGTH = 0.1665
ARM_COLLISION_LENGTH = 0.175
ARM_SWORD_LENGTH = ARM_COLLISION_LENGTH * 2


def is_arduino_connected() -> bool:
    """Checks COM ports to ensure arduino is connected.
    :return: True if port is present
    """
    return SERIAL_PORT in [port.name for port in list(serial.tools.list_ports.comports())]


class Ext:

    def __init__(self, ignore_motors: bool = False):
        """Creates and stores all connections to external devices.
        """
        self._right_cam = None
        self._left_cam = None
        self.cam_res = [0, 0]
        self._arduino = None
        self.connect_cameras()
        self.ignore_motors = ignore_motors
        if not self.ignore_motors:
            self.connect_arduino()

    def connect_cameras(self):
        """Opens connection to cameras.
        """
        self._left_cam = cv2.VideoCapture(LEFT_CAM_INDEX, cv2.CAP_DSHOW)
        self._right_cam = cv2.VideoCapture(RIGHT_CAM_INDEX, cv2.CAP_DSHOW)
        self.cam_res = (self._left_cam.get(cv2.CAP_PROP_FRAME_WIDTH),
                        self._left_cam.get(cv2.CAP_PROP_FRAME_HEIGHT))

    def disconnect_cameras(self):
        """Releases captures.
        """
        if self._left_cam:
            self._left_cam.release()
        if self._right_cam:
            self._right_cam.release()

    def swap_cameras(self):
        """Switches the "left" camera and the "right" camera in code.
        """
        self._left_cam, self._right_cam = self._right_cam, self._left_cam

    def connect_arduino(self):
        """Opens connection to motor control.
        """
        if self.ignore_motors:
            return
        self._arduino = serial.Serial(SERIAL_PORT, SERIAL_BAUD_RATE, timeout=1)
        sleep(2)

    def disconnect_arduino(self):
        """Closes connection to motor control.
        """
        if self.ignore_motors:
            return
        if self._arduino:
            self._arduino.close()

    def verify_connection(self):
        """Ensures all devices are connected.
        :raise StandbyTransition: At least one device is not reachable/connected.
        """
        if not self._left_cam or not self._left_cam.isOpened():
            raise StandbyTransition(f'Left camera {LEFT_CAM_INDEX} is not open')
        if not self._right_cam or not self._right_cam.isOpened():
            raise StandbyTransition(f'Right camera {RIGHT_CAM_INDEX} is not open')
        if not self.ignore_motors and (not self._arduino or not is_arduino_connected()):
            raise StandbyTransition(f'Arduino is not connected')

    def take_photos(self) -> Tuple[ndarray, ndarray]:
        """Gets snapshot from both cameras.
        :return: Arm's left camera image, then arm's right camera image. Image is ``None`` if camera cannot be reached.
        """
        ret, frame_l = self._left_cam.read()
        if not ret:
            raise StandbyTransition(f'Left camera {LEFT_CAM_INDEX} failed to read')
        ret, frame_r = self._right_cam.read()
        if not ret:
            raise StandbyTransition(f'Right camera {RIGHT_CAM_INDEX} failed to read')
        return frame_l, frame_r

    def arm_angles(self) -> Tuple[float, float, float]:
        """Gets angles of all arm joints, from base to end effector.
        :return: Base angle, then "elbow" angle, then "wrist" angle. Angle is ``None`` if sensor cannot be reached.
        """
        raise NotImplementedError

    def send_serial(self, state: State, angles: List[int] = (0, 0, 0)) -> None:
        """Sends state and target angles for arm to motor control.
        """
        if self.ignore_motors:
            return
        command = f'{state.value} {angles[0]} {angles[1]} {angles[2]}\n'
        try:
            self._arduino.flush()
            self._arduino.write(command.encode('utf-8'))
        except serial.serialutil.SerialException:
            raise StandbyTransition(f'Error sending message "{command.strip()}" over serial')

    def recv_serial(self):
        """Reads line from motor controller.
        :raise StandbyTransition: Error is received or unable to read from motor controller.
        """
        if self.ignore_motors:
            return
        try:
            msg = self._arduino.readline().decode('utf-8').strip()
        except serial.serialutil.SerialException:
            raise StandbyTransition(f'Error reading serial')
        error_val = int(msg, 2)
        if error_val != 0:
            raise StandbyTransition(f'Serial indicated error (error code: {error_val})')
