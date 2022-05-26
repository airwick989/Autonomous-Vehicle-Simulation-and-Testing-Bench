#include <Tone.h>

#define SPEED_PIN 4
#define RPM_PIN   2
#define DEBUG 1
Tone kmh;
Tone rpm;

int incomingSpeedValue = 1;
int incomingRPMValue = 0;
int temp = 0;
int temp2 = 0;
int tempSpeed = 1;
int tempRPM = 0;
int incoming[2];

void setup() {
  
  Serial.begin(115200);
 
  kmh.begin(SPEED_PIN);
  rpm.begin(RPM_PIN);
  
}

void loop() {

   updateGauges(); 

}

void updateGauges() {

  for(int i = 0; i < 2; i++){
    incoming[i] = Serial.read();
  }
  if(incoming[0] != 0 && incoming[1] != 0 && incoming[0] != -1 && incoming[1] != -1){
    Serial.println("incoming[0]: " + String(incoming[0]) + " incoming[1]: " + String(incoming[1]));
  }
  
  incomingSpeedValue = incoming[0];
  tempSpeed = incomingSpeedValue;
  int mappedSpeed = map(incomingSpeedValue,0,115,0,155);
  if(incomingSpeedValue != 0 && incomingSpeedValue != -1){
    temp = mappedSpeed;
  }
  kmh.play(temp);

  incomingRPMValue = incoming[1];
  tempRPM = incomingRPMValue;
  int mappedRPM = map(incomingRPMValue,0,200,0,155);
  if(incomingRPMValue != 0 && incomingRPMValue != -1){
    temp2 = mappedRPM;
  }
  //Serial.println("Speed: " + String(temp) + " RPM: " + String(temp2));
  //rpm.play(temp2);
  
  
  
}
