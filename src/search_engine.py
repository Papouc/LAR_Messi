"""
Scene Analysis Engine for TurtleBot Soccer Player.

This module implements the SearchEngine class which analyzes multiple scene
information samples to determine the robot's current detection state.
"""

from scene_info import SceneInfo
from typing import List


class SearchEngine:
    """Analyzes scene information over multiple frames to determine state."""

    def __init__(self, scene_infos: List[SceneInfo]) -> None:
        """
        Initialize the SearchEngine with historical scene information.

        Args:
            scene_infos: List of SceneInfo objects containing detection
                        results from previous frames
        """
        self._scene_infos: List[SceneInfo] = scene_infos

    def determine_state(self) -> str:
        """
        Determine current detection state based on accumulated information.

        Requires at least 3 positive detections of each object type for
        confirmation to ensure robust detection.

        Returns:
            str: One of the following detection states:
                - "BOTH_FOUND" (ball and both goal posts detected)
                - "BALL_FOUND" (only ball detected)
                - "PINS_FOUND" (only goal posts detected)
                - "NO_INFO" (insufficient detections)
        """
        positive_ball_cnt: int = 0
        positive_pin_cnt: int = 0

        for info in self._scene_infos:
            if info.has_ball:
                positive_ball_cnt += 1

            if info.pin_count == 2:  # Require both pins for positive detection
                positive_pin_cnt += 1

        if positive_ball_cnt >= 3 and positive_pin_cnt >= 3:
            return "BOTH_FOUND"
        if positive_ball_cnt >= 3:
            return "BALL_FOUND"
        if positive_pin_cnt >= 3:
            return "PINS_FOUND"

        return "NO_INFO"
