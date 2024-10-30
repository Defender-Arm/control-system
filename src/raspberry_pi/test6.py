import bluetooth

# Replace with your device's MAC address and port
target_mac_address = "XX:XX:XX:XX:XX:XX"  # Example: '00:1A:7D:DA:71:13'
port = 1  # Standard port for Bluetooth RFCOMM

try:
    # Create a Bluetooth socket and connect to the target device
    sock = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    sock.connect((target_mac_address, port))
    print(f"Connected to {target_mac_address} on port {port}")

    # Send a message to the Bluetooth device
    message = "Hello, Bluetooth device!"
    sock.send(message)
    print(f"Sent message: {message}")

    # Optionally, receive a response (blocking)
    response = sock.recv(1024)  # Adjust buffer size if needed
    print(f"Received response: {response.decode()}")

except bluetooth.btcommon.BluetoothError as err:
    print(f"Bluetooth connection error: {err}")

finally:
    # Always close the socket to release resources
    sock.close()
    print("Connection closed")
