"""
Autonomous TurtleBot Soccer Player System

This program implements a complete robotic soccer player capable of:
0. Starting by pressing a button
1. Visual perception using RGB-D camera
2. Object detection and tracking
3. Path planning and navigation
4. Autonomous goal-scoring behavior

Core Capabilities:
- Real-time ball detection using HSV color filtering (yellow)
- Goal(gate) post(pin) detection (two blue pins)
- Depth perception for distance measurement
- State machine-based decision making
- Precise motor control for navigation
- Visual feedback system

System Architecture:
1. Perception Layer:
   - Realsense D435 camera (RGB + Depth)
   - HSV color filtering (ball and goal posts)
   - Contour analysis for object classification

2. Processing Layer:
   - Image processing pipeline
   - Scene analysis and state determination
   - Path planning mathematics

3. Control Layer:
   - Finite State Machine (12 states)
   - Motor control
   - Odometry-based navigation

State Machine States:
IDLE → GENERAL_SEARCH → CENTER_BALL → GET_RADIUS → COMPUTE_PATH →
CHECK_DISTANCE → EXEC_PATH → PREP_TO_SCORE → BACK_OFF → ALIGN → SCORE → EM_STOP
"""

from robolab_turtlebot import Turtlebot, Rate
from motor_driver import MotorDriver
from scene_info import SceneInfo
from search_engine import SearchEngine
from visualizer import Visualizer
from hsv_filter import HSVFilter
from image_processor import ImageProcessor, Image
from path_info import PathInfo
from sympy import symbols, Eq, solve
from typing import Tuple

import numpy as np
import math


# System Constants
LOOP_RATE: int = 10                  # Main control loop frequency (Hz)
TURN_ANGLE: float = (1 / 18) * math.pi  # Default rotation increment (radians)
IMAGE_CENTER_X: int = 640 // 2       # Horizontal center of camera frame
X_THRESHOLD: int = 10                # Ball centering tolerance (pixels)
DEAD_AREA_ANGLE: float = 0.3         # Minimum viable path arc angle (radians)

# HSV Filter Parameters
BALL_HSV = HSVFilter(30, 125, 65, 48)   # Yellow ball detection thresholds
GOAL_HSV = HSVFilter(105, 160, 98, 196)  # Blue goal post detection thresholds


