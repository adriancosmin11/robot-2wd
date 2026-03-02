# Import necessary libraries
import pyfirmata
import time

# Setup communication with Arduino
board = pyfirmata.ArduinoMega('/dev/ttyACM0')
print("Communication Successfully started")

# Initialize pins
PWM1 = board.get_pin('d:3:p')
PWM2 = board.get_pin('d:5:p')
M1INA = board.get_pin('d:22:o')
M1INB = board.get_pin('d:23:o')
M2INA = board.get_pin('d:24:o')
M2INB = board.get_pin('d:25:o')

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
    # Ensure left motor is set to move forwards
    M1INA.write(1)
    M1INB.write(0)
    PWM1.write(vel)
    M2INA.write(0)
    M2INB.write(0)
    PWM2.write(0)

# Function to turn left
def left(vel):
    # Ensure right motor is set to move forwards
    M1INA.write(0)
    M1INB.write(0)
    PWM1.write(0)
    M2INA.write(1)
    M2INB.write(0)
    PWM2.write(vel)

# Main code block
if __name__ == '__main__':
    # Turn off all motors initially
    power_off_all_motors()

    try:
        # Main control loop
        while True:
            #forwards(0.5)
            #time.sleep(2)
            #print("done going forwards")
            #backwards(0.9)
            #time.sleep(2)
            #print("done going backwards")
            right(1)
            time.sleep(2)
            print("done going right")
            #left(0.1)
            #time.sleep(2)
            #print("done going left")
        
    except KeyboardInterrupt:
        print("\nExiting...")
        power_off_all_motors()
        board.exit()
