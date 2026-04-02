#!/usr/bin/env python3
"""
ROS2 node that bridges /cmd_vel to the pyfirmata motor driver.

Subscribes to:
  /cmd_vel  (geometry_msgs/Twist)

Parameters:
  serial_port  (string, default '/dev/ttyACM0')
      USB serial device for the Arduino Mega.  Create a udev rule on the
      RPi5 for a stable symlink if the port number changes between boots.
  cmd_vel_timeout  (double, default 0.5)
      Seconds without a new /cmd_vel before motors are stopped (safety).

Usage:
  ros2 run motor_control motor_driver_node
  ros2 run motor_control motor_driver_node --ros-args -p serial_port:=/dev/ttyACM1
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

from motor_control.motor_driver import MotorDriver


class MotorDriverNode(Node):

    def __init__(self):
        super().__init__('motor_driver_node')

        # ── Declare parameters ──────────────────────────────────────
        self.declare_parameter('serial_port', '/dev/ttyACM0')
        self.declare_parameter('cmd_vel_timeout', 0.5)

        serial_port = self.get_parameter('serial_port').get_parameter_value().string_value
        self.cmd_vel_timeout = self.get_parameter('cmd_vel_timeout').get_parameter_value().double_value

        # ── Initialise hardware ─────────────────────────────────────
        self.get_logger().info(f'Connecting to Arduino on {serial_port} ...')
        try:
            self.driver = MotorDriver(serial_port)
            self.get_logger().info('Arduino connection established.')
        except Exception as e:
            self.get_logger().fatal(f'Failed to connect to Arduino: {e}')
            raise

        # ── Subscriber ──────────────────────────────────────────────
        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self._cmd_vel_callback,
            10,
        )

        # ── Safety watchdog timer ───────────────────────────────────
        self._last_cmd_time = self.get_clock().now()
        self.watchdog_timer = self.create_timer(0.1, self._watchdog_callback)

        self.get_logger().info('motor_driver_node is ready — listening on /cmd_vel')

    # ────────────────────────────────────────────────────────────────

    def _cmd_vel_callback(self, msg: Twist):
        """Forward every Twist to the motor driver (non-blocking)."""
        self._last_cmd_time = self.get_clock().now()
        self.driver.drive_continuous(msg.linear.x, msg.angular.z)

    def _watchdog_callback(self):
        """Stop motors if no cmd_vel received within timeout."""
        elapsed = (self.get_clock().now() - self._last_cmd_time).nanoseconds / 1e9
        if elapsed > self.cmd_vel_timeout:
            self.driver.power_off()

    # ────────────────────────────────────────────────────────────────

    def destroy_node(self):
        self.get_logger().info('Shutting down motor_driver_node — stopping motors.')
        self.driver.shutdown()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MotorDriverNode()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
