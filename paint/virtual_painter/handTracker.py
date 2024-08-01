import mediapipe as mp
import cv2


class HandTracker:
    def __init__(self, mode=False, maxHands=2, detectionCon=0.5, trackCon=0.5):
        self.mode = mode
        self.maxHands = maxHands
        self.detectionCon = float(detectionCon)
        self.trackCon = float(trackCon)

        self.mpHands = mp.solutions.hands
        self.hands = self.mpHands.Hands(static_image_mode=self.mode,
                                        max_num_hands=self.maxHands,
                                        min_detection_confidence=self.detectionCon,
                                        min_tracking_confidence=self.trackCon)
        self.mpDraw = mp.solutions.drawing_utils
        self.results = None

    def findHands(self, img, draw=True):
        imgRGB = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
        self.results = self.hands.process(imgRGB)

        if self.results.multi_hand_landmarks:
            for handLm in self.results.multi_hand_landmarks:
                if draw:
                    self.mpDraw.draw_landmarks(img, handLm, self.mpHands.HAND_CONNECTIONS)
        return img

    def getPosition(self, img, handNo=0, draw=True):
        lmList = []
        if self.results and self.results.multi_hand_landmarks:
            myHand = self.results.multi_hand_landmarks[handNo]
            for lm in myHand.landmark:
                h, w, c = img.shape
                cx, cy = int(lm.x * w), int(lm.y * h)
                lmList.append((cx, cy))

                if draw:
                    cv2.circle(img, (cx, cy), 5, (255, 0, 255), cv2.FILLED)
        return lmList
    
    def getUpFingers(self, img):
        pos = self.getPosition(img, draw=False)
        upfingers = []
        if pos:
            # Thumb
            upfingers.append((pos[4][1] < pos[3][1]) and ((pos[5][0] - pos[4][0]) > 10))
            # Index
            upfingers.append(pos[8][1] < pos[7][1] < pos[6][1])
            # Middle
            upfingers.append(pos[12][1] < pos[11][1] < pos[10][1])
            # Ring
            upfingers.append(pos[16][1] < pos[15][1] < pos[14][1])
            # Pinky
            upfingers.append(pos[20][1] < pos[19][1] < pos[18][1])
        return upfingers
