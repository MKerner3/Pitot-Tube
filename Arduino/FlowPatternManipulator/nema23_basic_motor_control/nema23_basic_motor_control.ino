void setup() {
  pinMode(2, OUTPUT);
  pinMode(3, OUTPUT);
  digitalWrite(2, LOW); // Control the stepping direction (DIR pin)
}

void loop() {
  digitalWrite(3, LOW); // Set PUL pin to LOW
  digitalWrite(3, HIGH); // Set PUL pin to HIGH
  delayMicroseconds(60);
}
