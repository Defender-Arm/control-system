import serial
import struct
import time
import matplotlib.pyplot as plt
import numpy as np

# Parameters
esp32_port = "COM10"  # Replace with correct COM port
baud_rate = 115200
data_duration = 10  # seconds of data to collect

# Open serial connection
ser = serial.Serial(esp32_port, baud_rate, timeout=1)
time.sleep(2)
print("Connected to ESP32. Receiving data...")

# Variables for data storage
x_values = []
timestamps = []
start_time = time.time()
last_print_time = start_time

try:
    while True:
        if ser.in_waiting >= 12:
            data = ser.read(12)  # Read 12 bytes (3 floats)
            x, y, z = struct.unpack('fff', data)  # Unpack the data
            # print(x,y,z)

            # Calculate time since start
            current_time = time.time()
            delta_t = current_time - start_time
            if abs(x) < 0.2:
                x = 0
            x_values.append(x)
            timestamps.append(delta_t)

            # Print elapsed time every second
            if current_time - last_print_time >= 1:
                print(f"Time elapsed: {int(delta_t)} seconds")
                last_print_time = current_time

            if delta_t >= data_duration:
                break

except KeyboardInterrupt:
    print("Data streaming stopped manually.")
finally:
    ser.close()
# Convert lists to numpy arrays for processing
x_values = np.array(x_values)
timestamps = np.array(timestamps)

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
plt.show()
