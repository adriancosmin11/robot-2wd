#!/usr/bin/env python3
"""
ROS2 node that publishes an Empty message on /stop_motors to signal an
emergency stop.  The motor_driver_node does not subscribe to this topic
directly — instead this node publishes a zero-velocity Twist on /cmd_vel
which the motor_driver_node already handles.

Usage:
  ros2 run motor_control stop_motors_node
"""

import rclpy
from rclpy.node import Node
from geometry_msgs.msg import Twist


class StopMotorsNode(Node):

    def __init__(self):
        super().__init__('stop_motors_node')
        self.publisher = self.create_publisher(Twist, '/cmd_vel', 10)

        # Give the publisher a moment to be discovered by the graph
        self.create_timer(0.5, self._publish_stop)
        self.get_logger().info('stop_motors_node: will publish zero-velocity Twist on /cmd_vel')

    def _publish_stop(self):
        stop_msg = Twist()  # all fields default to 0.0
        self.publisher.publish(stop_msg)
        self.get_logger().info('Published STOP command on /cmd_vel')
        # Only need to publish once; shut down after a short delay
        self.create_timer(1.0, self._shutdown)

    def _shutdown(self):
        raise SystemExit


def main(args=None):
    rclpy.init(args=args)
    node = StopMotorsNode()
    try:
        rclpy.spin(node)
    except SystemExit:
        pass
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == '__main__':
    main()
