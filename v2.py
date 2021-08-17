import math
import cv2
import numpy as np
import pyautogui
import HandTrakingModule as htm
import time
from pynput.keyboard import Key, Controller
import pyttsx3

engine = pyttsx3.init()  # text to speech
keyboard = Controller()  # keyboard controller

# ######################### capture video
wCam, hCam = 640, 480
cap = cv2.VideoCapture(0)
cap.set(3, wCam)
cap.set(4, hCam)
cap.set(10, 100)

# ######################### screen size
wScr, hScr = pyautogui.size()
detector = htm.handDetector(maxHands=1)
pTime = 0

# ####################### Frame Reduction
frameR = 100
smoothening = 7
plocX, plocY = 0, 0
clocX, clocY = 0, 0

# ######################## output
engine.say("Heyyy! , Virtual Mouse here.")
engine.runAndWait()

while True:
    success, img = cap.read()
    # 1.  ======================================== find landmark
    img = detector.findHands(img, draw=True)
    lmList = detector.findPosition(img)
    # 2.  ========================================= find position
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        x3, y3 = lmList[4][1:]  # for thumb
        # 3. ======================================= Check finger
        tipIds = [4, 8, 12, 16, 20]
        fingers = []
        # Thumb
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)

        # ======== check Fingers are up
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)
        # print(fingers)
        # ============================================ frame redution
        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)
        # ===================================== all function =================================================

        # 5.  ====================================== Volume controller

        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            cx3, cy3 = (x1 + x3) // 2, (y1 + y3) // 2
            r, t = 9, 2
            if True:
                cv2.line(img, (x3, y3), (x1, y1), (255, 0, 255), t)
                cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (x3, y3), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (cx3, cy3), r, (0, 0, 255), cv2.FILLED)
                length = math.hypot(x3 - x1, y3 - y1)

                if length < 100:
                    cv2.circle(img, (cx3, cy3), 10, (0, 255, 0), cv2.FILLED)
                    keyboard.press(Key.media_volume_up)
                    keyboard.release(Key.media_volume_up)
                    time.sleep(0.1)
                if length > 100:
                    cv2.circle(img, (cx3, cy3), 10, (0, 0, 0), cv2.FILLED)
                    keyboard.press(Key.media_volume_down)
                    keyboard.release(Key.media_volume_down)
                    time.sleep(0.1)
        # 5.  ====================================== Mouses  is  moving
        if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 0:
            # 6. ===================================Convert Coordinates
            x3 = np.interp(x1, (frameR, wCam - frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam - frameR), (0, hScr))

            # 7. ===================================Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
            # 8. ===================================== Move Mouse
            pyautogui.moveTo(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 10, (0, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY
            # 9. ===================================== Click  Mouse
        if fingers[1] == 1 and fingers[2] == 1:
            cx, cy = (x1 + x2) // 2, (y1 + y2) // 2
            r, t = 9, 2
            if True:
                cv2.line(img, (x1, y1), (x2, y2), (255, 0, 255), t)
                cv2.circle(img, (x1, y1), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (x2, y2), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (cx, cy), r, (0, 0, 255), cv2.FILLED)
                length = math.hypot(x2 - x1, y2 - y1)
                if length < 40:
                    cv2.circle(img, (cx, cy), 10, (0, 255, 0), cv2.FILLED)
                    pyautogui.rightClick()
        # 10. ===================================== scroll   Mouse

        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            pyautogui.scroll(-1.5)
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 1:
            pyautogui.scroll(2)
        # 11. ===================================== doubleclick   Mouse
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
            pyautogui.doubleClick()

    # ===================================== all function =================================================

    # ######################### Framerate
    cTime = time.time()
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, f'FPS:{int(fps)}', (40, 50), cv2.FONT_HERSHEY_COMPLEX, 1, (255, 0, 0), 3)
    # ######################### Framerate

    cv2.imshow('Ans', img)
    cv2.waitKey(1)
