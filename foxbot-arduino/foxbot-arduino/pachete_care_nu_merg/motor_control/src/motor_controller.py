#!/usr/bin/python3

import rospy
from std_msgs.msg import Empty
import pyfirmata

# Define Arduino board port (adjust accordingly)
arduino_port = '/dev/ttyACM0'

# Define motor control pins
ENA = 2
IN1 = 3
IN2 = 4
IN3 = 5
IN4 = 6
ENB = 7

# Create Arduino board object
board = pyfirmata.Arduino(arduino_port)

# Set the motor control pins as outputs
for pin in [ENA, IN1, IN2, IN3, IN4, ENB]:
    board.digital[pin].mode = pyfirmata.OUTPUT

# Set motor A and B to run at maximum speed
board.digital[ENA].write(1)  # Use digital.write() for HIGH
board.digital[ENB].write(1)  # Use digital.write() for HIGH

# Set motor A to move forward
board.digital[IN1].write(1)
board.digital[IN2].write(0)

# Set motor B to move forward
board.digital[IN3].write(1)
board.digital[IN4].write(0)

def stop_motors_callback(msg):
    # Stop motors
    board.digital[ENA].write(0)
    board.digital[ENB].write(0)

if __name__ == '__main__':
    print("Starting motor_controller.py")
    rospy.init_node('motor_controller')
    
    # Subscribe to a ROS topic to stop motors
    rospy.Subscriber('/stop_motors', Empty, stop_motors_callback)

    rospy.spin()
    print("End of motor_controller.py")
