#!/usr/bin/env python3
"""
ROS2 node for standalone motor testing.

Replaces the old ROS1 control_cu_functii/run_node.py.
Runs a simple sequence (forward → backward → right → left) using the
shared MotorDriver from the motor_control package, then shuts down.

Parameters:
  serial_port  (string, default '/dev/ttyACM0')

Usage:
  ros2 run control_cu_functii motor_test_node
  ros2 run control_cu_functii motor_test_node --ros-args -p serial_port:=/dev/ttyACM1
"""

import time
import rclpy
from rclpy.node import Node

from motor_control.motor_driver import MotorDriver


class MotorTestNode(Node):

    def __init__(self):
        super().__init__('motor_test_node')

        self.declare_parameter('serial_port', '/dev/ttyACM0')
        serial_port = self.get_parameter('serial_port').get_parameter_value().string_value

        self.get_logger().info(f'Connecting to Arduino on {serial_port} ...')
        self.driver = MotorDriver(serial_port)
        self.get_logger().info('Arduino connection established.')

        # Run the test sequence in a one-shot timer so the node spins properly
        self.create_timer(0.5, self._run_test_sequence)
        self._test_done = False

    def _run_test_sequence(self):
        if self._test_done:
            return
        self._test_done = True

        logger = self.get_logger()

        try:
            logger.info('TEST: forwards at 50% for 2 s')
            self.driver.forwards(0.5)
            time.sleep(2.0)

            logger.info('TEST: backwards at 50% for 2 s')
            self.driver.backwards(0.5)
            time.sleep(2.0)

            logger.info('TEST: turn right at 80% for 2 s')
            self.driver.turn_right(0.8)
            time.sleep(2.0)

            logger.info('TEST: turn left at 80% for 2 s')
            self.driver.turn_left(0.8)
            time.sleep(2.0)

            logger.info('TEST: move(30 cm, 1.0 rad) — forward with left turn')
            self.driver.move(30.0, 1.0)

            logger.info('TEST COMPLETE — stopping motors.')
        except Exception as e:
            logger.error(f'Test failed: {e}')
        finally:
            self.driver.power_off()

        # Shut the node down after the test
        raise SystemExit

    def destroy_node(self):
        self.driver.shutdown()
        super().destroy_node()


def main(args=None):
    rclpy.init(args=args)
    node = MotorTestNode()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
