#!/usr/bin/env python3
"""
Launch file for the 2WD robot on RPi5.

Starts:
  1. motor_driver_node  — listens to /cmd_vel and drives the motors
  2. (Optionally) cmd_vel_publisher for manual teleop

Usage:
  ros2 launch motor_control robot_bringup.launch.py
  ros2 launch motor_control robot_bringup.launch.py serial_port:=/dev/ttyACM1
"""

from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    serial_port_arg = DeclareLaunchArgument(
        'serial_port',
        default_value='/dev/ttyACM0',
        description='Serial port for the Arduino Mega'
    )

    motor_driver = Node(
        package='motor_control',
        executable='motor_driver_node',
        name='motor_driver_node',
        output='screen',
        parameters=[{
            'serial_port': LaunchConfiguration('serial_port'),
            'cmd_vel_timeout': 0.5,
        }],
    )

    return LaunchDescription([
        serial_port_arg,
        motor_driver,
    ])
