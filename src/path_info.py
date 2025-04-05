"""
Path Planning Information Container for TurtleBot Soccer Player.

This module defines the PathInfo dataclass which stores all necessary
information for navigation and path planning during soccer operations.
"""

from dataclasses import dataclass, field
from typing import List


@dataclass
class PathInfo:
    """Centralized storage for path planning and navigation information.

    Attributes:
        pin_vectors: 3D vectors representing pin positions in camera space.
        circle_radius: Calculated distance to the ball in meters.
        ball_pins_angle: Relative angle between ball and goal posts in radians.
        path_arc_angle: Calculated arc angle for navigation path in radians.
        on_left: Flag indicating if ball is on left side relative to goal.
        from_one_picture: Flag if all objects were detected in single frame.
        aligning_phase: Flag indicating if robot is in final alignment phase.
        score_back_up_done: Flag tracking backup before scoring was performed.
        move_closer: Flag indicating if robot needs to reduce distance to ball.
    """

    pin_vectors: List = field(default_factory=list)
    circle_radius: float = 0.0
    ball_pins_angle: float = 0.0
    path_arc_angle: float = 0.0
    on_left: bool = True
    from_one_picture: bool = False
    aligning_phase: bool = False
    score_back_up_done: bool = False
    move_closer: bool = False
