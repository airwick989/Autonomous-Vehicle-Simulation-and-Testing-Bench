#include<Tone.h>

#define SPEED_PIN 4
#define RPM_PIN   2
#define DEBUG 1
Tone kmh;
Tone rpm;

int incomingSpeedValue = 1;
int incomingRPMValue = 0;
int tempSpeed = 0;
int tempRPM = 0;
int placeholder = 0;
int mappedSpeed = 0;
int mappedRPM = 0;

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

  incomingSpeedValue = strSpeed.toInt();
  incomingRPMValue = strRPM.toInt();

  if(incomingSpeedValue != -29080 && incomingRPMValue != -29080){

    if(incomingSpeedValue > 400){
      placeholder = incomingSpeedValue;
      incomingSpeedValue = incomingRPMValue;
      incomingRPMValue = placeholder;
    }
    Serial.println("Speed: " + String(incomingSpeedValue) + " RPM: " + String(incomingRPMValue));
   
  
    if(incomingSpeedValue < 25){
      mappedSpeed = map(incomingSpeedValue,0,3200,0,155);
    }
    else if(incomingSpeedValue > 25 && incomingSpeedValue < 150){
      mappedSpeed = map(incomingSpeedValue,0,115,0,155);
    }
    else if(incomingSpeedValue > 150 && incomingSpeedValue < 220){
      mappedSpeed = map(incomingSpeedValue,0,120,0,155);
    }
    else{
      mappedSpeed = map(incomingSpeedValue,0,123,0,155);
    }
    if(incomingSpeedValue != 0 && incomingSpeedValue != -1){
      tempSpeed = mappedSpeed;
    }
    kmh.play(tempSpeed);
  
  
    mappedRPM = map(incomingRPMValue,0,3400,0,155);
    if(incomingRPMValue != 0 && incomingRPMValue != -1){
      tempRPM = mappedRPM;
    }
    //Serial.println("Speed: " + String(temp) + " RPM: " + String(temp2));
    rpm.play(tempRPM);
    
  }
  else{
    
    Serial.write("RECIEVED");
    
  }  
} 
