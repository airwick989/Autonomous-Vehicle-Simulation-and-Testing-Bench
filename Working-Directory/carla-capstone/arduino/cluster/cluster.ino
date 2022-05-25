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
  
  Serial.begin(115200);
  
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
     
  if(incomingSpeedValue == 0){
    incomingSpeedValue = temp;
    incomingRPMValue = temp;
  }
  else{
    temp = incomingSpeedValue;
  }
   
  /*Speed GAUGE, 10 = 60mph, 23 is max */
  long value2 = map(incomingSpeedValue,0,12,0,155);
  //long value1 = map(speedValue,0,12,30,7);
  kmh.play(value2);
  
  /*---END SPEED GAUGE---*/

 
   /*---RPM GAUGE---*/
  if (incomingSpeedValue <= 1)
  {
    long value1 = map(0,0,5,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue == 2)
  {
    long value1 = map(1,0,4,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue == 3)
  {
    long value1 = map(1,0,4,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue == 4)
  {
    long value1 = map(1,0,4,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue == 5)
  {
    long value1 = map(2,0,5,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue == 6)
  {
    long value1 = map(2,0,5,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue == 7)
  {
    long value1 = map(2,0,5,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue == 8)
  {
    long value1 = map(2,0,5,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue == 9)
  {
    long value1 = map(2,0,5,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue == 10)
  {
    long value1 = map(3,0,5,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue == 11)
  {
    long value1 = map(3,0,5,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue = 12)
  {
    long value1 = map(3,0,5,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue = 13)
  {
    long value1 = map(4,0,5,0,7);
    rpm.play(value1);
  }
  else if (incomingSpeedValue = 14)
  {
    long value1 = map(4,0,5,0,7);
    rpm.play(value1);
  }
  else {
    long value1 = map(0,0,5,0,7);
    rpm.play(value1);
  }
  //long value1 = map(incomingRPMValue,0,3,0,3);
  //rpm.play(value1);
 /*--END RPM GAUGE--*/

   /*---FUEL GAUGE--150 max-*/
  //analogWrite(FUEL_PIN,fuelValue);

  /*---END FUEL GAUGE---*/

}
