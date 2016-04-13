#define SERIAL_BAUDRATE 115200
#define POSITION_POTI_PIN 7
#define MAX_BUTTON_PIN 2
#define MIN_BUTTON_PIN 3

int positionPotiValue = -1;
int minButtonState = -1;
int maxButtonState = -1;

void setupButtonPin(int pinNumber) {
  pinMode(pinNumber,INPUT_PULLUP); 
}

int getButtonState(int pinNumber) {
  return !digitalRead(pinNumber);
}

void sendState(int potiPosition, int isMin, int isMax) {
  Serial.print("#");
  Serial.print(potiPosition);
  Serial.print(" ");
  Serial.print(isMin);
  Serial.print(" ");
  Serial.println(isMax);
}

void setup() {
  Serial.begin(SERIAL_BAUDRATE);
  
  setupButtonPin(MIN_BUTTON_PIN);
  setupButtonPin(MAX_BUTTON_PIN);

  // No setup needed for analog read
}

void loop() {
  positionPotiValue = analogRead(POSITION_POTI_PIN);
  minButtonState = getButtonState(MIN_BUTTON_PIN);
  maxButtonState = getButtonState(MAX_BUTTON_PIN);

  sendState(positionPotiValue, minButtonState, maxButtonState);
}

