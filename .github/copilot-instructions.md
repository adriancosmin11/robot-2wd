# Copilot Instructions — Foxbot 2WD (ROS2 / RPi5)

## Project Overview
2WD differential-drive robot. ROS2 (ament_python) on Raspberry Pi 5 (Ubuntu). Arduino Mega for motor H-bridge control via pyfirmata over USB serial.

## Architecture
- **`motor_control`** — Core package. Contains `motor_driver.py` (ROS-agnostic hardware abstraction) and `motor_driver_node.py` (ROS2 node subscribing to `/cmd_vel`).
- **`direction_control`** — Teleop package. `cmd_vel_publisher.py` reads from stdin and publishes `Twist` at 10 Hz. `cmd_vel_subscriber.py` is a standalone alternative that directly drives motors.
- **`control_cu_functii`** — Test harness. Runs a motor test sequence (forward/backward/turn).
- **`my_slam_package`** — SLAM integration (rplidar_ros + slam_toolbox). Placeholder, not yet populated.
- Data flow: `Twist` on `/cmd_vel` → `motor_driver_node` → `MotorDriver` → pyfirmata → Arduino Mega → H-bridge → DC motors.

## Key Conventions
- **All packages are `ament_python`** — no CMakeLists.txt. Build with `colcon build --symlink-install`.
- **Hardware abstraction is ROS-agnostic**: `motor_control/motor_driver.py` does NOT import rclpy. This allows standalone testing without ROS.
- **Node classes inherit `rclpy.node.Node`**. Each node file has a `main()` entry point registered in `setup.py` → `console_scripts`.
- **Safety watchdog**: Every node that drives motors has a timer that calls `power_off()` if no `/cmd_vel` arrives within `cmd_vel_timeout` (default 0.5 s).
- **Serial port is a ROS2 parameter** (`serial_port`, default `/dev/ttyACM0`). Override at launch: `--ros-args -p serial_port:=/dev/arduino_mega`.

## Pin Mapping (Arduino Mega)
PWM left=D3, PWM right=D5, M1INA=D22, M1INB=D23, M2INA=D24, M2INB=D25. pyfirmata uses float [0.0, 1.0] for PWM duty cycle.

## Build & Run
```bash
cd ~/ros2_ws && colcon build --symlink-install && source install/setup.bash
ros2 launch motor_control robot_bringup.launch.py            # start motor driver
ros2 run direction_control cmd_vel_publisher                  # teleop
ros2 run control_cu_functii motor_test_node                   # standalone test
ros2 run motor_control stop_motors_node                       # emergency stop
```

## RPi5 / Ubuntu Specifics
- Arduino Mega via USB → `/dev/ttyACM0`. Install udev rule from `motor_control/config/99-arduino-mega.rules` for `/dev/arduino_mega`.
- User must be in `dialout` group for serial access.
- `pyfirmata` is installed via pip (not a ROS dependency). Arduino must have **StandardFirmata** uploaded.

## When Editing
- If you change pin assignments, update both `motor_driver.py` **and** the table in `README.md`.
- If you add a new node, register it in `setup.py` → `entry_points` → `console_scripts`.
- The old ROS1 code lives in `src/robot-2wd/` for reference only — do NOT modify it.
- Robot physical constants (wheel size, speed calibration) are in `motor_driver.py` at the top.
