"""
Image Processing Pipeline for TurtleBot Soccer Player

This module handles all image processing tasks for the robotic soccer system,
including:
- Color filtering in HSV space
- Contour detection and analysis
- Object classification (ball vs goal posts)
- Scene segmentation and feature extraction

The ImageProcessor class provides methods to:
1. Apply multiple HSV color filters to isolate objects of interest
2. Convert filtered images to binary representations
3. Detect and analyze contours to classify objects
4. Extract positional information about detected objects

Key Features:
- Uses HSV color space for robust color filtering
- Employs contour analysis to distinguish between ball and goal posts
- Provides geometric shape analysis (circle vs rectangle ratios)
- Maintains internal state of processed images for visualization

Constants:
- BW_THRESH: Threshold for binary image conversion
- BW_MAXVALUE: Maximum value for binary thresholding
- MIN_VALID_AREA_BALL: Minimum contour area to consider as valid ball
- MIN_VALID_AREA_PIN: Minimum contour area to consider as valid goal post
- CIRCLE_TO_RECT: Circle-to-rectangle area ratio threshold for ball detection
- CIRCLE_TO_HULL: Circle-to-hull area ratio threshold for ball detection
"""

import numpy as np
import copy
import cv2
import math

from scene_info import SceneInfo
from hsv_filter import HSVFilter

from typing import Tuple, Sequence

# Type alias for image arrays
Image = np.ndarray

# Binary thresholding constants
BW_THRESH: int = 30  # Threshold value for binary conversion
BW_MAXVALUE: int = 255  # Maximum pixel value for binary thresholding

# Minimum valid contour areas
MIN_VALID_AREA_BALL: int = 800  # Minimum area to consider as valid ball
MIN_VALID_AREA_PIN: int = 300  # Minimum area to consider as valid goal post

# Shape ratio thresholds for ball detection
CIRCLE_TO_RECT: float = 1.1  # Circle-to-rectangle area ratio threshold
CIRCLE_TO_HULL: float = 1.3  # Circle-to-convex-hull area ratio threshold


class ImageProcessor:
    """
    Main image processing class for filtering, segmentation and detection.
    Also handles contour calculation and comparison of visible ball and pins
    to perfect circle and square respectively.
    """

    def __init__(self, img: Image) -> None:
        """
        Initialize the ImageProcessor with an input image.

        Args:
            img (Image): Input BGR image as numpy array
        """
        self._processed_img: Image = copy.deepcopy(img)
        self._color_filters: list[HSVFilter] = []
        self._created_masks: list[np.ndarray] = []

    def add_color_filter(self, to_add: HSVFilter) -> None:
        """
        Add an HSV color filter to the processing pipeline.

        Args:
            to_add (HSVFilter): HSV filter to be added
        """
        self._color_filters.append(to_add)

    def filter_color(self) -> None:
        """
        Apply all registered HSV filters to the image.

        Creates binary masks for each filter and combines them to isolate
        objects of interest. Performs morphological opening to reduce noise.
        """
        if len(self._color_filters) <= 0:
            print("No filter added :D!!")
            return

        # Convert to HSV color space
        hsv_image: Image = cv2.cvtColor(
            self._processed_img, cv2.COLOR_BGR2HSV)

        # Create masks for each filter
        for hsv_filter in self._color_filters:
            h_diff = abs(hsv_filter.h_ref - hsv_image[:, :, 0])
            mask: np.ndarray = (
                    (h_diff < hsv_filter.h_thresh) &
                    (hsv_image[:, :, 2] > hsv_filter.v_thresh) &
                    (hsv_image[:, :, 1] > hsv_filter.s_thresh)
            )
            self._created_masks.append(mask)

        # Combine all masks
        final_mask: np.ndarray = self._created_masks[0]
        for mask_i in range(1, len(self._created_masks)):
            final_mask = np.logical_or(final_mask, self._created_masks[mask_i])

        # Apply combined mask
        self._processed_img[~final_mask] = 0

        # Denoise using morphological opening
        kernel: np.ndarray = np.ones((4, 4), np.uint8)
        self._processed_img = cv2.morphologyEx(
            self._processed_img, cv2.MORPH_OPEN, kernel)

    def segment_scene(self, draw: bool = False) -> SceneInfo:
        """
        Analyze the filtered image to detect and classify objects.

        Args:
            draw (bool): Whether to draw contours on the processed image

        Returns:
            SceneInfo: Object containing detected scene information
        """
        info: SceneInfo = SceneInfo()

        # Convert to grayscale and threshold
        bw_image: Image = copy.deepcopy(self._processed_img)
        bw_image = cv2.cvtColor(bw_image, cv2.COLOR_BGR2GRAY)
        _, bw_image = cv2.threshold(
            bw_image, BW_THRESH, BW_MAXVALUE, cv2.THRESH_BINARY)

        # Find contours in binary image
        contours: np.ndarray
        contours, _ = cv2.findContours(
            bw_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)

        # Analyze each contour
        for contour in contours:
            if cv2.contourArea(contour) <= MIN_VALID_AREA_PIN:
                continue

            # Calculate contour properties
            hull: np.ndarray = cv2.convexHull(contour)
            min_c_center: Tuple[float, float]
            min_c_radius: float
            min_c_center, min_c_radius = cv2.minEnclosingCircle(contour)
            min_rect: Tuple[Sequence[float], Sequence[float], float] = \
                cv2.minAreaRect(contour)
            min_c_area: float = math.pi * (min_c_radius ** 2)
            min_rect_area: float = min_rect[1][0] * min_rect[1][1]
            x, y, w, h = cv2.boundingRect(contour)

            # Classify as ball based on shape ratios
            if (min_c_area / min_rect_area < CIRCLE_TO_RECT and
                    min_c_area / cv2.contourArea(hull) < CIRCLE_TO_HULL):

                if cv2.contourArea(contour) <= MIN_VALID_AREA_BALL:
                    continue

                info.has_ball = True
                info.ball_position = (int(min_c_center[0]),
                                      int(min_c_center[1]))

                # Classify as goal post based on aspect ratio
            elif h / w > 1.9:
                cx: int = int(x + w / 2)
                cy: int = int(y + h / 2)

                if self._created_masks[1][cy][cx] == 1:
                    info.pin_count += 1
                    info.pin_positions.append((cx, cy))

            # Visualization (if enabled)
            if not draw:
                continue

            box: np.ndarray = cv2.boxPoints(min_rect)
            box = np.intp(box)
            cv2.drawContours(self._processed_img, [box], -1, (255, 0, 0), 2)
            cv2.drawContours(self._processed_img, [hull], -1, (0, 0, 255), 2)

        return info

    def retrieve_image(self) -> Image:
        """
        Get the processed image with optional visualizations.

        Returns:
            Image: The current processed image
        """
        return self._processed_img
