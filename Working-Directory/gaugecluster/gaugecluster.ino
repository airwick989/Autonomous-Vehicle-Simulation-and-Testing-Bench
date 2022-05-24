#include <Tone.h>

#define SPEED_PIN 4
#define RPM_PIN   2
#define DEBUG 1
Tone kmh;
Tone rpm;

int incomingSpeedValue = 1;
int incomingRPMValue = 0;
int temp = 0;
int tempSpeed = 1;

void setup() {
  
  Serial.begin(9600);
 
  kmh.begin(SPEED_PIN);
  rpm.begin(RPM_PIN);
  
}

void loop() {

   updateGauges(); 

}

void updateGauges() {

  incomingSpeedValue = Serial.read();
  int mappedSpeed = map(incomingSpeedValue,0,115,0,155);
  if(incomingSpeedValue != 0){
    temp = mappedSpeed;
  }
  Serial.println(temp);
  kmh.play(temp);

  
  
}
