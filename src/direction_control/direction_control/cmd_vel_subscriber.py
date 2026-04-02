#!/usr/bin/env python3
"""
ROS2 cmd_vel subscriber node — receives Twist and drives the motors.

This is the ROS2 equivalent of the old direction_control/cmd_vel_subscriber.py.
It subscribes to /cmd_vel and forwards commands to the motor driver via
pyfirmata.

NOTE: In a clean architecture you should use *motor_driver_node* from the
motor_control package instead of this node.  This node exists for
backwards-compatibility with the original project layout and as a
standalone alternative if you want a single all-in-one node.

Parameters:
  serial_port  (string, default '/dev/ttyACM0')

Usage:
  ros2 run direction_control cmd_vel_subscriber
  ros2 run direction_control cmd_vel_subscriber --ros-args -p serial_port:=/dev/ttyACM1
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist

from motor_control.motor_driver import MotorDriver


class CmdVelSubscriber(Node):

    def __init__(self):
        super().__init__('cmd_vel_subscriber')

        self.declare_parameter('serial_port', '/dev/ttyACM0')
        serial_port = self.get_parameter('serial_port').get_parameter_value().string_value

        self.get_logger().info(f'Connecting to Arduino on {serial_port} ...')
        self.driver = MotorDriver(serial_port)
        self.get_logger().info('Arduino connection established.')

        self.subscription = self.create_subscription(
            Twist,
            '/cmd_vel',
            self._callback,
            10,
        )

        # Safety watchdog — stop if no messages for 0.5 s
        self.declare_parameter('cmd_vel_timeout', 0.5)
        self._timeout = self.get_parameter('cmd_vel_timeout').get_parameter_value().double_value
        self._last_msg_time = self.get_clock().now()
        self.create_timer(0.1, self._watchdog)

        self.get_logger().info('cmd_vel_subscriber ready — listening on /cmd_vel')

    def _callback(self, msg: Twist):
        self._last_msg_time = self.get_clock().now()
        self.driver.drive_continuous(msg.linear.x, msg.angular.z)

    def _watchdog(self):
        elapsed = (self.get_clock().now() - self._last_msg_time).nanoseconds / 1e9
        if elapsed > self._timeout:
            self.driver.power_off()

    def destroy_node(self):
        self.get_logger().info('Shutting down — stopping motors.')
        self.driver.shutdown()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = CmdVelSubscriber()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
