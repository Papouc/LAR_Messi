from robolab_turtlebot import Turtlebot, Rate

from motor_driver import MotorDriver
from scene_info import SceneInfo
from search_engine import SearchEngine
from visualizer import Visualizer
from hsv_filter import HSVFilter
from image_processor import ImageProcessor, Image

import math

LOOP_RATE: int = 10
TURN_ANGLE: float = (1/18) * math.pi

def main() -> None:
    turtle: Turtlebot = Turtlebot(rgb=True)
    main_loop_rate: Rate = Rate(LOOP_RATE)

    visual: Visualizer = Visualizer("WINDOW")

    image_reults: list = []
    prev_search_results: list = []

    sanity_check: bool = False
    robot_state: str = "GENERAL_SEARCH" # GENERAL_SEARCH, CENTER_BALL, MOVE_RADIUS

    while not turtle.is_shutting_down():
        new_img: Image = turtle.get_rgb_image()

        img_processor: ImageProcessor = ImageProcessor(new_img)

        # "yellow" filter
        ball_filter: HSVFilter = HSVFilter(30, 130, 60, 48)
        img_processor.add_color_filter(ball_filter)

        # "blue" filter
        goal_filter: HSVFilter = HSVFilter(105, 160, 98, 196)
        img_processor.add_color_filter(goal_filter)

        img_processor.filter_color()

        result: SceneInfo = img_processor.segment_scene(draw=True)
        image_reults.append(result)

        visual.refresh_image(img_processor.retrieve_image(), center_point=True)

        if len(image_reults) < 5:
            continue

        search_engine: SearchEngine = SearchEngine(image_reults)
        search_result: str = search_engine.determine_state()
        prev_search_results.append(search_result)

        motor_driver: MotorDriver = MotorDriver(turtle, 0.7, 0.0)

        if robot_state == "GENERAL_SEARCH":
            if state_machine_step(sanity_check, prev_search_results, motor_driver):
                if sanity_check:
                    # succesfully found ball
                    sanity_check = False
                    print("checked")
                    prev_search_results = []
                    exit()
                else:
                    # initialize double check
                    sanity_check = True
        elif robot_state == "SANITY_CHECK":
            pass

        main_loop_rate.sleep()
        image_reults = []


def state_machine_step(only_ball: bool, prev_search_results: list, motor_driver: MotorDriver) -> bool:

    # purely for being sure that the ball is in the image
    if only_ball and prev_search_results[-1] == "BALL_FOUND":
        return True
    elif only_ball:
        motor_driver.rotate(TURN_ANGLE)
        return False

    if "BOTH_FOUND" in prev_search_results:
        return True
    elif "BALL_FOUND" in prev_search_results and "PINS_FOUND" in prev_search_results:
        ball_first_index: int = prev_search_results.index("BALL_FOUND")
        ball_last_index: int = len(prev_search_results) - prev_search_results[::-1].index("BALL_FOUND")
        ball_mid_index: int = int((ball_last_index + ball_first_index) / 2)
        pins_index: int = prev_search_results.index("PINS_FOUND")

        if pins_index > ball_first_index:
            motor_driver.rotation_speed *= -1.0
            motor_driver.rotate((ball_mid_index - pins_index) * TURN_ANGLE)
            motor_driver.rotation_speed *= -1.0
            return True

    else:
        motor_driver.rotate(TURN_ANGLE)

    return False

if __name__ == "__main__":
    main()
