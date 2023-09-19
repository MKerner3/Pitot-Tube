float V_0 = 5.0; // supply voltage to the pressure sensor
float rho = 1.204; // density of air

float sensor0;

// parameters for averaging and offset
float offset = 0;
int offset_size = 10;
int veloc_mean_size = 20;
int zero_span = 2;


float offset1 = 0;
int offset1_size = 10;
int veloc1_mean_size = 20;
int zero1_span = 2;

// setup and calculate offset
void setup() {
  Serial.begin(4800);

  // Analog 0 offset
  for (int i=0;i<offset_size;i++){
    offset += analogRead(A0)-(1023/2); //analogRead(A0) returns 550.00 or 551.00
  }
  offset /= offset_size;

  // Analog 1 offset
  for (int ii=0;ii<offset1_size;ii++){
    offset1 += analogRead(A1)-(1023/2);
  }
  offset1 /= offset1_size;

}

void loop() {
  float veloc;
  float sensor0 = analogRead(A0) - offset;

  // make sure if the ADC reads below 512, then we equate it to a negative velocity
    if (sensor0<512){
      veloc = sqrt((-10000.0*((sensor0/1023.0)-0.5))/rho);
    } else if(sensor0>512){
      veloc = -sqrt((10000.0*((sensor0/1023.0)-0.5))/rho);
    }
  Serial.print("High Frequency: ");
  Serial.print(veloc, 16); // print velocity
  Serial.println();

  // Microcontroller channel 1 Calculations

  float veloc1;
  float sensor1 = analogRead(A1) - offset1;

  // make sure if the ADC reads below 512, then we equate it to a negative velocity
    if (sensor1<512){
      veloc1 = sqrt((-10000.0*((sensor1/1023.0)-0.5))/rho);
    } else if(sensor1>512){
      veloc1 = -sqrt((10000.0*((sensor1/1023.0)-0.5))/rho);
    }
  Serial.print("Low Frequency: ");
  Serial.print(veloc1, 16); // print velocity
  Serial.println();



}