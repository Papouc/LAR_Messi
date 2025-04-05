"""
HSV Color Filter Implementation

This module defines an HSV (Hue-Saturation-Value) color filter used for object
detection in the TurtleBot soccer player system. The filter uses threshold
values to identify specific color ranges in the HSV color space.

The HSVFilter class is implemented as a dataclass for convenient storage and
access to filter parameters.

Attributes:
    h_thresh (float): Hue threshold value (range 0-180 in OpenCV)
    s_thresh (float): Saturation threshold value (range 0-255)
    v_thresh (float): Value (brightness) threshold value (range 0-255)
    h_ref (float): Reference hue value for color comparison

The filter is used by the ImageProcessor to isolate specific colored objects
(ball and goal(gate) posts(pins)) in the camera feed by creating binary masks
based on these threshold values.

Note: In OpenCV's implementation of HSV:
- Hue ranges from 0-180 (instead of 0-360)
- Saturation and Value range from 0-255
"""

from dataclasses import dataclass


@dataclass
class HSVFilter:
    """
    Data class representing an HSV color filter for object detection.

    The filter parameters define the threshold for detecting wanted colors.
    Attributes:
        h_thresh (float): Threshold for hue difference from reference value
        s_thresh (float): Minimum saturation value threshold
        v_thresh (float): Minimum brightness value threshold
        h_ref (float): Reference hue value for the target color
    """
    h_thresh: float
    s_thresh: float
    v_thresh: float
    h_ref: float
