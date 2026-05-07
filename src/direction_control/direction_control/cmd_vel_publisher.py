#!/usr/bin/env python3
"""
ROS2 keyboard teleop node — publishes Twist on /cmd_vel.

Replaces the old ROS1 cmd_vel_publisher.py.  Reads linear.x and angular.z
from stdin and publishes them at 10 Hz until new values are entered.

Usage:
  ros2 run direction_control cmd_vel_publisher
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

import sys
import threading
import termios
import tty


# ── Velocity presets (tune these for your robot) ────────────────────
LINEAR_VEL = 0.5    # m/s (default was 0.2)
ANGULAR_VEL = 2.0   # rad/s (default was 1.0)
CURVE_ANGULAR = 1.0  # rad/s for diagonal moves

# Key → (linear.x, angular.z)
KEY_BINDINGS = {
    'i': ( LINEAR_VEL,  0.0),           # forward
    ',': (-LINEAR_VEL,  0.0),           # backward
    'j': ( 0.0,         ANGULAR_VEL),   # spin left  (CCW)
    'l': ( 0.0,        -ANGULAR_VEL),   # spin right (CW)
    'u': ( LINEAR_VEL,  CURVE_ANGULAR), # curve forward-left
    'o': ( LINEAR_VEL, -CURVE_ANGULAR), # curve forward-right
    'm': (-LINEAR_VEL, -CURVE_ANGULAR), # curve backward-left
    '.': (-LINEAR_VEL,  CURVE_ANGULAR), # curve backward-right
    'k': ( 0.0,  0.0),                 # stop
    ' ': ( 0.0,  0.0),                 # stop (spacebar)
}

USAGE_TEXT = """
─────────────────────────────────
  Standard Teleop — Foxbot 2WD
─────────────────────────────────
    U  I  O
    J  K  L
    M  ,  .

  I/, : Forward / Backward
  J/L : Spin Left / Spin Right
  U/O : Curve Forward-Left / Right
  M/. : Curve Backward-Left / Right
  K   : STOP
  ESC : Quit
─────────────────────────────────
"""


class CmdVelPublisher(Node):

    def __init__(self):
        super().__init__('cmd_vel_publisher')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self._linear_x = 0.0
        self._angular_z = 0.0
        self._lock = threading.Lock()
        self._running = True

        # Publish at 10 Hz so the motor driver watchdog stays happy
        self.timer = self.create_timer(0.1, self._publish)

        # Spawn a background thread for blocking key reads
        self._input_thread = threading.Thread(target=self._read_keys, daemon=True)
        self._input_thread.start()

        self.get_logger().info('Teleop ready — use U-I-O / J-K-L to drive.')
        print(USAGE_TEXT)

    # ── Terminal raw-mode key reader ────────────────────────────────

    @staticmethod
    def _get_key():
        """Read a single keypress without waiting for Enter (Linux only)."""
        fd = sys.stdin.fileno()
        old_settings = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            ch = sys.stdin.read(1)
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old_settings)
        return ch

    def _read_keys(self):
        """Background thread: read keys and update velocity state."""
        global LINEAR_VEL, ANGULAR_VEL, CURVE_ANGULAR
        try:
            while self._running and rclpy.ok():
                key = self._get_key()

                # ESC → signal shutdown
                if ord(key) == 27:
                    self.get_logger().info('ESC pressed — shutting down.')
                    self._running = False
                    with self._lock:
                        self._linear_x = 0.0
                        self._angular_z = 0.0
                    rclpy.shutdown()
                    break

                key = key.lower()

                # Speed control
                if key == 'q':
                    LINEAR_VEL *= 1.1
                    ANGULAR_VEL *= 1.1
                    self.get_logger().info(f'Speeds increased: linear={LINEAR_VEL:.2f}, angular={ANGULAR_VEL:.2f}')
                elif key == 'z':
                    LINEAR_VEL *= 0.9
                    ANGULAR_VEL *= 0.9
                    self.get_logger().info(f'Speeds decreased: linear={LINEAR_VEL:.2f}, angular={ANGULAR_VEL:.2f}')
                elif key == 'w':
                    LINEAR_VEL *= 1.1
                    self.get_logger().info(f'Linear speed increased: {LINEAR_VEL:.2f}')
                elif key == 'x':
                    LINEAR_VEL *= 0.9
                    self.get_logger().info(f'Linear speed decreased: {LINEAR_VEL:.2f}')
                elif key == 'e':
                    ANGULAR_VEL *= 1.1
                    self.get_logger().info(f'Angular speed increased: {ANGULAR_VEL:.2f}')
                elif key == 'c':
                    ANGULAR_VEL *= 0.9
                    self.get_logger().info(f'Angular speed decreased: {ANGULAR_VEL:.2f}')

                # Movement control
                elif key in KEY_BINDINGS:
                    # Refresh values based on current presets
                    if key == 'i': lx, az = LINEAR_VEL, 0.0
                    elif key == ',': lx, az = -LINEAR_VEL, 0.0
                    elif key == 'j': lx, az = 0.0, ANGULAR_VEL   # Pure Spin Left
                    elif key == 'l': lx, az = 0.0, -ANGULAR_VEL  # Pure Spin Right
                    elif key == 'u': lx, az = LINEAR_VEL, ANGULAR_VEL / 2.0
                    elif key == 'o': lx, az = LINEAR_VEL, -ANGULAR_VEL / 2.0
                    elif key == 'm': lx, az = -LINEAR_VEL, -ANGULAR_VEL / 2.0
                    elif key == '.': lx, az = -LINEAR_VEL, ANGULAR_VEL / 2.0
                    elif key == 'k' or key == ' ': lx, az = 0.0, 0.0
                    
                    with self._lock:
                        self._linear_x = lx
                        self._angular_z = az
                    self.get_logger().info(
                        f'cmd_vel: linear.x={lx:+.2f}  angular.z={az:+.2f}'
                    )
        except Exception as e:
            self.get_logger().error(f'Error reading keys: {e}')

    # ── Timer callback — continuous publisher ───────────────────────

    def _publish(self):
        msg = Twist()
        with self._lock:
            msg.linear.x = self._linear_x
            msg.angular.z = self._angular_z
        self.publisher.publish(msg)


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelPublisher()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        # Ensure motors stop on exit
        stop_msg = Twist()
        node.publisher.publish(stop_msg)
        node.destroy_node()
        if rclpy.ok():
            rclpy.shutdown()


if __name__ == '__main__':
    main()
