import cv2
import numpy as np

def nothing(x):
    pass

# Create a window
cv2.namedWindow('Red Mask Adjuster')

# Create trackbars for lower mask
cv2.createTrackbar('Lower H', 'Red Mask Adjuster', 0, 179, nothing)
cv2.createTrackbar('Lower S', 'Red Mask Adjuster', 120, 255, nothing)
cv2.createTrackbar('Lower V', 'Red Mask Adjuster', 70, 255, nothing)

# Create trackbars for upper mask
cv2.createTrackbar('Upper H', 'Red Mask Adjuster', 10, 179, nothing)
cv2.createTrackbar('Upper S', 'Red Mask Adjuster', 255, 255, nothing)
cv2.createTrackbar('Upper V', 'Red Mask Adjuster', 255, 255, nothing)

def mask_red_color(frame):
    lower_h = cv2.getTrackbarPos('Lower H', 'Red Mask Adjuster')
    lower_s = cv2.getTrackbarPos('Lower S', 'Red Mask Adjuster')
    lower_v = cv2.getTrackbarPos('Lower V', 'Red Mask Adjuster')

    upper_h = cv2.getTrackbarPos('Upper H', 'Red Mask Adjuster')
    upper_s = cv2.getTrackbarPos('Upper S', 'Red Mask Adjuster')
    upper_v = cv2.getTrackbarPos('Upper V', 'Red Mask Adjuster')

    lower_red = np.array([lower_h, lower_s, lower_v])
    upper_red = np.array([upper_h, upper_s, upper_v])

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower_red, upper_red)
    
    red_only_frame = cv2.bitwise_and(frame, frame, mask=mask)

    return red_only_frame

cap = cv2.VideoCapture(0)  # 0 is typically the default camera

while True:
    # Capture frame-by-frame
    ret, frame = cap.read()
    if not ret:
        print("Failed to grab frame")
        break

    red_only_frame = mask_red_color(frame)

    cv2.imshow('Red Masked Frame', red_only_frame)

    # Break the loop when 'q' is pressed
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()