def main() -> None:
    """Main control loop for autonomous soccer player."""
    turtle: Turtlebot = Turtlebot(rgb=True, pc=True)
    main_loop_rate: Rate = Rate(LOOP_RATE)

    visual: Visualizer = Visualizer("WINDOW")

    image_results: list = []
    prev_search_results: list = []

    # Robot state machine states
    robot_state: str = "IDLE"  # Possible states:
    # IDLE, GENERAL_SEARCH, CENTER_BALL, GET_RADIUS, COMPUTE_PATH,
    # EXEC_PATH, CHECK_DISTANCE, PREP_TO_SCORE, BACK_OFF, ALIGN, SCORE, EM_STOP

    # Math related values for path planning
    path_info: PathInfo = PathInfo()
    k_matrix: np.ndarray = turtle.get_rgb_K()

    def change_state_onclicked(cb: dict) -> None:
        """Callback for button press event to start the robot."""
        nonlocal robot_state
        robot_state = "GENERAL_SEARCH"

    def change_state_onbumper(cb: dict) -> None:
        """Callback for bumper press event for emergency stop."""
        nonlocal robot_state
        robot_state = "EM_STOP"

    turtle.register_button_event_cb(change_state_onclicked)
    turtle.register_bumper_event_cb(change_state_onbumper)

    back_off_counter: int = 0

    while not turtle.is_shutting_down():
        new_img: Image = turtle.get_rgb_image()

        if new_img is None or robot_state == "IDLE":
            continue

        img_processor: ImageProcessor = ImageProcessor(new_img)

        # "yellow" filter for ball detection
        ball_filter: HSVFilter = HSVFilter(30, 125, 65, 48)
        img_processor.add_color_filter(ball_filter)

        # "blue" filter for goal pins detection
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

        # State machine implementation
        if robot_state == "GENERAL_SEARCH":
            prev_search_results.append(search_result)

            depth_image: np.ndarray = turtle.get_point_cloud()

            if search_result == "BOTH_FOUND":
                path_info.pin_vectors = get_pin_vectors(
                    depth_image, k_matrix, image_results[-1])
                path_info.from_one_picture = True
                path_info.ball_pins_angle = 0
                path_info.on_left, _ = get_side(image_results)

            elif (search_result == "PINS_FOUND" and
                    len(path_info.pin_vectors) <= 0):
                path_info.pin_vectors = get_pin_vectors(
                    depth_image, k_matrix, image_results[-1])

            if state_machine_step(prev_search_results, motor_driver,
                                  path_info):
                if (search_result == "BALL_FOUND" or
                        search_result == "BOTH_FOUND"):
                    robot_state = "CENTER_BALL"
                else:
                    path_info = PathInfo()
                    prev_search_results = []
                    robot_state = "GENERAL_SEARCH"

        elif robot_state == "CENTER_BALL":
            motor_driver.reset_odometry_blocking()
            if center_ball(image_results, motor_driver):
                # add centering offset to angle between pins and ball
                turtle.wait_for_odometry()
                path_info.ball_pins_angle += turtle.get_odometry()[2]
                print("Centering offset", turtle.get_odometry()[2])

                robot_state = "GET_RADIUS"
            elif not image_results[-1].has_ball:
                robot_state = "GENERAL_SEARCH"

        elif robot_state == "GET_RADIUS":
            if image_results[-1].has_ball:
                depth_image: np.ndarray = turtle.get_point_cloud()
                y_ball_pos: int = image_results[-1].ball_position[1]
                x_ball_pos: int = image_results[-1].ball_position[0]

                path_info.circle_radius = get_distance_of_pixel(
                    depth_image, x_ball_pos, y_ball_pos)

                if path_info.aligning_phase:
                    robot_state = "ALIGN"
                elif path_info.move_closer:
                    robot_state = "CHECK_DISTANCE"
                else:
                    robot_state = "COMPUTE_PATH"

        elif robot_state == "COMPUTE_PATH":
            if not path_info.from_one_picture:
                ball_index: int = prev_search_results.index("BALL_FOUND")
                pins_index: int = prev_search_results.index("PINS_FOUND")

                # check if full revolution between ball and pins
                if ((abs(ball_index - pins_index) > 15 and
                     ball_index > pins_index) or
                    (pins_index > ball_index and
                     abs(ball_index - pins_index) < 10)):
                    path_info.on_left = True
                else:
                    path_info.on_left = False
                    path_info.ball_pins_angle *= -1

            temp = path_info.pin_vectors[1] - path_info.pin_vectors[0]
            q1: np.ndarray = temp
            c1: np.ndarray = path_info.pin_vectors[0] + q1 / 2

            beta: float = path_info.ball_pins_angle
            print("Beta", beta)

            transf_matrix: np.ndarray = np.array([
                [math.cos(beta), 0, math.sin(beta)],
                [0, 1, 0],
                [-math.sin(beta), 0, math.cos(beta)]
            ])

            r_transf: np.ndarray = transf_matrix @ np.array(
                [0, 0, path_info.circle_radius])

            # TODO: typdef
            x, y = symbols('x y', real=True)

            eq1 = Eq((x - r_transf[0]) ** 2 + (y - r_transf[2]) ** 2 -
                     path_info.circle_radius ** 2, 0)
            eq2 = Eq(q1[0] * x + q1[2] * y -
                     (q1[0] * c1[0] + q1[2] * c1[2]), 0)

            solutions : Tuple[float, float] = solve((eq1, eq2), (x, y))

            # no intersections found
            if len(solutions) != 2:
                path_info = PathInfo()
                prev_search_results = []
                robot_state = "GENERAL_SEARCH"
                continue

            guess_pos_1: np.ndarray = np.array(
                [c1[0] - solutions[0][0], c1[2] - solutions[0][1]])
            guess_pos_2: np.ndarray = np.array(
                [c1[0] - solutions[1][0], c1[2] - solutions[1][1]])

            dest_pos: np.ndarray
            if vector_norm(guess_pos_2) > vector_norm(guess_pos_1):
                dest_pos = np.array([solutions[1][0], solutions[1][1]])
            else:
                dest_pos = np.array([solutions[0][0], solutions[0][1]])

            r_transf2D: np.ndarray = np.array([r_transf[0], r_transf[2]])
            center_to_dest: np.ndarray = dest_pos - r_transf2D

            dot_product: float = (-r_transf2D[0] * center_to_dest[0]) + \
                                 (-r_transf2D[1] * center_to_dest[1])
            final_angle: float = math.acos(dot_product /
                                           (vector_norm(-r_transf2D) *
                                            vector_norm(center_to_dest)))

            path_info.path_arc_angle = final_angle
            print("Arc angle:", final_angle)

            robot_state = "CHECK_DISTANCE"

        elif robot_state == "CHECK_DISTANCE":
            path_info.move_closer = False

            if path_info.circle_radius < 0.9:
                robot_state = "EXEC_PATH"
            else:
                path_info.move_closer = True
                motor_driver.set_speed(0.0, 0.2)
                motor_driver.move_forward(1)
                motor_driver.set_speed(0.7, 0.0)

                robot_state = "CENTER_BALL"

        elif robot_state == "EXEC_PATH":
            if path_info.path_arc_angle < DEAD_AREA_ANGLE:
                robot_state = "PREP_TO_SCORE"
                continue

            if (("BALL_FOUND" in prev_search_results and
                 "PINS_FOUND" in prev_search_results) or
                    "BOTH_FOUND" in prev_search_results):

                if "BOTH_FOUND" not in prev_search_results:
                    ball_index: int = prev_search_results.index("BALL_FOUND")
                    pins_index: int = prev_search_results.index("PINS_FOUND")

                    left: bool = ball_index > pins_index

                    # check if full revolution between ball and pins
                    if abs(ball_index - pins_index) > 15:
                        left = not left
                else:
                    left = not path_info.on_left

                # look 90deg away from ball
                motor_driver.rotate(math.pi / 2, left)

                # follow arc until shooting position
                lin_speed: float = 0.2
                rot_speed: float = lin_speed / path_info.circle_radius

                travel_time: float = (path_info.path_arc_angle *
                                      path_info.circle_radius) / lin_speed
                print("Travel time:", travel_time)

                motor_driver.set_speed(
                    rot_speed if path_info.on_left else -rot_speed, lin_speed)
                motor_driver.move_forward_accel(travel_time)

                motor_driver.set_speed(0.7, 0.0)
                motor_driver.rotate(math.pi / 2, not left)
                robot_state = "PREP_TO_SCORE"
            else:
                # previously found both and got here by accident
                robot_state = "GENERAL_SEARCH"

            prev_search_results = []

        elif robot_state == "PREP_TO_SCORE":
            path_info.aligning_phase = True
            robot_state = "CENTER_BALL"

        elif robot_state == "BACK_OFF":
            reverse_walk(motor_driver)
            back_off_counter += 1
            robot_state = "CENTER_BALL"

        elif robot_state == "ALIGN":
            if image_results[-1].pin_count < 2:
                if back_off_counter < 2:
                    robot_state = "BACK_OFF"
                else:
                    robot_state = "SCORE"
                continue

            on_left: bool
            pin_center: int
            on_left, pin_center = get_side(image_results)
            ball_center: int = image_results[-1].ball_position[0]

            dist_from_center: int = abs(ball_center - pin_center)
            print("Pixel distance:", dist_from_center)

            if dist_from_center < 10:
                robot_state = "SCORE"
            else:
                motor_driver.rotate(math.pi / 2, not on_left)

                lin_speed: float = 0.1
                rot_speed: float = (lin_speed / path_info.circle_radius) * 2

                motor_driver.set_speed(
                    rot_speed if on_left else -rot_speed, lin_speed)
                motor_driver.move_forward(
                    dist_from_center * path_info.circle_radius / 30)
                motor_driver.set_speed(0.7, 0.0)

                motor_driver.rotate(math.pi / 2, on_left)
                robot_state = "PREP_TO_SCORE"

        elif robot_state == "SCORE":
            depth_image: np.ndarray = turtle.get_point_cloud()

            ball_x: int
            ball_y: int
            ball_x, ball_y = image_results[-1].ball_position

            dist_to_ball: float = depth_image[ball_y][ball_x][2]

            # back off from the ball a little
            if (dist_to_ball < 0.6 and
                    not path_info.score_back_up_done):
                reverse_walk(motor_driver)

            path_info.score_back_up_done = True

            lin_speed: float = 0.8
            rot_speed: float = 0.75 / dist_to_ball

            motor_driver.set_speed(rot_speed, lin_speed)

            score_time: float = dist_to_ball / lin_speed
            motor_driver.move_forward(score_time)
            print("Gooool:D!!")
            break

        elif robot_state == "EM_STOP":
            motor_driver.set_speed(0.0, 0.0)
            break

        main_loop_rate.sleep()
        image_results = []

    turtle.play_sound()


