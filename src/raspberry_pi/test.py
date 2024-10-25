from IOBluetooth import IOBluetoothRFCOMMChannel

# Set up Bluetooth server
server_sock = IOBluetoothRFCOMMChannel()
port = 1
server_sock.bind("", port)
server_sock.listen(1)

print("Waiting for connection...")
client_sock, client_info = server_sock.accept()
print("Accepted connection from", client_info)

# Receive data
data = client_sock.read(1024)