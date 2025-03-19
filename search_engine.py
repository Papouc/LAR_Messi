from scene_info import SceneInfo

class SearchEngine:
    def __init__(self, scene_infos: list) -> None:
        self._scene_infos: list = scene_infos

    def determine_state(self) -> str:

        positive_ball_cnt: int = 0
        positive_pin_cnt: int = 0

        info: SceneInfo
        for info in self._scene_infos:

            if info.has_ball:
                positive_ball_cnt += 1

            if info.pin_count == 2:
                positive_pin_cnt += 1

        if positive_ball_cnt >= 3 and positive_pin_cnt >= 3:
            # ball and two pins
            return "BOTH_FOUND"
        elif positive_ball_cnt >= 3:
            # only ball
            return "BALL_FOUND"
        elif positive_pin_cnt >= 3:
            # only pins
            return "PINS_FOUND"

        return "NO_INFO"
