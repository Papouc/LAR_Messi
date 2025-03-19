from robolab_turtlebot import Turtlebot, Rate

from motor_driver import MotorDriver
from scene_info import SceneInfo
from search_engine import SearchEngine
from visualizer import Visualizer
from hsv_filter import HSVFilter
from image_processor import ImageProcessor, Image

import math

LOOP_RATE: int = 10
TURN_ANGLE: float = (1 / 18) * math.pi

IMAGE_CENTER_X: int = 640 / 2
X_THRESHOLD: int = 10


def main() -> None:
    turtle: Turtlebot = Turtlebot(rgb=True, pc=True)
    main_loop_rate: Rate = Rate(LOOP_RATE)

    visual: Visualizer = Visualizer("WINDOW")

    image_results: list = []
    prev_search_results: list = []

    sanity_check: bool = False
    robot_state: str = "GENERAL_SEARCH"  # GENERAL_SEARCH, CENTER_BALL, GET_RADIUS, MOVE_RADIUS
    last_radius: float = 0.0

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
        image_results.append(result)

        visual.refresh_image(img_processor.retrieve_image(), center_point=True)

        if len(image_results) < 5:
            continue

        search_engine: SearchEngine = SearchEngine(image_results)
        search_result: str = search_engine.determine_state()

        motor_driver: MotorDriver = MotorDriver(turtle, 0.7, 0.0)

        if robot_state == "GENERAL_SEARCH":
            prev_search_results.append(search_result)

            if state_machine_step(sanity_check, prev_search_results, motor_driver):
                if sanity_check:
                    # succesfully found ball
                    sanity_check = False
                    robot_state = "CENTER_BALL"
                else:
                    # initialize double check
                    sanity_check = True
        elif robot_state == "CENTER_BALL":
            if center_ball(image_results, motor_driver):
                robot_state = "GET_RADIUS"
        elif robot_state == "GET_RADIUS":

            if image_results[-1].has_ball:
                depth_image: np.ndarray = turtle.get_point_cloud()
                y_ball_pos: int = image_results[-1].ball_position[1]
                x_ball_pos: int = image_results[-1].ball_position[0]

                last_radius = 0.0
                for y in range(y_ball_pos - 3, y_ball_pos + 4):
                    for x in range(x_ball_pos - 3, x_ball_pos + 4):
                        last_radius += depth_image[y][x][2]

                last_radius /= 7 ** 2
                print(last_radius)
                robot_state = "MOVE_RADIUS"
        elif robot_state == "MOVE_RADIUS":

            if "BALL_FOUND" in prev_search_results and "PINS_FOUND" in prev_search_results:
                print(prev_search_results)

                ball_index: int = prev_search_results.index("BALL_FOUND")
                pins_index: int = prev_search_results.index("PINS_FOUND")

                left: bool = ball_index > pins_index

                if abs(ball_index - pins_index) > 15:
                    left = not left

                print(ball_index, pins_index, left)

                motor_driver.rotate(math.pi / 2, left)
                exit()
            else:
                # previously found both and got here by accident
                robot_state = "GENERAL_SEARCH"

            prev_search_results = []

        main_loop_rate.sleep()
        image_results = []


def state_machine_step(only_ball: bool, prev_search_results: list, motor_driver: MotorDriver) -> bool:
    # purely for being sure that the ball is in the image

    if only_ball and prev_search_results[-1] == "BALL_FOUND":
        return True
    elif only_ball:
        motor_driver.rotate(TURN_ANGLE)
        return False

    # TODO: write something for both found :D
    if "BOTH_FOUND" in prev_search_results:
        return True
    elif "BALL_FOUND" in prev_search_results and "PINS_FOUND" in prev_search_results:
        ball_first_index: int = prev_search_results.index("BALL_FOUND")
        ball_last_index: int = len(prev_search_results) - prev_search_results[::-1].index("BALL_FOUND")
        ball_mid_index: int = int((ball_last_index + ball_first_index) / 2)
        pins_index: int = prev_search_results.index("PINS_FOUND")

        if pins_index > ball_first_index:
            motor_driver.rotate(abs(ball_mid_index - pins_index) * TURN_ANGLE, False)

        return True

    else:
        motor_driver.rotate(TURN_ANGLE)

    return False


def center_ball(image_results: list, motor_driver: MotorDriver) -> bool:
    if image_results[-1].has_ball:
        # only take this image
        dist_from_mid: int = image_results[-1].ball_position[0] - IMAGE_CENTER_X
        if abs(dist_from_mid) < X_THRESHOLD:
            # ball is ~ centered :D, stop rotation
            motor_driver.rotate_non_blocking(False, False)
            return True
        elif dist_from_mid > 0:
            motor_driver.rotate_non_blocking(True, False)
        else:
            motor_driver.rotate_non_blocking(True, True)
    else:
        return False


if __name__ == "__main__":
    main()
