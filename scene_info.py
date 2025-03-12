from dataclasses import dataclass, field
from typing import Tuple


@dataclass
class SceneInfo:
    has_ball: bool = False
    ball_position: Tuple[int, int] = (0, 0)
    pin_count: int = 0
    pin_positions: list = field(default_factory=list)
