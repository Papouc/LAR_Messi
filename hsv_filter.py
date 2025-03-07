from dataclasses import dataclass

@dataclass
class HSVFilter:
    h_thresh: float
    s_thresh: float
    v_thresh: float

    h_ref: float