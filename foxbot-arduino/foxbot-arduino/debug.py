import pyfirmata
import time

board = pyfirmata.ArduinoMega('/dev/ttyACM0')
print("Communication Successfully started")

# Define PWM pins on Arduino Mega
pwm_pins = range (2, 13)

# Set mode to PWM and write maximum duty cycle
for pin in pwm_pins:
    board.digital[pin].mode = 3  # Set to PWM mode
    board.digital[pin].write(100)  # Set to high (maximum duty cycle)

# To keep the program running and allow PWM output
try:
    while True:
        time.sleep(1)  # Sleep for a second
except KeyboardInterrupt:
    # Reset all pins when stopping the script
    for pin in pwm_pins:
        board.digital[pin].write(0)
    board.exit()
    print("Program terminated and pins reset.")
