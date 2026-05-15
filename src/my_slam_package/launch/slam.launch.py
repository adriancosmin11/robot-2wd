#!/usr/bin/env python3
"""
SLAM launch file for the Foxbot 2WD robot.

Launches the full SLAM pipeline:
  1. robot_state_publisher  — publishes URDF → TF (base_link → laser)
  2. Static TF: odom → base_footprint (identity — no wheel encoders)
  3. rplidar_ros             — LaserScan on /scan
  4. slam_toolbox            — online async SLAM (map → odom via scan matching)
  5. foxglove_bridge         — WebSocket bridge for Foxglove Studio visualization

The resulting TF tree:
  map ──(slam_toolbox)──→ odom ──(static)──→ base_footprint ──(URDF)──→ base_link ──(URDF)──→ laser

Visualization:
  Open https://app.foxglove.dev in any browser, then:
    → Open connection → Foxglove WebSocket → ws://<ROBOT_IP>:8765

Usage:
  # Default (RPLidar on /dev/ttyUSB0):
  ros2 launch my_slam_package slam.launch.py

  # Custom serial ports:
  ros2 launch my_slam_package slam.launch.py lidar_serial_port:=/dev/rplidar

  # Disable Foxglove bridge (e.g. for headless mapping):
  ros2 launch my_slam_package slam.launch.py use_foxglove:=false
"""

import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import DeclareLaunchArgument, LogInfo
from launch.conditions import IfCondition
from launch.substitutions import LaunchConfiguration
from launch_ros.actions import Node


def generate_launch_description():
    pkg_share = get_package_share_directory('my_slam_package')

    # ── Launch Arguments ─────────────────────────────────────────────
    lidar_serial_port_arg = DeclareLaunchArgument(
        'lidar_serial_port',
        default_value='/dev/ttyUSB0',
        description='Serial port for the RPLidar',
    )

    lidar_baudrate_arg = DeclareLaunchArgument(
        'lidar_baudrate',
        default_value='115200',
        description='Baud rate for the RPLidar (115200 for A1/A2, 256000 for A3/S1)',
    )

    use_foxglove_arg = DeclareLaunchArgument(
        'use_foxglove',
        default_value='true',
        description='Start Foxglove Bridge for browser-based visualization',
    )

    foxglove_port_arg = DeclareLaunchArgument(
        'foxglove_port',
        default_value='8765',
        description='WebSocket port for Foxglove Bridge',
    )

    use_rviz_arg = DeclareLaunchArgument(
        'use_rviz',
        default_value='false',
        description='Start RViz2 for visualization',
    )

    # ── Paths ────────────────────────────────────────────────────────
    urdf_file = os.path.join(pkg_share, 'urdf', 'foxbot_2wd.urdf')
    slam_params_file = os.path.join(pkg_share, 'config', 'slam_toolbox_params.yaml')
    rviz_config_file = os.path.join(pkg_share, 'rviz', 'slam_view.rviz')

    # Read URDF content for robot_state_publisher
    with open(urdf_file, 'r') as f:
        robot_description_content = f.read()

    # ── 1. Robot State Publisher ─────────────────────────────────────
    # Publishes the URDF joint transforms to /tf (base_link → laser, etc.)
    robot_state_publisher_node = Node(
        package='robot_state_publisher',
        executable='robot_state_publisher',
        name='robot_state_publisher',
        output='screen',
        parameters=[{
            'robot_description': robot_description_content,
            'use_sim_time': False,
        }],
    )

    # ── 2. Static Transform: odom → base_footprint ──────────────────
    # Since we have NO wheel encoders, we publish an identity transform
    # from odom → base_footprint.  slam_toolbox provides the map → odom
    # transform via scan matching, which effectively becomes our sole
    # localization source.
    #
    # This is the standard approach for encoder-less robots using
    # slam_toolbox — the "odom" frame exists only as a required
    # intermediate in the TF tree.
    static_odom_tf = Node(
        package='tf2_ros',
        executable='static_transform_publisher',
        name='static_odom_publisher',
        output='screen',
        arguments=[
            '--x', '0.0',
            '--y', '0.0',
            '--z', '0.0',
            '--roll', '0.0',
            '--pitch', '0.0',
            '--yaw', '0.0',
            '--frame-id', 'odom',
            '--child-frame-id', 'base_footprint',
        ],
    )

    # ── 3. RPLidar Driver ────────────────────────────────────────────
    rplidar_node = Node(
        package='rplidar_ros',
        executable='rplidar_composition',
        name='rplidar_composition',
        output='screen',
        parameters=[{
            'serial_port': LaunchConfiguration('lidar_serial_port'),
            'serial_baudrate': 115200,
            'frame_id': 'laser',
            'inverted': False,
            'angle_compensate': True,
        }],
    )

    # ── 4. SLAM Toolbox (Online Async) ───────────────────────────────
    slam_toolbox_node = Node(
        package='slam_toolbox',
        executable='async_slam_toolbox_node',
        name='slam_toolbox',
        output='screen',
        parameters=[
            slam_params_file,
            {'use_sim_time': False},
        ],
    )

    # ── 5. Foxglove Bridge ───────────────────────────────────────────
    # Exposes all ROS 2 topics/services/params over a WebSocket so you
    # can visualize from any browser at https://app.foxglove.dev
    #
    # Connect with:  ws://<ROBOT_IP>:8765
    #
    # Advantages over RViz:
    #   - No ROS install needed on the viewing machine
    #   - Works from any device (laptop, tablet, phone)
    #   - Rich built-in panels: map, 3D, laser scan, plots, diagnostics
    #   - Shareable layouts
    foxglove_bridge_node = Node(
        package='foxglove_bridge',
        executable='foxglove_bridge',
        name='foxglove_bridge',
        output='screen',
        parameters=[{
            'port': LaunchConfiguration('foxglove_port'),
            'address': '0.0.0.0',
            'send_buffer_limit': 10000000,
            'num_threads': 2,
        }],
        condition=IfCondition(LaunchConfiguration('use_foxglove')),
    )

    foxglove_info = LogInfo(
        msg='Foxglove Bridge started — open https://app.foxglove.dev '
            'and connect to ws://<ROBOT_IP>:8765',
        condition=IfCondition(LaunchConfiguration('use_foxglove')),
    )

    # ── 6. RViz2 ─────────────────────────────────────────────────────
    rviz_node = Node(
        package='rviz2',
        executable='rviz2',
        name='rviz2',
        arguments=['-d', rviz_config_file],
        condition=IfCondition(LaunchConfiguration('use_rviz')),
    )

    # ── Assemble Launch Description ──────────────────────────────────
    return LaunchDescription([
        lidar_serial_port_arg,
        lidar_baudrate_arg,
        use_foxglove_arg,
        foxglove_port_arg,
        use_rviz_arg,
        robot_state_publisher_node,
        static_odom_tf,
        rplidar_node,
        slam_toolbox_node,
        foxglove_bridge_node,
        foxglove_info,
        rviz_node,
    ])
