import cv2
import math
import pyautogui
import numpy as np
import HandTrackingModule as htm
import time
import autopy
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume

##########################
wCam, hCam = 640, 480
frameR = 100  # Frame Reduction
smoothening = 7
#########################

pTime = 0
plocX, plocY = 0, 0
clocX, clocY = 0, 0
cap = cv2.VideoCapture(0)

cap.set(3, wCam)
cap.set(4, hCam)
detector = htm.handDetector(maxHands=1)
detector = htm.handDetector(detectionCon=0.7)

devices = AudioUtilities.GetSpeakers()
interface = devices.Activate(IAudioEndpointVolume._iid_, CLSCTX_ALL, None)
volume = cast(interface, POINTER(IAudioEndpointVolume))
# volume.GetMute()
# volume.GetMasterVolumeLevel()
volRange = volume.GetVolumeRange()
minVol = volRange[0]
maxVol = volRange[1]
vol = 0
volBar = 400
volPer = 0


wScr, hScr = autopy.screen.size()
#print(wScr, hScr)

while True:
    # 1. Find hand Landmarks
    success, img = cap.read()
    img = detector.findHands(img)
    lmList, bbox = detector.findPosition(img, draw=False) #false nikal

    # 2. Get the tip of the index and middle fingers
    if len(lmList) != 0:
        x1, y1 = lmList[8][1:]
        x2, y2 = lmList[12][1:]
        #x3, y3 = lmList[4][1:]
        x4, y4 = lmList[4][1], lmList[4][2]
        x5, y5 = lmList[8][1], lmList[8][2]

        tipIds = [4, 8, 12, 16, 20]
        fingers = []
       # print(x1, y1, x2, y2)

    # 3. Check which fingers are up
        fingers = detector.fingersUp()
        if lmList[tipIds[0]][1] > lmList[tipIds[0] - 1][1]:
            fingers.append(1)
        else:
            fingers.append(0)
        #print(fingers)
        for id in range(1, 5):
            if lmList[tipIds[id]][2] < lmList[tipIds[id] - 2][2]:
                fingers.append(1)
            else:
                fingers.append(0)

        cv2.rectangle(img, (frameR, frameR), (wCam - frameR, hCam - frameR),
                      (255, 0, 255), 2)


        # 4. Only Index Finger : Moving Mode
        if fingers[1] == 1 and fingers[2] == 0 and fingers[0] == 0:
        # 5. Convert Coordinates

            x3 = np.interp(x1, (frameR, wCam-frameR), (0, wScr))
            y3 = np.interp(y1, (frameR, hCam-frameR), (0, hScr))
        # 6. Smoothen Values
            clocX = plocX + (x3 - plocX) / smoothening
            clocY = plocY + (y3 - plocY) / smoothening
    # 7. Move Mouse
            autopy.mouse.move(wScr - clocX, clocY)
            cv2.circle(img, (x1, y1), 15, (255, 0, 255), cv2.FILLED)
            plocX, plocY = clocX, clocY
##########################################################################################

    # 8. Both Index and middle fingers are up : Clicking Mode
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 0 and fingers[4] == 0:

    # 9. Find distance between fingers
            length,img, lineInfo = detector.findDistance(8,12,img)
            #print(length)
     # 10. Click mouse if distance short
            if length <40:
                cv2.circle(img, (lineInfo[4],lineInfo[5]), 15, (0, 255, 0), cv2.FILLED)
                autopy.mouse.click()
        #RIGHT CLICK
        if fingers[0] == 0 and fingers[1] == 1 and fingers[2] == 1 and fingers[3] == 1 and fingers[4] == 0:
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

        #VOLUME
        if fingers[0] == 1 and fingers[1] == 1 and fingers[2] == 0 and fingers[3] == 0 and fingers[4] == 0:
            cx3, cy3 = (x4 + x5) // 2, (y4 + y5) // 2
            r, t = 15, 3
            if True:

                cv2.circle(img, (x4, y4), r, (255, 0, 255), cv2.FILLED)
                cv2.circle(img, (x5, y5), r, (255, 0, 255), cv2.FILLED)
                cv2.line(img, (x5, y5), (x4, y4), (255, 0, 255), t)
                cv2.circle(img, (cx3, cy3), r, (0, 0, 255), cv2.FILLED)
                length = math.hypot(x5 - x4, y5 - y4)

                length = math.hypot(x5 - x4, y5 - y4)
                # print(length)

                # Hand range 50 - 300
                # Volume Range -65 - 0

                vol = np.interp(length, [50, 300], [minVol, maxVol])
                volBar = np.interp(length, [50, 300], [400, 150])
                volPer = np.interp(length, [50, 300], [0, 100])
                print(int(length), vol)
                volume.SetMasterVolumeLevel(vol, None)

                if length < 50:
                    cv2.circle(img, (cx3, cy3), 10, (0, 255, 0), cv2.FILLED)

        cv2.rectangle(img, (50, 150), (85, 400), (255, 0, 0), 3)
        cv2.rectangle(img, (50, int(volBar)), (85, 400), (255, 0, 0), cv2.FILLED)
        cv2.putText(img, f'{int(volPer)} %', (40, 450), cv2.FONT_HERSHEY_COMPLEX,
                    1, (255, 0, 0), 3)














##############################################################
    cTime = time.time()
    # 11. Frame Rate
    fps = 1 / (cTime - pTime)
    pTime = cTime
    cv2.putText(img, str(int(fps)), (20, 50), cv2.FONT_HERSHEY_PLAIN, 3,
                (255, 0, 0), 3)
    # 12. Display
    cv2.imshow("Image", img)
    cv2.waitKey(1)