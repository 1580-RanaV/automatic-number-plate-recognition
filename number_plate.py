import cv2
import os
import time
import numpy as np

harcascade = "model/haarcascade_russian_plate_number.xml"

if not os.path.exists(harcascade):
    print(f"Error: The Haar Cascade file '{harcascade}' does not exist.")
    exit()

cap = cv2.VideoCapture(0)
cap.set(3, 640)
cap.set(4, 480)

min_area = 500
count = 0
last_saved_time = time.time()
save_interval = 2
previous_plate = None

def plates_are_similar(img1, img2, threshold=0.9):
    if img1 is None or img2 is None:
        return False

    if img1.shape != img2.shape:
        return False

    diff = cv2.absdiff(img1, img2)
    non_zero_count = np.count_nonzero(diff)
    total_count = img1.size
    similarity = 1 - (non_zero_count / total_count)

    return similarity >= threshold

while True:
    success, img = cap.read()

    if not success:
        print("Failed to capture image")
        break

    plate_cascade = cv2.CascadeClassifier(harcascade)
    img_gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    plates = plate_cascade.detectMultiScale(img_gray, 1.1, 4)

    for (x, y, w, h) in plates:
        area = w * h

        if area > min_area:
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 255, 0), 2)
            cv2.putText(img, "Number Plate", (x, y - 5), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, (255, 0, 255), 2)

            img_roi = img[y: y + h, x: x + w]

            current_time = time.time()
            if current_time - last_saved_time >= save_interval:
                if not os.path.exists("plates"):
                    os.makedirs("plates")
                
                if previous_plate is None or not plates_are_similar(previous_plate, img_roi):
                    cv2.imwrite(f"plates/scanned_img_{count}.jpg", img_roi)
                    cv2.rectangle(img, (0, 200), (640, 300), (0, 255, 0), cv2.FILLED)
                    cv2.putText(img, "Plate Saved", (150, 265), cv2.FONT_HERSHEY_COMPLEX_SMALL, 2, (0, 0, 255), 2)
                    cv2.imshow("Result", img)
                    last_saved_time = current_time
                    count += 1
                    previous_plate = img_roi

    cv2.imshow("Result", img)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
