void setup() {
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  Serial.begin(9600); // Start serial communication at 9600 baud rate
}

void loop() {
  if (Serial.available() > 0) {
    char receivedChar = Serial.read(); // Read the incoming character
    if (receivedChar == 'l') { // If the character is 'l'
      turnMotorOnForDuration(500, LOW); // Turn motor left for 0.5 seconds
    } else if (receivedChar == 'r') { // If the character is 'r'
      turnMotorOnForDuration(500, HIGH); // Turn motor right for 0.5 seconds
    } else if (receivedChar == 's') { // If the character is 's'
      stopMotor(); // Stop the motor
    }
  } else {
    for (int i = 0; i < 11; i++) {
      turnMotorOnForDuration(250, LOW); // Turn motor left for 0.25 seconds
      delay(2000); // Wait for 1 second
    }
    for (int i = 0; i < 11; i++) {
      turnMotorOnForDuration(250, HIGH); // Turn motor right for 0.25 seconds
      delay(2000); // Wait for 1 second
    }
  }
}

void turnMotorOnForDuration(int duration, int direction) {
  digitalWrite(2, direction); // Set motor direction
  unsigned long startTime = millis();
  while (millis() - startTime < duration) {
    if (Serial.available() > 0 && Serial.read() == 's') {
      break; // Stop the motor if 's' is received
    }
    digitalWrite(3, LOW); // Set PUL pin to LOW
    digitalWrite(3, HIGH); // Set PUL pin to HIGH
    delayMicroseconds(60);
  }
  stopMotor(); // Ensure the motor stops after the duration
}

void stopMotor() {
  digitalWrite(3, LOW); // Ensure the PUL pin is LOW to stop the motor
}