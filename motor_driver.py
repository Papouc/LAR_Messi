import turtle

from robolab_turtlebot import Turtlebot, Rate
from time import sleep


class MotorDriver:
    def __init__(self, turtle: Turtlebot, rotation_speed: float, forward_speed: float):
        self.rotation_speed: float = rotation_speed
        self.forward_speed: float = forward_speed
        self._turtle: Turtlebot = turtle
        self._rate: Rate = Rate(10)

    def rotate(self, degrees: int):

        while (abs(self._turtle.get_odometry()[0]) > 0.1 or abs(self._turtle.get_odometry()[1]) > 0.1 or abs(
                self._turtle.get_odometry()[2]) > 0.1) and (not self._turtle.is_shutting_down()):
            self._turtle.reset_odometry()

        while abs(self._turtle.get_odometry()[2]) < abs(degrees) and (not self._turtle.is_shutting_down()):
            self._turtle.cmd_velocity(linear=0.0, angular=self.rotation_speed)
            self._rate.sleep()

        self._turtle.cmd_velocity(linear=0.0, angular=0.0)
        self._turtle.reset_odometry()
