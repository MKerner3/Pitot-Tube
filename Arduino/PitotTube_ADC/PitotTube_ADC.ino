#include <ADS1256.h>
#include <SPI.h>

//Routine for calculating the velocity from 
//a pitot tube and MPXV7002DP pressure differential sensor
int channel = 0;

float clockMHZ = 7.68;
float vRef = 2.5;
ADS1256 adc(clockMHZ, vRef, true);

float V_0 = 5.0; // supply voltage to the pressure sensor
float rho = 1.204; // density of air

float sensor1;

// parameters for averaging and offset
float offset = 0;
int offset_size = 10;
int veloc_mean_size = 20;
int zero_span = 2;

// setup and calculate offset
void setup() {
  Serial.begin(9600);
  adc.begin(ADS1256_DRATE_30000SPS, ADS1256_GAIN_1, false);
  adc.setChannel(channel);

  adc.waitDRDY();
  for (int i=0;i<offset_size;i++){
    offset = offset + adc.readCurrentChannel() - 2.5; //analogRead(A0) returns 550.00 or 551.00
  }
  offset /= offset_size;
}

void loop() {
  //adc.waitDRDY();
  sensor1 = adc.readCurrentChannel() - offset;
  //Serial.println(offset);
  //Serial.println(sensor1, 16);

  float veloc = 0.0;
  //float adc_avg = 0.0;
  float vavg = (5 * sensor1)/V_0;
  
  if (sensor1 > 2.5) {
    veloc = sqrt( ( 2000* (vavg - 2.5) ) / rho );
  } else {
    veloc = sqrt( ( -2000* (vavg - 2.5) ) / rho );
  }
  Serial.println(veloc, 16); // print velocity  

}