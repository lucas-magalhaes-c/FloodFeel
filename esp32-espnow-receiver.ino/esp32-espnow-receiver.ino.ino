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
uint8_t mac[] = {0x82, 0x88, 0x88, 0x88, 0x88, 0x88};
const uint8_t channel = 14;
struct __attribute__((packed)) DataStruct {
  float temperature;
  float humidity;
};

DataStruct myData;

void receiveCallBackFunction(const uint8_t *senderMac, const uint8_t *incomingData, int len) {
//  memcpy(&myData, incomingData, sizeof(myData));
  memcpy(&myData, incomingData, len);
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level
  Serial.printf("Transmitter MacAddr: %02x:%02x:%02x:%02x:%02x:%02x, ", senderMac[0], senderMac[1], senderMac[2], senderMac[3], senderMac[4], senderMac[5]);
  Serial.printf("Temperature: %.2f, ", myData.temperature);
  Serial.printf("Humidity: %.2f, ", myData.humidity);
  
}

void setup() {
  // initialize digital pin LED_BUILTIN as an output.
  pinMode(LED_BUILTIN, OUTPUT);
  
  Serial.begin(115200);
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
  digitalWrite(LED_BUILTIN, HIGH);   // turn the LED on (HIGH is the voltage level)
  delay(1000);                       // wait for a second
  digitalWrite(LED_BUILTIN, LOW);    // turn the LED off by making the voltage LOW
  delay(500); 

  Serial.println("Mac Address in Station: "); 
  Serial.println(WiFi.macAddress());
}
