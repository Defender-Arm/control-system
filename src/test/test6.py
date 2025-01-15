import bluetooth
import time
import struct
import sys

# Replace with your device's MAC address and port
target_mac_address = "E8:9F:6D:55:15:7E"  # Example: '00:1A:7D:DA:71:13'
port = 1  # Standard port for Bluetooth RFCOMM

def recv_exactly(sock, num_bytes):
    data = b""
    while len(data) < num_bytes:
        packet = sock.recv(num_bytes - len(data))
        if not packet:
            raise ConnectionError("Connection closed by the remote device")
        data += packet
    return data

try:
    # Create a Bluetooth socket and connect to the target device
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((target_mac_address, port))
    print(f"Connected to {target_mac_address} on port {port}")

    # Send a message to the Bluetooth device
    message = "Hello, Bluetooth device!"
    sock.send(message)
    print(f"Sent message: {message}")

    stamp = time.time()
    ma = [0, 0, 0]
    count = 0
    dropped = 0
    while stamp+10>time.time():
        # Optionally, receive a response (blocking)
        # response = recv_exactly(sock, 12)
        response = sock.recv(12)
        count += 1
        try:
            a = struct.unpack("f"*(len(response)//4), response)
            a = list(a) + [0]*(3-len(response)//4)
            for i in range(0,3):
                ma[i] = max(ma[i], a[i])
            print(f"{time.time()-stamp:10.7}s ({count-dropped:5}/{count:5}): {a[0]:10.7f} ({ma[0]:10.7f}) {a[1]:10.7f} ({ma[1]:10.7f}) {a[2]:10.7f} ({ma[2]:10.7f})", end="\r")
        except:
            dropped += 1
            print(f"Dropped {len(response)}")

except bluetooth.btcommon.BluetoothError as err:
    print(f"Bluetooth connection error: {err}")

finally:
    # Always close the socket to release resources
    sock.close()
    print("\nConnection closed")
