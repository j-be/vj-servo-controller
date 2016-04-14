#define SERIAL_BAUDRATE 115200
#define POSITION_POTI_PIN 7
#define END_BUTTON_PIN 2

int positionPotiValue = -1;
int endButtonState = -1;

int getButtonState(int pinNumber) {
  return digitalRead(pinNumber);
}

void sendState(int potiPosition, int endButtonState) {
  Serial.print("#");
  Serial.print(potiPosition);
  Serial.print(" ");
  Serial.println(endButtonState);
}

void setup() {
  Serial.begin(SERIAL_BAUDRATE);
  
  pinMode(END_BUTTON_PIN, INPUT_PULLUP);

  // No setup needed for analog read
}

void loop() {
  positionPotiValue = analogRead(POSITION_POTI_PIN);
  endButtonState = getButtonState(END_BUTTON_PIN);

  sendState(positionPotiValue, endButtonState);
}

