#include <ADS1256.h>
#include <SPI.h>

float clockMHZ = 7.68;
float vRef = 2.5;
ADS1256 adc0(clockMHZ, vRef, true);

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

  // Channel 0
  adc0.begin(ADS1256_DRATE_30000SPS, ADS1256_GAIN_1, false);
  adc0.setChannel(channel0);

  // Channel 0 offset
  adc0.waitDRDY();
  for (int i=0;i<offset_size;i++){
    offset = offset + adc0.readCurrentChannel() - 2.5; //analogRead(A0) returns 550.00 or 551.00
  }
  offset /= offset_size;

  // Analog 0 offset
  for (int ii=0;ii<offset1_size;ii++){
    offset1 += analogRead(A0)-(1023/2);
  }
  offset1 /= offset1_size;

}

void loop() {
  adc0.waitDRDY();
  sensor0 = adc0.readCurrentChannel() - offset;
  
  float veloc = 0.0;
  float vavg = (5 * sensor0)/V_0;

  if (sensor0 > 2.5) {
    veloc = sqrt( ( 2000* (vavg - 2.5) ) / rho );
  } else {
    veloc = sqrt( ( -2000* (vavg - 2.5) ) / rho );
  }
  Serial.print("High Frequency: ");
  Serial.print(veloc, 16);
  Serial.println();

  // Microcontroller channel Calculations

  float veloc1;
  float sensor1 = analogRead(A0) - offset1;

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