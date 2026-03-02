/// Modific pini pt robotul meu


#define M1INA 3
#define M1INB 4
#define M2INA 5
#define M2INB 6
#define PWM1 2
#define PWM2 7

void setup() {
  // put your setup code here, to run once:
pinMode(M1INA,OUTPUT);
pinMode(M1INB,OUTPUT);
pinMode(M2INA,OUTPUT);
pinMode(M2INB,OUTPUT);
pinMode(PWM1,OUTPUT);
pinMode(PWM2,OUTPUT);
Serial.begin(9600);
digitalWrite(M1INA, LOW);
digitalWrite(M1INB, LOW);
digitalWrite(M2INA, LOW);
digitalWrite(M2INB, LOW);
Serial.print("Motoareale sunt oprite \n");
}

void loop() {
  // put your main code here, to run repeatedly:
Serial.print("Rotile din stanga merg in fata... \n");
digitalWrite(M1INA, HIGH);
digitalWrite(M1INB, LOW);
digitalWrite(M2INA, LOW);
digitalWrite(M2INB, LOW);
analogWrite(PWM1,-);
analogWrite(PWM2,100);
delay(2000);
Serial.print("Rotile din stanga merg in spate... \n");
digitalWrite(M1INA, LOW);
digitalWrite(M1INB, HIGH);
digitalWrite(M2INA, LOW);
digitalWrite(M2INB, LOW);
analogWrite(PWM1,100);
analogWrite(PWM2,100);
delay(2000);
Serial.print("Motoarele se opresc... \n");
digitalWrite(M1INA, LOW);
digitalWrite(M1INB, LOW);
digitalWrite(M2INA, LOW);
digitalWrite(M2INB, LOW);
delay(2000);
exit(1);
}
