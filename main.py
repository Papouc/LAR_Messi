import copy
import math

from robolab_turtlebot import Turtlebot, Rate
import numpy as np
import cv2

WINDOW = 'obstacles'
cv2.namedWindow(WINDOW)

turtle = Turtlebot(rgb=True)
rate = Rate(10)

while not turtle.is_shutting_down():
    new_image = turtle.get_rgb_image()

    if new_image is None:
        continue

    # mask = new_image[:, :, 0] > 150
    # mask = np.logical_and(mask, new_image[:, :, 1] > 150)
    # mask = np.logical_and(mask, new_image[:, :, 2] < 150)

    # print(new_image[240][320])

    HSV_ref = [48, 79, 75]
    HSV_image = cv2.cvtColor(new_image, cv2.COLOR_BGR2HSV)

    # H V S
    mask = (abs(HSV_ref[0] - HSV_image[:, :, 0]) < 30) & (HSV_image[:, :, 2] > 60) & (HSV_image[:, :, 1] > 130)

    masked = new_image.copy()
    masked[~mask] = 0

    masked[241][320][2] = 255
    masked[241][320][1] = 0
    masked[241][320][0] = 0

    masked[242][320][2] = 255
    masked[242][320][1] = 0
    masked[242][320][0] = 0

    masked[243][320][2] = 255
    masked[243][320][1] = 0
    masked[243][320][0] = 0

    masked[244][320][2] = 255
    masked[244][320][1] = 0
    masked[244][320][0] = 0

    masked_cpy = copy.deepcopy(masked)

    kernel = np.ones((4, 4), np.uint8)
    masked = cv2.morphologyEx(masked, cv2.MORPH_OPEN, kernel)

    masked = cv2.cvtColor(masked, cv2.COLOR_BGR2GRAY)
    _, masked = cv2.threshold(masked, 70, 255, 0)
    # masked = cv2.Canny(masked, 30, 200)

    out = cv2.connectedComponentsWithStats(masked.astype(np.uint8))
    contours, hieararchy = cv2.findContours(masked, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

    # 0 - počet oblsatí
    for contour in contours:
        # 2 - parametry, i - oblast, 4 - area
        if cv2.contourArea(contour) > 400:
            hull = cv2.convexHull(contour)
            (x, y), radius = cv2.minEnclosingCircle(contour)
            rect = cv2.minAreaRect(contour)

            center = (int(x), int(y))
            cv2.circle(masked_cpy, center, int(radius), (0, 255, 0), 3)

            box = cv2.boxPoints(rect)
            box = np.int0(box)

            cv2.drawContours(masked_cpy, [box], -1, (255, 0, 0), 3)

            cv2.drawContours(masked_cpy, [hull], -1, (0, 0, 255), 3)

            circle_area = math.pi * (radius ** 2)
            box_area = rect[1][0] * rect[1][0]

            # možnost přidat další poměry (např. hull/box)
            print("c/b", circle_area / box_area)
            print("c/h", circle_area / cv2.contourArea(hull))
            if circle_area / box_area < 1.1 and circle_area / cv2.contourArea(hull) < 1.3:
                print("Circle :D")
            else:
                print("not")

    # cv2.drawContours(masked_cpy, contours, -1, (0, 255, 0), 1)

    cv2.imshow(WINDOW, masked_cpy)
    cv2.waitKey(1)

    rate.sleep()
