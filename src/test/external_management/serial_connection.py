import serial
import serial.tools.list_ports
import time

PORT = 'COM4'
BAUD_RATE = 115200


def check_for_port(port: str):
    ports = [p.name for p in list(serial.tools.list_ports.comports())]
    return port in ports


def send_command(state, base, elbow, wrist):
    try:
        command = f"{state} {base} {elbow} {wrist}\n"
        ser.flush()  # Clear the buffer before sending
        ser.write(command.encode('utf-8'))
        print(f"Sent: {command.strip()}")

        # Wait for acknowledgment
        ack = ser.readline().decode('utf-8').strip()
        ack_int = int(ack, 2)
        print(f"Received: {ack} / {ack_int}")
        if ack_int != 0:
            print(f"Warning: Unexpected response from Arduino: {ack}")
        time.sleep(0.1)  # Small delay
    except:
        print("Serial timeout, resetting connection...")
        ser.close()
        time.sleep(1)
        ser.open()


# RUN =============================================================
if not check_for_port(PORT):
    print(f'{PORT} not present')
    exit()
ser = serial.Serial(PORT, BAUD_RATE, timeout=1)

time.sleep(2)

while check_for_port(PORT):
    send_command(1, 0, 0, 0)
    time.sleep(0.5)

ser.close()
print(ser.is_open)