def reverse_walk(motor_driver: MotorDriver) -> None:
    """Make the robot move backward for a short distance."""
    motor_driver.set_speed(0.0, -0.15)
    motor_driver.move_forward(2.0)
    motor_driver.set_speed(0.7, 0.0)


def get_side(image_results: list) -> Tuple[bool, int]:
    """
    Determine which side of the field the robot is on relative to goal center.

    Args:
        image_results: List of recent image processing results

    Returns:
        Tuple containing:
        - bool: True if ball is on left side of goal center
        - int: x-coordinate of goal center in image
    """
    index: int = 1
    while len(image_results[5 - index].pin_positions) < 2:
        index += 1

    pin_center: int = (image_results[5 - index].pin_positions[0][0] +
                       image_results[5 - index].pin_positions[1][0]) / 2

    return pin_center <= image_results[5 - index].ball_position[0], pin_center


def state_machine_step(prev_search_results: list,
                       motor_driver: MotorDriver,
                       path_info: PathInfo) -> bool:
    """
    Handle state transitions for the GENERAL_SEARCH state.

    Args:
        prev_search_results: List of previous search results
        motor_driver: Motor controller instance
        path_info: Path planning information container

    Returns:
        bool: True if state transition should occur, False otherwise
    """
    if "BOTH_FOUND" in prev_search_results:
        return True

    if ("BALL_FOUND" in prev_search_results and
            "PINS_FOUND" in prev_search_results):
        ball_first_index: int = prev_search_results.index("BALL_FOUND")
        ball_last_index: int = (len(prev_search_results) -
                                prev_search_results[::-1].index("BALL_FOUND"))
        ball_mid_index: int = int((ball_last_index + ball_first_index) / 2)
        pins_index: int = prev_search_results.index("PINS_FOUND")

        # set angle between ball and pins for later usage
        path_info.ball_pins_angle = (abs(ball_mid_index - pins_index) *
                                     TURN_ANGLE)

        # look back at the ball
        if pins_index > ball_first_index:
            left: bool = False
            if path_info.ball_pins_angle > math.pi:
                # rotate around shorter arc
                path_info.ball_pins_angle = abs(
                    (2 * math.pi - path_info.ball_pins_angle) - 1.75)
                left = not left

            print("Correction:", path_info.ball_pins_angle)
            motor_driver.rotate(path_info.ball_pins_angle, left)

        # made rotation over 180deg
        if path_info.ball_pins_angle > math.pi:
            path_info.ball_pins_angle = abs(
                (2 * math.pi - path_info.ball_pins_angle) - 1.75)

        return True

    motor_driver.rotate(TURN_ANGLE)
    return False


