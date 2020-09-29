/*
  ESP 32 Blink

  Configure NodeMCU ESP8266 board (Add to File > Preferences > Aditional Boards Manager URLs, then Tools > Board Manager > search for esp and install it)
  http://arduino.esp8266.com/stable/package_esp8266com_index.json

  CP210x USB to UART Bridge VCP Drivers
  https://www.silabs.com/products/development-tools/software/usb-to-uart-bridge-vcp-drivers
*/

#define LED 2

// the setup function runs once when you press reset or power the board
void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED, OUTPUT);
}

// the loop function runs over and over again forever
void loop() {
  digitalWrite(LED, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(LED, LOW);    // turn the LED off by making the voltage LOW
  delay(1000);                       // wait for a second
}
