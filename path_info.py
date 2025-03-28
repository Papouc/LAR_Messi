from dataclasses import dataclass, field

@dataclass
class PathInfo:
    pin_vectors: list = field(default_factory=list)
    circle_radius: float = 0.0
    ball_pins_angle: float = 0.0
    path_arc_angle: float = 0.0
    on_left: bool = True
    from_one_picture: bool = False
    aligning_phase: bool = False