import pyfirmata
import time

# Initialize Arduino board
board = pyfirmata.ArduinoMega('/dev/ttyACM0')  # Adjust port as necessary
print("Communication Successfully started")

# Set pin modes
PWM1 = board.get_pin('d:3:p')
PWM2 = board.get_pin('d:5:p')
M1INA = board.get_pin('d:22:o')
M1INB = board.get_pin('d:23:o')
M2INA = board.get_pin('d:24:o')
M2INB = board.get_pin('d:25:o')

# Initialize pins
M1INA.write(0)
M1INB.write(0)
M2INA.write(0)
M2INB.write(0)
PWM1.write(0)
PWM2.write(0)

print("Motoarele sunt oprite")

try:
    while True:
        print("Rotile din stanga merg in fata...")
        M1INA.write(1)
        M1INB.write(0)
        M2INA.write(0)
        M2INB.write(0)
        PWM1.write(0)  # Adjust PWM values as needed
        PWM2.write(1)  # Adjust PWM values as needed
        time.sleep(300)

        '''print("Rotile din stanga merg in spate...")
        M1INA.write(0)
        M1INB.write(1)
        M2INA.write(0)
        M2INB.write(0)
        PWM1.write(100)  # Adjust PWM values as needed
        PWM2.write(100)  # Adjust PWM values as needed
        time.sleep(2)

        print("Motoarele se opresc...")
        M1INA.write(0)
        M1INB.write(0)
        M2INA.write(0)
        M2INB.write(0)
        time.sleep(2)'''

except KeyboardInterrupt:
    print("\nExiting...")
    board.exit()
