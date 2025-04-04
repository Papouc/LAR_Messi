"""
Scene Information Data Structure for TurtleBot Soccer Player.

This module defines the SceneInfo dataclass which serves as a structured
container for storing information about detected objects in the environment.
"""

from dataclasses import dataclass, field
from typing import Tuple, List


@dataclass
class SceneInfo:
    """Data container for scene analysis results from image processing.

    Attributes:
        has_ball: Flag indicating if a ball was detected in the scene.
        ball_position: Pixel coordinates (x,y) of detected ball center.
        pin_count: Number of detected goal posts (pins).
        pin_positions: List of (x,y) pixel coordinates for each detected pin.
    """
    has_ball: bool = False
    ball_position: Tuple[int, int] = (0, 0)
    pin_count: int = 0
    pin_positions: List[Tuple[int, int]] = field(default_factory=list)
