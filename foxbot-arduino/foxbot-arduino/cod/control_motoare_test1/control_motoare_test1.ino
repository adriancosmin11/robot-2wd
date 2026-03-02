// Motor control using H-bridge

// Define motor control pins
int ENA = 2;  // PWM pin for Motor A speed control
int IN1 = 3;  // Motor A input 1
int IN2 = 4;  // Motor A input 2
int IN3 = 5;  // Motor B input 1
int IN4 = 6;  // Motor B input 2
int ENB = 7;  // PWM pin for Motor B speed control

void setup() {
  // Set the motor control pins as outputs
  pinMode(ENA, OUTPUT);
  pinMode(IN1, OUTPUT);
  pinMode(IN2, OUTPUT);
  pinMode(IN3, OUTPUT);
  pinMode(IN4, OUTPUT);
  pinMode(ENB, OUTPUT);

  // Set motor A and B to run at maximum speed
  analogWrite(ENA, 255);

  // Set motor A to move forward
  digitalWrite(IN1, HIGH);
  digitalWrite(IN2, LOW);
  // Set motor B to move forward
  digitalWrite(IN3, HIGH);
  digitalWrite(IN4, LOW);

  // Set motor A and B to run at maximum speed
  analogWrite(ENA, 255);
  analogWrite(ENB, 255);
  
}

void loop() {

  // Run motors for 10 seconds
  delay(10000);  // 10 seconds delay

  // Stop motors
  analogWrite(ENA, 0);
  analogWrite(ENB, 0);
}

