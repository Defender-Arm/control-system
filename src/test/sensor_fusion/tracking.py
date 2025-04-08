import cv2
import numpy as np

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
cap = cv2.VideoCapture(1, cv2.CAP_DSHOW)  # Open webcam
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 20)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 20)
while True:
    ret, frame = cap.read()
    if not ret:
        break

    center, angle, box, mask_frame = find_red_stick_center_orientation(frame)

    if center:
        # Draw bounding box
        cv2.drawContours(frame, [box], 0, (0, 255, 0), 2)

        # Draw center point
        cv2.circle(frame, center, 5, (255, 0, 0), -1)

        # Display angle
        cv2.putText(frame, f"Angle: {int(angle)} deg", (center[0] + 10, center[1] - 10),
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 2)

        cv2.imshow("Frame", mask_frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):  # Press 'q' to exit
        break

cap.release()
cv2.destroyAllWindows()
