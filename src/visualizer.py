"""
Visualization System for TurtleBot Soccer Player.

This module provides real-time visualization of the robot's perception
and processing with optional visual markers.
"""

import cv2
from image_processor import Image

# Display refresh delay in milliseconds (1ms for near real-time)
DELAY_TIME: int = 1


class Visualizer:
    """Handles visualization of processed images with optional markers."""

    def __init__(self, win_name: str) -> None:
        """
        Initialize the visualizer with a window name.

        Args:
            win_name: Name for the display window
        """
        self.win_name: str = win_name
        cv2.namedWindow(self.win_name)  # Create named window for display

    def refresh_image(self, image: Image, center_point: bool = False) -> None:
        """
        Update the display with a new image and optional center marker.

        Args:
            image: The image to display (numpy array)
            center_point: Whether to draw a center reference marker
        """
        if center_point and len(image) > 0:
            # Calculate image center coordinates
            y_half: int = len(image) // 2
            x_half: int = len(image[0]) // 2

            # Draw 3x3 red square at center
            for y_offset in range(-1, 2):
                for x_offset in range(-1, 2):
                    image[y_half + y_offset][x_half + x_offset] = [0, 0, 255]

        # Update display
        cv2.imshow(self.win_name, image)
        cv2.waitKey(DELAY_TIME)  # Brief delay allows window to updat
