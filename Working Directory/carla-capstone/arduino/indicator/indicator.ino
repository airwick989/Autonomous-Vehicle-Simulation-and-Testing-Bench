#define rightIndicator_PIN 11
#define leftIndicator_PIN 10

int IndicatorValue = 0;


void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(rightIndicator_PIN,OUTPUT);
  pinMode(leftIndicator_PIN,OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
    
    IndicatorValue = Serial.read() - '0';

    if(IndicatorValue == 1)
    {
      Serial.print("Working");
      digitalWrite(rightIndicator_PIN, LOW);
      digitalWrite(leftIndicator_PIN, HIGH);
      delay(500);
      digitalWrite(rightIndicator_PIN,HIGH);
      delay(500);
    }

    if(IndicatorValue == 2)
    {
      digitalWrite(leftIndicator_PIN, LOW);
      digitalWrite(rightIndicator_PIN, HIGH);
      delay(500);
      digitalWrite(leftIndicator_PIN, HIGH);
      delay(500);
    }

    if(IndicatorValue == 3){
      digitalWrite(rightIndicator_PIN, LOW);
      digitalWrite(leftIndicator_PIN, LOW);
      delay(500);
      digitalWrite(rightIndicator_PIN,HIGH);
      digitalWrite(leftIndicator_PIN, HIGH);
      delay(500);
    }
	
	  if(IndicatorValue == 0){
      digitalWrite(rightIndicator_PIN,HIGH);
      digitalWrite(leftIndicator_PIN, HIGH);
      delay(500);
    }
    
  
}
