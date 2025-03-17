import cv2
import numpy as np
from time import monotonic, sleep
import serial

def find_red_stick_center_orientation(image):
    # Convert the image to HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Define red color range in HSV (red has two ranges in HSV)
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])

    # Create masks for red color
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = mask1 + mask2  # Combine both masks

    # Apply morphological operations to remove noise
    kernel = np.ones((5, 5), np.uint8)
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)

    # Find contours
    contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

    if contours:
        # Find the largest contour (assuming it's the stick)
        largest_contour = max(contours, key=cv2.contourArea)

        # Fit a rotated rectangle
        rect = cv2.minAreaRect(largest_contour)
        box = cv2.boxPoints(rect)
        box = box.astype(int)  # Convert to integer

        # Extract center and orientation
        center = (int(rect[0][0]), int(rect[0][1]))  # x, y
        angle = rect[2]  # Rotation angle

        return center, angle, box, mask
    else:
        return None, None, None, None

# Example usage with webcam
cap = cv2.VideoCapture(0)  # Open webcam
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1920)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 1080)
last = 0
half_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)) // 2
half_height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) // 2
ser = serial.Serial('COM4', 9600, timeout=1)
def send_command(base, elbow, wrist):
    command = f"{base} {elbow} {wrist}\n"
    ser.write(command.encode('utf-8'))
    print(f"Sent: {command.strip()}")
print(f'{half_width*2}x{half_height*2}')
while True:
    ret, frame = cap.read()
    if not ret:
        break

    center, angle, box, mask = find_red_stick_center_orientation(frame)

    if center:
        # Draw bounding box
        cv2.drawContours(mask, [box], 0, (0, 255, 0), 2)

        # Draw center point
        cv2.circle(mask, center, 5, (255, 0, 0), -1)

        # Display angle
        cv2.putText(mask, f"Angle: {int(angle)} deg", (center[0] + 10, center[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

    cv2.imshow("Frame", mask)

    if last + 0.5 < monotonic():
        last = monotonic()
        target_x = (center[0] - half_width) / half_width * 60
        target_y = (center[1] - half_height) / half_height * 45
        if target_x < -60:
            print(f'target_x increased from {target_x} to -60')
            target_x = -60
        if target_x > 60:
            print(f'target_x decreased from {target_x} to 60')
            target_x = 60
        if target_y < -45:
            print(f'target_y increased from {target_y} to -45')
            target_x = -45
        if target_x > 45:
            print(f'target_y decreased from {target_y} to 45')
            target_x = 45
        print(f'target is {int(target_x)} {-int(target_y)}')
        target_wr = angle
        if abs(target_wr) > 90:
            print(f'target_wr changed from {target_wr} to 90')
            target_wr = 90
        send_command(int(target_x), -int(target_y), int(target_wr))

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()
send_command(0,0,0)
sleep(3)
ser.close()
