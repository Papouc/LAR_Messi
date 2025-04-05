"""
Motor Control System for TurtleBot Soccer Player

This module provides precise motor control for the TurtleBot, implementing:
- Velocity-controlled movement
- Smooth acceleration profiles
- Blocking and non-blocking rotation commands
- Odometry-based movement control
"""

import time
from robolab_turtlebot import Turtlebot, Rate

# Number of acceleration phases for smooth speed ramping
ACCEL_PHASES_CNT: int = 10


class MotorDriver:
    """Provides high-level motor control for TurtleBot soccer operations."""

    def __init__(self, turtle: Turtlebot, rotation_speed: float, forward_speed: float) -> None:
        """
        Initialize the MotorDriver with TurtleBot instance and default speeds.

        Args:
            turtle: TurtleBot robot instance
            rotation_speed: Default angular velocity (rad/s)
            forward_speed: Default linear velocity (m/s)
        """
        self._rotation_speed: float = rotation_speed
        self._forward_speed: float = forward_speed
        self._turtle: Turtlebot = turtle
        self._rate: Rate = Rate(10)  # Control rate at 10Hz

    def set_speed(self, rotation_speed: float, forward_speed: float) -> None:
        """Update motor speed parameters."""
        self._rotation_speed = rotation_speed
        self._forward_speed = forward_speed

    def move_forward_accel(self, travel_time: float) -> None:
        """
        Move forward with smooth acceleration profile.

        Implements gradual acceleration to target speed, maintains speed for
        specified duration, and includes automatic shutdown safety checks.
        """
        start_time: float = time.time()
        accel_start: float = time.time()
        speed_fw: float = 0.0  # Current forward speed
        speed_ag: float = 0.0  # Current angular speed
        stage_counter: int = 0  # Acceleration phase counter

        # Smooth acceleration phase
        while stage_counter < ACCEL_PHASES_CNT and (not self._turtle.is_shutting_down()):
            self._turtle.cmd_velocity(linear=speed_fw, angular=speed_ag)
            self._rate.sleep()

            if time.time() - start_time > 0.1:
                speed_fw += self._forward_speed / ACCEL_PHASES_CNT
                speed_ag += self._rotation_speed / ACCEL_PHASES_CNT
                start_time = time.time()
                stage_counter += 1

        accel_time: float = time.time() - accel_start

        # Constant velocity phase
        start_time = time.time()
        while not self._turtle.is_shutting_down():
            self._turtle.cmd_velocity(linear=self._forward_speed, angular=self._rotation_speed)
            self._rate.sleep()

            if time.time() - start_time >= travel_time + accel_time:
                break

    def move_forward(self, move_time: float) -> None:
        """Move forward at constant speed for specified duration."""
        start_time: float = time.time()

        while (time.time() - start_time < move_time) and (not self._turtle.is_shutting_down()):
            self._turtle.cmd_velocity(linear=self._forward_speed, angular=self._rotation_speed)
            self._rate.sleep()

    def rotate(self, degrees: float, left: bool = True) -> None:
        """
        Rotate by specified angle with blocking execution.

        Uses odometry to achieve precise rotation and automatically stops when
        target is reached.
        """
        self.reset_odometry_blocking()
        self._set_direction(left)

        while abs(self._turtle.get_odometry()[2]) < abs(degrees) and (not self._turtle.is_shutting_down()):
            self._turtle.cmd_velocity(linear=0.0, angular=self._rotation_speed)
            self._rate.sleep()

        self._turtle.cmd_velocity(linear=0.0, angular=0.0)
        self._turtle.reset_odometry()

    def _set_direction(self, left: bool) -> None:
        """Set rotation direction (internal helper method)."""
        self._rotation_speed = (abs(self._rotation_speed) if left else -abs(self._rotation_speed))

    def rotate_non_blocking(self, enabled: bool, left: bool) -> None:
        """Continuous rotation command (non-blocking)."""
        if not enabled:
            self._turtle.cmd_velocity(linear=0.0, angular=0.0)
            return

        self._set_direction(left)
        # Reduced speed for fine control
        self._turtle.cmd_velocity(linear=0.0, angular=self._rotation_speed / 1.75)

    def reset_odometry_blocking(self) -> None:
        """
        Reset odometry and verify successful reset.

        Blocks until odometry values are confirmed near zero by timeout safety.
        """
        self._turtle.reset_odometry()
        start_time: float = time.time()
        while ((abs(self._turtle.get_odometry()[0]) > 0.1 or
                abs(self._turtle.get_odometry()[1]) > 0.1 or
                abs(self._turtle.get_odometry()[2]) > 0.1) and
               (not self._turtle.is_shutting_down())):
            self._turtle.wait_for_odometry()

            if time.time() - start_time > 0.1:
                start_time = time.time()
                self._turtle.reset_odometry()
