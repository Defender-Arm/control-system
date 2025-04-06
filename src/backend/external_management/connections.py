import cv2
from math import pi
from numpy import ndarray
import serial
from typing import List, Tuple

from src.backend.error.standby_transition import StandbyTransition
from src.backend.state_management.state_manager import State


LEFT_CAM_INDEX = 1
RIGHT_CAM_INDEX = 2
LEFT_CAM_OFFSET = (0.3, 0.0, 0.0)  # TODO m from origin
LEFT_CAM_ANGLES = (0, pi/8)  # TODO rad from origin
CAM_FOV = 70.0 * 2*pi / 360
SERIAL_PORT = 'COM4'
SERIAL_FREQ = 0.1

ARM_BASE_LENGTH = 0.268  # metres
ARM_FORE_LENGTH = 0.1665
ARM_COLLISION_LENGTH = 0.175
ARM_SWORD_LENGTH = ARM_COLLISION_LENGTH * 2


class Ext:

    def __init__(self):
        """Creates and stores all connections to external devices.
        """
        self._right_cam = None
        self._left_cam = None
        self.cam_res = [0, 0]
        self._arduino = None
        self.connect_cameras()
        self.connect_motor_control()

    def connect_cameras(self):
        """Opens connection to cameras.
        """
        self._left_cam = cv2.VideoCapture(LEFT_CAM_INDEX, cv2.CAP_DSHOW)
        self._left_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self._left_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
        self._right_cam = cv2.VideoCapture(RIGHT_CAM_INDEX, cv2.CAP_DSHOW)
        self._right_cam.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
        self._right_cam.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
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

    def connect_motor_control(self):
        """Opens connection to motor control.
        """
        if not self._arduino:
            self._arduino = serial.Serial(SERIAL_PORT, 9600, timeout=1)
        if not self._arduino.is_open:
            self._arduino.open()

    def disconnect_motor_control(self):
        """Closes connection to motor control.
        """
        if self._arduino and self._arduino.is_open:
            self._arduino.flush()
            self._arduino.close()

    def verify_connection(self):
        """Ensures all devices are connected.
        :raise StandbyTransition: At least one device is not reachable/connected.
        """
        if not self._left_cam or not self._left_cam.isOpened():
            raise StandbyTransition(f'Left camera {LEFT_CAM_INDEX} is not open')
        if not self._right_cam or not self._right_cam.isOpened():
            raise StandbyTransition(f'Right camera {RIGHT_CAM_INDEX} is not open')

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
        command = f'{state.value} {angles[0]} {angles[1]} {angles[2]}\n'
        try:
            self._arduino.flush()
            self._arduino.write(command.encode('utf-8'))
        except serial.SerialException:
            return

    def recv_serial(self):
        """Reads line from motor controller.
        :raise StandbyTransition: Error is received or unable to read from motor controller.
        """
        try:
            msg = self._arduino.readline().decode('utf-8').strip()
        except serial.SerialException:
            return
        if len(msg) == 0:
            return
        error_val = int(msg, 2)
        if error_val != 0:
            errs = []
            if error_val & 1:
                errs.append('wrist')
            if error_val >> 1 & 1:
                errs.append('elbow')
            if error_val >> 2 & 1:
                errs.append('base')
            raise StandbyTransition(f'Error from motor control at {",".join(errs)} (error code: {error_val})')
