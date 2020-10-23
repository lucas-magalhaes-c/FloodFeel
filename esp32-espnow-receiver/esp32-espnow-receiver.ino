// esp32-espnow-receiver.ino
// This code works for ESP32 only.
// Configure NodeMCU ESP32 board (Add to File > Preferences > Aditional Boards Manager URLs (insert the bellow link here), then Tools > Board Manager > search for esp and install it)
// https://dl.espressif.com/dl/package_esp32_index.json
// ESP-NOW for ESP8266 has different API from the ESP32 implementation
// Receiver_MAC: 24:0A:C4:59:1A:78
// Transmiter_MAC: 

#include <WiFi.h>
#include <esp_now.h>

#define RETRY_INTERVAL 5000
#define LED_BUILTIN 2

// the following 3 settings must match transmitter's settings
uint8_t mac[] = {0x84, 0x0D, 0x8E, 0xA9, 0xB9, 0x40};
const uint8_t channel = 14;
struct __attribute__((packed)) DataStruct {
  int distance;
  String transmitter_mac;
};

DataStruct myData;

void receiveCallBackFunction(const uint8_t *senderMac, const uint8_t *incomingData, int len) {
//  memcpy(&myData, incomingData, sizeof(myData));
  memcpy(&myData, incomingData, len); 
  
  Serial.printf("Transmitter MacAddr: %02x:%02x:%02x:%02x:%02x:%02x\n", senderMac[0], senderMac[1], senderMac[2], senderMac[3], senderMac[4], senderMac[5]);
  
  // Prints the distance on the Serial Monitor
  Serial.print("Distance: ");
  Serial.println(myData.distance);
  // Prints the distance on the Serial Monitor
  Serial.print("Trasmitter mac adress: ");
  Serial.println(myData.transmitter_mac);
  
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(50);
  digitalWrite(LED_BUILTIN, LOW);   // turn the LED off (LOW is the voltage level)
}

void setup() {
  Serial.begin(115200);
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  
  Serial.print("Starting..."); 
  delay(500); 
  
  WiFi.mode(WIFI_STA);
  //  WiFi.disconnect();
  
  Serial.println("ESP-Now Receiver");
  
  Serial.println("Mac Address in Station: "); 
  Serial.println(WiFi.macAddress());
  
  if (esp_now_init() != 0) {
    Serial.println("ESP_Now init failed...");
    delay(RETRY_INTERVAL);
    ESP.restart();
  }

  esp_now_register_recv_cb(receiveCallBackFunction);
  Serial.println("Slave ready. Waiting for messages...");
}

void loop() {
  delay(3000);
}
