import turtle
import math
import time

from robolab_turtlebot import Turtlebot, Rate
from time import sleep

ACCEL_PHASES_CNT: int = 10

class MotorDriver:
    def __init__(self, turtle: Turtlebot, rotation_speed: float, forward_speed: float) -> None:
        self._rotation_speed: float = rotation_speed
        self._forward_speed: float = forward_speed
        self._turtle: Turtlebot = turtle
        self._rate: Rate = Rate(10)

    def set_speed(self, rotation_speed: float, forward_speed: float) -> None:
        self._rotation_speed = rotation_speed
        self._forward_speed = forward_speed

    def move_forward(self) -> None:

        start_time: float = time.time()
        speed_fw: float = 0.0
        speed_ag: float = 0.0
        stage_counter: int = 0

        # smooth acceleration
        while stage_counter < ACCEL_PHASES_CNT and (not self._turtle.is_shutting_down()):

            self._turtle.cmd_velocity(linear=speed_fw, angular=speed_ag)
            self._rate.sleep()

            if time.time() - start_time > 0.1:
                speed_fw += self._forward_speed / ACCEL_PHASES_CNT
                speed_ag += self._rotation_speed / ACCEL_PHASES_CNT
                start_time = time.time()
                stage_counter += 1

        while not self._turtle.is_shutting_down():
            print("Up to speed :D")
            self._turtle.cmd_velocity(linear=self._forward_speed, angular=self._rotation_speed)
            self._rate.sleep()

    def rotate(self, degrees: int, left: bool = True) -> None:
        while (abs(self._turtle.get_odometry()[0]) > 0.1 or abs(self._turtle.get_odometry()[1]) > 0.1 or abs(
                self._turtle.get_odometry()[2]) > 0.1) and (not self._turtle.is_shutting_down()):
            self._turtle.reset_odometry()

        if degrees > math.pi:
            degrees = abs((2*math.pi - degrees) - (math.pi / 9))
            left = not left

        self._set_direction(left)

        while abs(self._turtle.get_odometry()[2]) < abs(degrees) and (not self._turtle.is_shutting_down()):
            self._turtle.cmd_velocity(linear=0.0, angular=self._rotation_speed)
            self._rate.sleep()

        self._turtle.cmd_velocity(linear=0.0, angular=0.0)
        self._turtle.reset_odometry()

    def _set_direction(self, left: bool) -> None:
        self._rotation_speed = abs(self._rotation_speed) if left else -abs(self._rotation_speed)

    def rotate_non_blocking(self, enabled: bool, left: bool) -> None:
        if not enabled:
            self._turtle.cmd_velocity(linear=0.0, angular=0.0)
            return

        self._set_direction(left)
        self._turtle.cmd_velocity(linear=0.0, angular=self._rotation_speed / 2)
