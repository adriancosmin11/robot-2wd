# Import necessary libraries
import pyfirmata
import time

# Function to turn off all motors
def power_off_all_motors():
    M1INA.write(0)
    M1INB.write(0)
    M2INA.write(0)
    M2INB.write(0)

# Function to move forward
def forwards(vel):
    # Ensure motors are set to move forwards
    M1INA.write(1)
    M1INB.write(0)
    M2INA.write(1)
    M2INB.write(0)
    PWM1.write(vel)
    PWM2.write(vel)

# Function to move backwards
def backwards(vel):
    # Ensure motors are set to move backwards
    M1INA.write(0)
    M1INB.write(1)
    M2INA.write(0)
    M2INB.write(1)
    PWM1.write(vel)
    PWM2.write(vel)

# Function to turn right
def right(vel):
    # Ensure motors are set to move forwards
    M1INA.write(1)
    M1INB.write(0)
    M2INA.write(0)
    M2INB.write(1)
    PWM1.write(vel)
    PWM2.write(vel/2)

# Function to turn left
def left(vel):
    # Ensure motors are set to move forwards
    M1INA.write(0)
    M1INB.write(1)  # Changed for left turn
    M2INA.write(1)
    M2INB.write(0)
    # Convert velocity from percentage to PWM value and ensure it's within byte range
    v = max(0, min(int(vel / 100 * 255), 255))
    # Set different velocities for turning
    PWM1.write(vel/2) 
    PWM2.write(vel)

# Main code block
if __name__ == '__main__':
    # Setup communication with Arduino
    board = pyfirmata.ArduinoMega('/dev/tty.usbmodem1301')
    print("Communication Successfully started")
    
    # Initialize pins
    PWM1 = board.get_pin('d:4:p')
    PWM2 = board.get_pin('d:5:p')
    M1INA = board.get_pin('d:22:o')
    M1INB = board.get_pin('d:23:o')
    M2INA = board.get_pin('d:24:o')
    M2INB = board.get_pin('d:25:o')

    # Turn off all motors initially
    power_off_all_motors()

    # Main control loop
    # while True:
    forwards(100)
    time.sleep(6)
    print("done going forwards")
    backwards(100)
    time.sleep(2)
    print("done going backwards")
    right(100)
    time.sleep(2)
    print("done going right")
    left(100)
    time.sleep(2)
    print("done going left")
    power_off_all_motors()
