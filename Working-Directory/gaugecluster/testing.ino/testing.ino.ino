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
  
  Serial.begin(2000000);
 
  kmh.begin(SPEED_PIN);
  rpm.begin(RPM_PIN);
  
}

void loop() {

   updateGauges(); 

}

void updateGauges() {

  String strRPM = Serial.readStringUntil('\n');
  String strSpeed = Serial.readStringUntil('\n');
  
  Serial.println("Speed: " + strSpeed + " RPM: " + strRPM);
   
  incomingSpeedValue = strSpeed.toInt();
  tempSpeed = incomingSpeedValue;
  int mappedSpeed = map(incomingSpeedValue,0,115,0,155);
  if(incomingSpeedValue != 0 && incomingSpeedValue != -1){
    temp = mappedSpeed;
  }
  kmh.play(temp);

  incomingRPMValue = strRPM.toInt();
  tempRPM = incomingRPMValue;
  int mappedRPM = map(incomingRPMValue,0,115,0,155);
  if(incomingRPMValue != 0 && incomingRPMValue != -1){
    temp2 = mappedRPM;
  }
  //Serial.println("Speed: " + String(temp) + " RPM: " + String(temp2));
  rpm.play(temp2);
    
    
} 