def center_ball(image_results: list, motor_driver: MotorDriver) -> bool:
    """
    Center the ball in the robot's field of view.

    Args:
        image_results: List of recent image processing results
        motor_driver: Motor controller instance

    Returns:
        bool: True when ball is centered, False otherwise
    """
    if image_results[-1].has_ball:
        dist_from_mid: int = (image_results[-1].ball_position[0] -
                              IMAGE_CENTER_X)
        if abs(dist_from_mid) < X_THRESHOLD:
            # ball is centered, stop rotation
            motor_driver.rotate_non_blocking(False, False)
            return True
        elif dist_from_mid > 0:
            motor_driver.rotate_non_blocking(True, False)
        else:
            motor_driver.rotate_non_blocking(True, True)
    return False


def get_distance_of_pixel(depth_image: np.ndarray,
                          x_center: int, y_center: int) -> float:
    """
    Calculate average distance of a 7x7 pixel area around given coordinates.

    Args:
        depth_image: 2D array of depth values
        x_center: Center x-coordinate
        y_center: Center y-coordinate

    Returns:
        float: Average distance in meters
    """
    depth: float = 0.0

    for y in range(y_center - 3, y_center + 4):
        for x in range(x_center - 3, x_center + 4):
            depth += depth_image[y][x][2]

    return depth / (7 ** 2)


def get_pin_vectors(depth_image: np.ndarray,
                    k_matrix: np.ndarray,
                    scene_info: SceneInfo) -> list:
    """
    Convert pin positions from image coordinates to 3D camera space vectors.

    Args:
        depth_image: 2D array of depth values
        k_matrix: Camera intrinsic matrix
        scene_info: Scene information containing pin positions

    Returns:
        list: List of 3D vectors representing pin positions in camera space
    """
    vectors: list = []

    for pin_pos in scene_info.pin_positions:
        # (pixel - Cx) * (d/Fx)
        x_component: float = (pin_pos[0] - k_matrix[0][2]) * \
                            (depth_image[pin_pos[1]][pin_pos[0]][2] /
                             k_matrix[0][0])
        y_component: float = (pin_pos[1] - k_matrix[1][2]) * \
                             (depth_image[pin_pos[1]][pin_pos[0]][2] /
                              k_matrix[1][1])
        z_component: float = depth_image[pin_pos[1]][pin_pos[0]][2]

        # create pin vectors in camera space
        pin_vector: np.ndarray = np.array(
            [x_component, y_component, z_component])
        vectors.append(pin_vector)

    return vectors


def vector_norm(vector: np.ndarray) -> float:
    """Calculate Euclidean norm (magnitude) of a 2D vector."""
    return math.sqrt(vector[0] ** 2 + vector[1] ** 2)


if __name__ == "__main__":
    main()
