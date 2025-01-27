from handTracker import *
import cv2
import mediapipe as mp
import numpy as np
import random

class ColorRect():
    def __init__(self, x, y, w, h, color, text='', alpha=0.5):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.color = color
        self.text = text
        self.alpha = alpha
    
    def drawRect(self, img, text_color=(255, 255, 255), fontFace=cv2.FONT_HERSHEY_SIMPLEX, fontScale=0.8, thickness=2):
        alpha = self.alpha
        bg_rec = img[self.y:self.y + self.h, self.x:self.x + self.w]
        white_rect = np.ones(bg_rec.shape, dtype=np.uint8)
        white_rect[:] = self.color
        res = cv2.addWeighted(bg_rec, alpha, white_rect, 1-alpha, 1.0)
        img[self.y:self.y + self.h, self.x:self.x + self.w] = res
        text_size = cv2.getTextSize(self.text, fontFace, fontScale, thickness)
        text_pos = (int(self.x + self.w / 2 - text_size[0][0] / 2), int(self.y + self.h / 2 + text_size[0][1] / 2))
        cv2.putText(img, self.text, text_pos, fontFace, fontScale, text_color, thickness)

    def isOver(self, x, y):
        return (self.x + self.w > x > self.x) and (self.y + self.h > y > self.y)

detector = HandTracker(detectionCon=0.8)

cap = cv2.VideoCapture(0)
cap.set(3, 1280)
cap.set(4, 720)

canvas = np.zeros((720, 1280, 3), np.uint8)
px, py = 0, 0
color = (255, 0, 0)
brushSize = 5
eraserSize = 20

colorsBtn = ColorRect(200, 0, 100, 100, (120, 255, 0), 'Colors')
colors = [
    ColorRect(300, 0, 100, 100, (int(random.random() * 255), int(random.random() * 255), int(random.random() * 255))),
    ColorRect(400, 0, 100, 100, (0, 0, 255)),
    ColorRect(500, 0, 100, 100, (255, 0, 0)),
    ColorRect(600, 0, 100, 100, (0, 255, 0)),
    ColorRect(700, 0, 100, 100, (0, 255, 255)),
    ColorRect(800, 0, 100, 100, (0, 0, 0), "Eraser")
]
clear = ColorRect(900, 0, 100, 100, (100, 100, 100), "Clear")

pens = [ColorRect(1100, 50 + 100 * i, 100, 100, (50, 50, 50), str(penSize)) for i, penSize in enumerate(range(5, 25, 5))]
penBtn = ColorRect(1100, 0, 100, 50, color, 'Pen')
boardBtn = ColorRect(50, 0, 100, 100, (255, 255, 0), 'Board')
whiteBoard = ColorRect(50, 120, 1020, 580, (255, 255, 255), alpha=0.6)

coolingCounter = 20
hideBoard = True
hideColors = True
hidePenSizes = True

while True:
    if coolingCounter:
        coolingCounter -= 1

    ret, frame = cap.read()
    if not ret:
        break
    frame = cv2.resize(frame, (1280, 720))
    frame = cv2.flip(frame, 1)

    detector.findHands(frame)
    positions = detector.getPosition(frame, draw=False)
    upFingers = detector.getUpFingers(frame)

    if upFingers:
        x, y = positions[8][0], positions[8][1]
        if upFingers[1] and not whiteBoard.isOver(x, y):
            px, py = 0, 0

            if not hidePenSizes:
                for pen in pens:
                    if pen.isOver(x, y):
                        brushSize = int(pen.text)
                        pen.alpha = 0
                        print(f"Selected brush size: {brushSize}")  # Debug print
                    else:
                        pen.alpha = 0.5

            if not hideColors:
                for cb in colors:
                    if cb.isOver(x, y):
                        color = cb.color
                        cb.alpha = 0
                        print(f"Selected color: {color}")  # Debug print
                    else:
                        cb.alpha = 0.5
                if clear.isOver(x, y):
                    clear.alpha = 0
                    canvas = np.zeros((720, 1280, 3), np.uint8)  # Clear the canvas
                else:
                    clear.alpha = 0.5

            if colorsBtn.isOver(x, y) and not coolingCounter:
                coolingCounter = 10
                colorsBtn.alpha = 0
                hideColors = not hideColors
                colorsBtn.text = 'Colors' if hideColors else 'Hide'
            else:
                colorsBtn.alpha = 0.5

            if penBtn.isOver(x, y) and not coolingCounter:
                coolingCounter = 10
                penBtn.alpha = 0
                hidePenSizes = not hidePenSizes
                penBtn.text = 'Pen' if hidePenSizes else 'Hide'
            else:
                penBtn.alpha = 0.5

            if boardBtn.isOver(x, y) and not coolingCounter:
                coolingCounter = 10
                boardBtn.alpha = 0
                hideBoard = not hideBoard
                boardBtn.text = 'Board' if hideBoard else 'Hide'
            else:
                boardBtn.alpha = 0.5

        elif upFingers[1] and not upFingers[2]:
            if whiteBoard.isOver(x, y) and not hideBoard:
                if px == 0 and py == 0:
                    px, py = x, y
                if color == (0, 0, 0):  # Eraser
                    cv2.line(canvas, (px, py), (x, y), color, eraserSize)
                else:
                    cv2.line(canvas, (px, py), (x, y), color, brushSize)
                px, py = x, y
        else:
            px, py = 0, 0

    # Draw canvas on the frame
    frame = cv2.add(frame, canvas)

    # Draw UI elements
    colorsBtn.drawRect(frame)
    penBtn.drawRect(frame)
    if not hideColors:
        for cb in colors:
            cb.drawRect(frame)
        clear.drawRect(frame)

    if not hidePenSizes:
        for pen in pens:
            pen.drawRect(frame)
    if not hideBoard:
        whiteBoard.drawRect(frame)
    boardBtn.drawRect(frame)

    cv2.imshow("Paint App", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
