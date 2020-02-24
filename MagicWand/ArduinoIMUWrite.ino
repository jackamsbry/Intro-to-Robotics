#include <Arduino_LSM6DS3.h>
const int buttonPin = 2;
const int ledPin = 13;

bool buttonState = 0;

float xAcc, yAcc, zAcc;
float xGyro, yGyro, zGyro;

void setup() {
// put your setup code here, to run once:
pinMode(buttonPin, INPUT);
pinMode(ledPin, OUTPUT);

Serial.begin(9600);
if (!IMU.begin()) {
Serial.println("Failed to initialize IMU");
// stop here if you can't access the IMU:
}
}

void loop() {
// put your main code here, to run repeatedly:
buttonState = digitalRead(buttonPin);
  if (IMU.accelerationAvailable() &&
  IMU.gyroscopeAvailable()) {
    // read accelerometer and gyrometer:
    IMU.readAcceleration(xAcc, yAcc, zAcc);
    IMU.readGyroscope(xGyro, yGyro, zGyro);
    // handle the results:
    xAcc = 10 * xAcc;
    yAcc = 10 * yAcc;
    zAcc = 10 * zAcc;
    // print the results:
    Serial.print(xAcc);
    Serial.print(",");
    Serial.print(yAcc);
    Serial.print(",");
    Serial.print(zAcc);
    Serial.print(",");
    Serial.print(xGyro);
    Serial.print(",");
    Serial.print(yGyro);
    Serial.print(",");
    Serial.println(zGyro);
   }  

delay(1);
}
