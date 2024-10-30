# test7 wrapped by test6

import bluetooth  # pybluez
import time
import struct
import numpy as np
import matplotlib.pyplot as plt

# Replace with your device's MAC address and port
target_mac_address = "E8:9F:6D:55:15:7E"  # Example: '00:1A:7D:DA:71:13'
port = 1  # Standard port for Bluetooth RFCOMM
x_values = []
time_delta = []
ma = [0, 0, 0]
count = 0
dropped = 0

try:
    # Create a Bluetooth socket and connect to the target device
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((target_mac_address, port))
    print(f"Connected to {target_mac_address} on port {port}")

    stamp = time.time()
    # run for 10s
    while stamp+10>time.time():
        # receive 3 floats (4*3)
        response = sock.recv(12)
        count += 1
        try:
            # decode
            a = struct.unpack("f"*(len(response)//4), response)
            a = list(a) + [0]*(3-len(response)//4)  # add back zeroes
            for i in range(0,3):
                ma[i] = max(ma[i], a[i])
            print(f"{time.time()-stamp:10.7}s ({count-dropped:5}/{count:5}): {a[0]:10.7f} ({ma[0]:10.7f}) {a[1]:10.7f} ({ma[1]:10.7f}) {a[2]:10.7f} ({ma[2]:10.7f})", end="\r")
            # store
            x_values.append(a[0] if a[0]>0.1 else 0)
            time_delta.append(time.time() - stamp)
        except:
            dropped += 1
            print(f"Dropped {len(response)}")

except bluetooth.btcommon.BluetoothError as err:
    print(f"Bluetooth connection error: {err}")

finally:
    # Always close the socket to release resources
    sock.close()
    print("\nConnection closed")

# Convert lists to numpy arrays for processing
x_values = np.array(x_values)
timestamps = np.array(time_delta)

# Calculate velocity (numerical integration of acceleration)
velocity = np.cumsum(x_values * np.gradient(timestamps))

# Calculate position (numerical integration of velocity)
position = np.cumsum(velocity * np.gradient(timestamps))

# Plotting the results
plt.figure(figsize=(12, 8))

# Acceleration plot
plt.subplot(3, 1, 1)
plt.plot(timestamps, x_values, label='Acceleration (x)')
plt.xlabel("Time (seconds)")
plt.ylabel("Acceleration")
plt.title("X Acceleration over Time")
plt.legend()

# Velocity plot
plt.subplot(3, 1, 2)
plt.plot(timestamps, velocity, label='Velocity (x)', color='orange')
plt.xlabel("Time (seconds)")
plt.ylabel("Velocity")
plt.title("X Velocity over Time")
plt.legend()

# Position plot
plt.subplot(3, 1, 3)
plt.plot(timestamps, position, label='Position (x)', color='green')
plt.xlabel("Time (seconds)")
plt.ylabel("Position")
plt.title("X Position over Time")
plt.legend()

plt.tight_layout()