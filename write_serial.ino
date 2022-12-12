int trigger_in = 12;
int ledPin = 13;
int val = 0;

void setup() {
  // put your setup code here, to run once:
  Serial.begin(9600);
  pinMode(trigger_in, INPUT);
  pinMode(ledPin, OUTPUT);
}

void loop() {
  // put your main code here, to run repeatedly:
  val = digitalRead(trigger_in);

  if (val == HIGH) {
    Serial.write(1);
    digitalWrite(ledPin, val);
  }
}
