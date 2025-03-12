import numpy as np
import copy
import cv2
import math

from scene_info import SceneInfo
from hsv_filter import HSVFilter

from typing import Tuple, Sequence

# type alias to spare my fingers :D
Image = np.ndarray

# BW THRESHOLDING CONSTS
BW_THRESH: int = 30
BW_MAXVALUE: int = 255

# AREA CONSTS
MIN_VALID_AREA: int = 400

CIRCLE_TO_RECT: float = 1.1
CIRCLE_TO_HULL: float = 1.3


class ImageProcessor:
    def __init__(self, img: Image) -> None:
        self._processed_img: Image = copy.deepcopy(img)
        self._color_filters: list[HSVFilter] = []
        self._created_masks: list[np.ndarray] = []

    def add_color_filter(self, to_add: HSVFilter) -> None:
        self._color_filters.append(to_add)

    def filter_color(self) -> None:
        if len(self._color_filters) <= 0:
            print("No filter added :D!!")
            return

        hsv_image: Image = cv2.cvtColor(self._processed_img, cv2.COLOR_BGR2HSV)

        for hsv_filter in self._color_filters:
            # H V S
            mask: np.ndarray = (abs(hsv_filter.h_ref - hsv_image[:, :, 0]) < hsv_filter.h_thresh) & (
                    hsv_image[:, :, 2] > hsv_filter.v_thresh) & (hsv_image[:, :, 1] > hsv_filter.s_thresh)

            self._created_masks.append(mask)

        # put all masks together
        final_mask: np.ndarray = self._created_masks[0]
        for mask_i in range(1, len(self._created_masks)):
            final_mask = np.logical_or(final_mask, self._created_masks[mask_i])

        self._processed_img[~final_mask] = 0

        # denoise
        kernel: np.ndarray = np.ones((4, 4), np.uint8)
        self._processed_img = cv2.morphologyEx(self._processed_img, cv2.MORPH_OPEN, kernel)

    def segment_scene(self, draw: bool = False) -> SceneInfo:
        info: SceneInfo = SceneInfo()

        # remove color from image (make it black and white)
        bw_image: Image = copy.deepcopy(self._processed_img)
        bw_image = cv2.cvtColor(bw_image, cv2.COLOR_BGR2GRAY)
        _, bw_image = cv2.threshold(bw_image, BW_THRESH, BW_MAXVALUE, cv2.THRESH_BINARY)

        contours: np.ndarray
        contours, _ = cv2.findContours(bw_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # evaluate all valid contours
        for contour in contours:
            if cv2.contourArea(contour) <= MIN_VALID_AREA:
                continue

            hull: np.ndarray = cv2.convexHull(contour)

            min_c_center: Tuple[float, float]
            min_c_radius: float
            min_c_center, min_c_radius = cv2.minEnclosingCircle(contour)

            min_rect: Tuple[Sequence[float], Sequence[float], float] = cv2.minAreaRect(contour)

            min_c_area: float = math.pi * (min_c_radius ** 2)
            min_rect_area: float = min_rect[1][0] * min_rect[1][1]

            x: int
            y: int
            w: int
            h: int
            x, y, w, h = cv2.boundingRect(contour)

            # the ball should have different circle/rect area ratio than the pins
            if min_c_area / min_rect_area < CIRCLE_TO_RECT and min_c_area / cv2.contourArea(hull) < CIRCLE_TO_HULL:
                info.has_ball = True
                info.ball_position = (int(min_c_center[0]), int(min_c_center[1]))
            elif h / w > 1.9:
                cx: int = int(x + w / 2)
                cy: int = int(y + h / 2)

                if self._created_masks[1][cy][cx] == 1:
                    info.pin_count += 1
                    info.pin_positions.append((cx, cy))

            # make contours visible in image
            if not draw:
                continue

            # convert to drawable contour
            box: np.ndarray = cv2.boxPoints(min_rect)
            box = np.intp(box)

            cv2.drawContours(self._processed_img, [box], -1, (255, 0, 0), 2)
            cv2.drawContours(self._processed_img, [hull], -1, (0, 0, 255), 2)

        # TODO: Properly return ball center in image
        return info

    def retrieve_image(self) -> Image:
        return self._processed_img
