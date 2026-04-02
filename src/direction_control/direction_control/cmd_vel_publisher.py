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


class CmdVelPublisher(Node):

    def __init__(self):
        super().__init__('cmd_vel_publisher')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        self._linear_x = 0.0
        self._angular_z = 0.0
        self._lock = threading.Lock()

        # Publish at 10 Hz so the motor driver watchdog stays happy
        self.timer = self.create_timer(0.1, self._publish)

        # Spawn a background thread for blocking stdin input
        self._input_thread = threading.Thread(target=self._read_input, daemon=True)
        self._input_thread.start()

        self.get_logger().info(
            'cmd_vel_publisher ready.\n'
            '  Enter "<linear_x> <angular_z>" (e.g. "0.2 0.0").\n'
            '  Press Ctrl+C to quit.'
        )

    def _read_input(self):
        """Blocking loop that reads velocity from stdin."""
        try:
            while rclpy.ok():
                line = input('cmd_vel > ')
                parts = line.strip().split()
                if len(parts) != 2:
                    print('  ⚠  Enter exactly two numbers: <linear_x> <angular_z>')
                    continue
                try:
                    lx, az = float(parts[0]), float(parts[1])
                except ValueError:
                    print('  ⚠  Invalid numbers. Try again.')
                    continue
                with self._lock:
                    self._linear_x = lx
                    self._angular_z = az
                self.get_logger().info(f'Set cmd_vel: linear.x={lx:.3f}, angular.z={az:.3f}')
        except (EOFError, KeyboardInterrupt):
            pass

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
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
