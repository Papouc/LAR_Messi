import turtle
import math

from robolab_turtlebot import Turtlebot, Rate
from time import sleep


class MotorDriver:
    def __init__(self, turtle: Turtlebot, rotation_speed: float, forward_speed: float) -> None:
        self.rotation_speed: float = rotation_speed
        self.forward_speed: float = forward_speed
        self._turtle: Turtlebot = turtle
        self._rate: Rate = Rate(10)

    def rotate(self, degrees: int, left: bool = True) -> None:
        while (abs(self._turtle.get_odometry()[0]) > 0.1 or abs(self._turtle.get_odometry()[1]) > 0.1 or abs(
                self._turtle.get_odometry()[2]) > 0.1) and (not self._turtle.is_shutting_down()):
            self._turtle.reset_odometry()

        if degrees > math.pi:
            degrees = abs((2*math.pi - degrees) - (math.pi / 9))
            left = not left

        self._set_direction(left)

        while abs(self._turtle.get_odometry()[2]) < abs(degrees) and (not self._turtle.is_shutting_down()):
            self._turtle.cmd_velocity(linear=0.0, angular=self.rotation_speed)
            self._rate.sleep()

        self._turtle.cmd_velocity(linear=0.0, angular=0.0)
        self._turtle.reset_odometry()

    def _set_direction(self, left: bool) -> None:
        self.rotation_speed = abs(self.rotation_speed) if left else -abs(self.rotation_speed)

    def rotate_non_blocking(self, enabled: bool, left: bool) -> None:
        if not enabled:
            self._turtle.cmd_velocity(linear=0.0, angular=0.0)
            return

        self._set_direction(left)
        self._turtle.cmd_velocity(linear=0.0, angular=self.rotation_speed / 2)
