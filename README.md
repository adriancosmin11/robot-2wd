# Foxbot 2WD — ROS2 on Raspberry Pi 5

A 2-wheel-drive robot controlled via ROS2 (Humble/Jazzy) running Ubuntu on a Raspberry Pi 5, communicating with an Arduino Mega over USB serial using pyfirmata.

## Architecture

```
┌──────────────────┐     /cmd_vel      ┌───────────────────┐    USB serial    ┌──────────────┐
│  Teleop / Nav2   │ ──── Twist ─────▶ │  motor_driver_node│ ── pyfirmata ──▶ │ Arduino Mega │ ── H-bridge ── Motors
│  cmd_vel_publisher│                   │  (motor_control)  │                  │              │
└──────────────────┘                    └───────────────────┘                  └──────────────┘
                                              ▲
                                              │ uses
                                     ┌────────┴─────────┐
                                     │  motor_driver.py  │  (ROS-agnostic hardware layer)
                                     └──────────────────┘
```

## Packages

| Package | Type | Description |
|---------|------|-------------|
| `motor_control` | ament_python | Motor driver node, hardware abstraction, launch files |
| `direction_control` | ament_python | cmd_vel publisher (teleop) and subscriber |
| `control_cu_functii` | ament_python | Standalone motor test sequence node |
| `my_slam_package` | ament_python | SLAM integration (rplidar + slam_toolbox) |

## Quick Start

```bash
# 1. Install pyfirmata (pip — not available as a ROS package)
pip install pyfirmata

# 2. Upload StandardFirmata to your Arduino Mega via the Arduino IDE
#    (File → Examples → Firmata → StandardFirmata)

# 3. Set up the udev rule for stable serial port (optional but recommended)
sudo cp src/motor_control/config/99-arduino-mega.rules /etc/udev/rules.d/
sudo udevadm control --reload-rules && sudo udevadm trigger

# 4. Build
cd ~/ros2_ws
colcon build --symlink-install
source install/setup.bash

# 5. Run the motor driver
ros2 launch motor_control robot_bringup.launch.py serial_port:=/dev/ttyACM0

# 6. In another terminal — manual teleop
source install/setup.bash
ros2 run direction_control cmd_vel_publisher

### Keyboard Mapping (Standard Layout)
| Key | Action |
|:---:|:---|
| **I** | Forward |
| **,** | Backward |
| **J** | Spin Left |
| **L** | Spin Right |
| **U** / **O** | Curve Forward Left / Right |
| **M** / **.** | Curve Backward Left / Right |
| **K** / **Space** | **STOP** |
| **ESC** | Quit Teleop |

### Speed Control
| Key | Action |
|:---:|:---|
| **Q** / **Z** | Increase / Decrease overall speed |
| **W** / **X** | Increase / Decrease linear speed only |
| **E** / **C** | Increase / Decrease angular speed only |
```

## Pin Mapping (Arduino Mega)

| Function | Pin | Mode |
|----------|-----|------|
| Left motor PWM | D3 | PWM |
| Right motor PWM | D5 | PWM |
| Left motor direction A | D22 | Digital Out |
| Left motor direction B | D23 | Digital Out |
| Right motor direction A | D24 | Digital Out |
| Right motor direction B | D25 | Digital Out |

## SLAM (Mapping with RPLidar)

The `my_slam_package` provides a complete SLAM pipeline using an RPLidar and `slam_toolbox`, with **Foxglove Studio** for browser-based visualization (no ROS install needed on the viewing machine).

### Prerequisites

```bash
# Install SLAM dependencies (if not already installed)
sudo apt install ros-jazzy-rplidar-ros ros-jazzy-slam-toolbox \
                 ros-jazzy-robot-state-publisher ros-jazzy-foxglove-bridge
```

### Running SLAM

```bash
# Terminal 1 (on RPi5): Start motors
ros2 launch motor_control robot_bringup.launch.py

# Terminal 2 (on RPi5): Start SLAM + Foxglove Bridge
ros2 launch my_slam_package slam.launch.py

# Terminal 3 (on RPi5 or remote): Teleop to drive around
ros2 run direction_control cmd_vel_publisher
```

### Visualizing in Browser (Foxglove)

1. Open **https://app.foxglove.dev** in any browser (laptop, tablet, phone)
2. Click **"Open connection"**
3. Select **"Foxglove WebSocket"**
4. Enter: `ws://<ROBOT_IP>:8765`
5. Add panels: **Map**, **3D**, **Raw Messages**, **Plot**, etc.

### Visualizing on your Laptop (RViz)

If you prefer to use RViz locally on your laptop:
```bash
ros2 launch my_slam_package slam.launch.py use_rviz:=true use_foxglove:=false
```

### Launch Arguments

| Argument | Default | Description |
|----------|---------|-------------|
| `lidar_serial_port` | `/dev/ttyUSB0` | Serial port for the RPLidar |
| `lidar_baudrate` | `115200` | Baud rate (115200 for A1/A2, 256000 for A3/S1) |
| `use_foxglove` | `true` | Start the Foxglove Bridge WebSocket server |
| `foxglove_port` | `8765` | WebSocket port for Foxglove Bridge |

### TF Tree

```
map ──(slam_toolbox)──▶ odom ──(static)──▶ base_footprint ──(URDF)──▶ base_link ──(URDF)──▶ laser
```

> **Note:** This robot has no wheel encoders, so `odom → base_footprint` is a static identity transform. All localization comes from slam_toolbox's scan matching. This works well indoors but pure in-place rotation may not be tracked perfectly.

### Saving the Map

```bash
# Save the current map (while slam_toolbox is running)
ros2 run nav2_map_server map_saver_cli -f ~/maps/my_map
```

## RPi5 Notes

- Ubuntu 24.04 or later recommended
- Arduino Mega appears as `/dev/ttyACM0` (use the udev rule above for `/dev/arduino_mega`)
- Ensure your user is in the `dialout` group: `sudo usermod -aG dialout $USER`
- RPi5 has better USB throughput than RPi3/4 — pyfirmata communication is more reliable
