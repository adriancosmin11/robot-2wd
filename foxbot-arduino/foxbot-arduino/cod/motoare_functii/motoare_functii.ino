
#define M1INA 22
#define M1INB 23
#define M2INA 24
#define M2INB 25
#define PWM1 4
#define PWM2 5

void powerOffAllMotors()
{
digitalWrite(M1INA, LOW);
digitalWrite(M1INB, LOW);
digitalWrite(M2INA, LOW);
digitalWrite(M2INB, LOW);
}

void Forwards(int vel) //vel e procent
{
digitalWrite(M1INA, HIGH);
digitalWrite(M1INB, LOW);
digitalWrite(M2INA, HIGH);
digitalWrite(M2INB, LOW);
vel = vel/100*255;
analogWrite(PWM1,vel);
analogWrite(PWM2,vel);
}

void Backwards(int vel)
{ 
digitalWrite(M1INA, LOW);
digitalWrite(M1INB, HIGH);
digitalWrite(M2INA, LOW);
digitalWrite(M2INB, HIGH);
vel = vel/100*255;
analogWrite(PWM1,vel);
analogWrite(PWM2,vel);
}

void Right(int vel)
{
digitalWrite(M1INA, HIGH);
digitalWrite(M1INB, LOW);
digitalWrite(M2INA, HIGH);
digitalWrite(M2INB, LOW);
vel = vel/100*255;
analogWrite(PWM1,vel);
analogWrite(PWM2,vel/2); 
}

void Left(int vel)
{
digitalWrite(M1INA, HIGH);
digitalWrite(M1INB, LOW);
digitalWrite(M2INA, HIGH);
digitalWrite(M2INB, LOW);
vel = vel/100*255;
analogWrite(PWM1,vel/2);
analogWrite(PWM2,vel);  
}

void setup() {
pinMode(M1INA,OUTPUT);
pinMode(M1INB,OUTPUT);
pinMode(M2INA,OUTPUT);
pinMode(M2INB,OUTPUT);
pinMode(PWM1,OUTPUT);
pinMode(PWM2,OUTPUT);
powerOffAllMotors();
}

void loop() {
  Forwards(100);
  delay(2000);
  Backwards(100);
  delay(2000);
  Right(100);
  delay(2000);
  Left(100);
  delay(2000);
}
