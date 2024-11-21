from bluetooth import RFCOMM, BluetoothSocket
from logging import getLogger
from struct import unpack
from time import monotonic

from ..const import TARGET_MAC_ADDRESS, TARGET_PORT
from ..handler.handler import Handler
from connection import Connection


class ConnectionFromLinux(Connection):

    run_time = 0

    def __init__(
            self,
            handler: Handler,
            run_time: int = 999999
    ):
        self.logger = getLogger(__name__)
        self.handler = handler
        self.run_time = run_time

    def connect(self):
        sock = BluetoothSocket(RFCOMM)
        try:
            # connect to ESP32
            sock.connect((TARGET_MAC_ADDRESS, TARGET_PORT))
            self.logger.debug(f"Connected to {TARGET_MAC_ADDRESS} on port {TARGET_PORT}")
            start_time = monotonic()
            while start_time + self.run_time > monotonic():
                # receive 3 floats (4*3)
                response = sock.recv(12)
                try:
                    # decode; if some floats are zeroes, `response`
                    # is smaller. Read based on size and add back zeroes.
                    floats_received = len(response) // 4
                    acc = unpack("f" * floats_received, response)
                    acc = list(acc) + [0.0] * (3 - floats_received)
                    # send measurement to handler
                    self.handler.step(acc)
                except Exception as err:
                    self.logger.warning(f"Dropped; {err}")
        except Exception as err:
            self.logger.warning(f"Bluetooth connection error: {err}")
        finally:
            # Always close the socket to release resources
            sock.close()
            print("\n")
            self.logger.info("Connection closed")
