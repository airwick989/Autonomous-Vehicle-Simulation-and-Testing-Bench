#include <Tone.h>

#define SPEED_PIN 4
#define FUEL_PIN  5
#define WATER_PIN 6
#define RPM_PIN   2
#define DEBUG 1

Tone rpm;
Tone kmh;

int incomingSpeedValue = 1;
int incomingRPMValue = 0;
int incomingFuelValue = 0;
int temp = 0;

void setup() {
  
  Serial.begin(9600);
  
  pinMode(FUEL_PIN,OUTPUT);
  
  rpm.begin(RPM_PIN);
  kmh.begin(SPEED_PIN);
  
}

void loop() {

   updateGauges();
   delay(20); 

}

void updateGauges() {

  incomingSpeedValue = Serial.read();

  long value2 = map(incomingSpeedValue,0,12,0,155);
  Serial.println(value2-620);
  kmh.play(value2-620);

  
     
 

}
