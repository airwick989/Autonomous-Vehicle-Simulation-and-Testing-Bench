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
String strSpeed = "";

void setup() {
  
  Serial.begin(9600);
  
  pinMode(FUEL_PIN,OUTPUT);
  
  rpm.begin(RPM_PIN);
  kmh.begin(SPEED_PIN);
  
}

void loop() {

   updateGauges(); 

}

void updateGauges() {

  incomingSpeedValue = Serial.read();
  int mappedSpeed = map(incomingSpeedValue,0,115,0,155);
  if(incomingSpeedValue != 0 && incomingSpeedValue != -12 && incomingSpeedValue != -1){
    temp = mappedSpeed;
  }
  Serial.println(temp);
  kmh.play(temp);
  
}
