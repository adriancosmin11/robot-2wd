"""
Motor hardware abstraction layer for the 2WD robot.

Communicates with an Arduino Mega via pyfirmata over USB serial.
This module is ROS-agnostic so it can be tested independently.

Pin mapping (Arduino Mega):
  PWM1 = D3  (left motor speed,  PWM)
  PWM2 = D5  (right motor speed, PWM)
  M1INA = D22 (left motor  direction A, digital)
  M1INB = D23 (left motor  direction B, digital)
  M2INA = D24 (right motor direction A, digital)
  M2INB = D25 (right motor direction B, digital)

Velocity values for pyfirmata PWM are floats in [0.0, 1.0].
"""

import pyfirmata
import time
from math import pi


# ── Robot physical constants ────────────────────────────────────────
WHEEL_LENGTH_CM = 25.15           # wheel circumference (cm)
WHEEL_DISTANCE_CM = 30.0          # distance between the two wheels (cm)
FULL_TURN_CIRCUMFERENCE = WHEEL_DISTANCE_CM * pi * 2  # circumference of turning circle
VELOCITY_100_CM_S = 26.0          # measured speed at PWM=1.0 (cm/s) — calibrate on your surface!


class MotorDriver:
    """Thin wrapper around pyfirmata that exposes high-level motor primitives."""

    def __init__(self, serial_port: str = '/dev/ttyACM0'):
        """
        Open serial connection to the Arduino Mega.

        Args:
            serial_port: Serial device path. On RPi5 with Ubuntu the Arduino
                         Mega typically shows up as /dev/ttyACM0.  If you use
                         a USB hub it may become /dev/ttyACM1 — pass the
                         correct path or create a udev rule for a stable symlink.
        """
        self.board = pyfirmata.ArduinoMega(serial_port)

        # PWM pins (speed control, values 0.0-1.0)
        self.pwm_left = self.board.get_pin('d:3:p')
        self.pwm_right = self.board.get_pin('d:5:p')

        # Direction pins (digital output)
        self.m1_ina = self.board.get_pin('d:22:o')
        self.m1_inb = self.board.get_pin('d:23:o')
        self.m2_ina = self.board.get_pin('d:24:o')
        self.m2_inb = self.board.get_pin('d:25:o')

        # Start with motors off
        self.power_off()

    # ── Low-level helpers ───────────────────────────────────────────

    def power_off(self):
        """Immediately stop both motors (coast stop)."""
        self.m1_ina.write(0)
        self.m1_inb.write(0)
        self.m2_ina.write(0)
        self.m2_inb.write(0)
        self.pwm_left.write(0.0)
        self.pwm_right.write(0.0)

    def _set_direction(self, left_fwd: bool, right_fwd: bool):
        """Set the H-bridge direction bits for each motor."""
        self.m1_ina.write(1 if left_fwd else 0)
        self.m1_inb.write(0 if left_fwd else 1)
        self.m2_ina.write(1 if right_fwd else 0)
        self.m2_inb.write(0 if right_fwd else 1)

    def _set_speed(self, left_vel: float, right_vel: float):
        """Write PWM duty cycle (0.0-1.0) for each motor."""
        self.pwm_left.write(max(0.0, min(left_vel, 1.0)))
        self.pwm_right.write(max(0.0, min(right_vel, 1.0)))

    # ── High-level movement primitives ──────────────────────────────

    def forwards(self, vel: float = 1.0):
        """Drive both motors forward at the given velocity (0.0-1.0)."""
        self._set_direction(left_fwd=True, right_fwd=True)
        self._set_speed(vel, vel)

    def backwards(self, vel: float = 1.0):
        """Drive both motors backward at the given velocity (0.0-1.0)."""
        self._set_direction(left_fwd=False, right_fwd=False)
        self._set_speed(vel, vel)

    def turn_right(self, vel: float = 1.0):
        """Pivot right: left motor forward, right motor stopped."""
        self.m1_ina.write(1)
        self.m1_inb.write(0)
        self.m2_ina.write(0)
        self.m2_inb.write(0)
        self._set_speed(vel, 0.0)

    def turn_left(self, vel: float = 1.0):
        """Pivot left: right motor forward, left motor stopped."""
        self.m1_ina.write(0)
        self.m1_inb.write(0)
        self.m2_ina.write(1)
        self.m2_inb.write(0)
        self._set_speed(0.0, vel)

    # ── cmd_vel-style movement (linear + angular) ───────────────────

    def move(self, linear_cm: float, angular_rad: float):
        """
        Execute a movement command derived from cmd_vel Twist messages.

        This replicates the original `move_motors()` kinematics:
        - ``linear_cm``  — distance to travel (cm). Positive = forward, negative = backward.
        - ``angular_rad`` — turning bias (radians). Positive = turn left, negative = turn right.

        The function is *blocking*: it drives the motors for the computed
        duration and then stops them.  For continuous cmd_vel streaming the
        caller should use ``drive_continuous()`` instead.
        """
        self.power_off()

        if linear_cm == 0.0:
            return  # nothing to do

        # Direction
        going_forward = linear_cm > 0
        self._set_direction(left_fwd=going_forward, right_fwd=going_forward)

        # Compute differential velocity for turning
        vel_left = 1.0
        vel_right = 1.0

        if angular_rad != 0.0:
            pct = abs(angular_rad) * 100.0 / (2.0 * pi)           # % of full circle
            arc_equiv = pct * FULL_TURN_CIRCUMFERENCE / 100.0       # equivalent arc (cm)
            slow_factor = arc_equiv / (abs(linear_cm) + arc_equiv)  # [0, 1)

            if angular_rad >= 0:
                vel_left -= slow_factor   # turning left → slow down left wheel
            else:
                vel_right -= slow_factor  # turning right → slow down right wheel

        vel_left = max(0.0, vel_left)
        vel_right = max(0.0, vel_right)

        time_to_wait = abs(linear_cm) / ((1.0 - min(vel_left, vel_right)) * VELOCITY_100_CM_S
                                          if min(vel_left, vel_right) < 1.0
                                          else VELOCITY_100_CM_S)

        self._set_speed(vel_left, vel_right)
        time.sleep(time_to_wait)
        self.power_off()

    def drive_continuous(self, linear_x: float, angular_z: float):
        """
        Non-blocking differential drive from a Twist message.

        Used for continuous ``/cmd_vel`` streaming (e.g. from teleop or nav2).
        - ``linear_x``  — m/s  (positive = forward)
        - ``angular_z``  — rad/s (positive = counter-clockwise)

        Call ``power_off()`` when no new command arrives within a timeout.
        """
        if linear_x == 0.0 and angular_z == 0.0:
            self.power_off()
            return

        # Simple differential drive: v_left = v - ω·L/2, v_right = v + ω·L/2
        wheel_base_m = WHEEL_DISTANCE_CM / 100.0
        v_left = linear_x - angular_z * wheel_base_m / 2.0
        v_right = linear_x + angular_z * wheel_base_m / 2.0

        # Normalise to [-1, 1] range based on max expected speed (m/s)
        max_speed = VELOCITY_100_CM_S / 100.0  # convert cm/s → m/s
        norm_left = max(-1.0, min(v_left / max_speed, 1.0))
        norm_right = max(-1.0, min(v_right / max_speed, 1.0))

        # Set direction per wheel
        self.m1_ina.write(1 if norm_left >= 0 else 0)
        self.m1_inb.write(0 if norm_left >= 0 else 1)
        self.m2_ina.write(1 if norm_right >= 0 else 0)
        self.m2_inb.write(0 if norm_right >= 0 else 1)

        self._set_speed(abs(norm_left), abs(norm_right))

    def shutdown(self):
        """Stop motors and close the serial connection."""
        self.power_off()
        self.board.exit()
