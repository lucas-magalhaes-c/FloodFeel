<<<<<<< HEAD
// esp8266-espnow-transmitter.ino
// This code works for ESP8266 only.
// Configure NodeMCU ESP8266 board (Add to File > Preferences > Aditional Boards Manager URLs, then Tools > Board Manager > search for esp and install it)
// http://arduino.esp8266.com/stable/package_esp8266com_index.json
// Then, select the board "NodeMCU 1.0: ESP12-E"
// ESP-NOW for ESP32 has different API from the ESP8266 implementation
// MAC address of this board 84:0D:8E:A9:B9:40

#include <ESP8266WiFi.h>
#include <espnow.h>


#define RETRY_INTERVAL 5000
#define SEND_INTERVAL 3000 


const int trigger_pin = D6;
const int echo_pin = D7;

// defines variables
long duration;
int distance;

#define LED_BUILTIN 2

// Use the following pattern to create a Locally Administered MAC Address
//   x2-xx-xx-xx-xx-xx
//   x6-xx-xx-xx-xx-xx
//   xA-xx-xx-xx-xx-xx
//   xE-xx-xx-xx-xx-xx
// replace x with any hex value

// the following three settings must match the slave settings (central node receiver)
uint8_t remoteMac[] = {0x24, 0x0A, 0xC4, 0x59, 0x1A, 0x78};

const uint8_t channel = 14;
struct __attribute__((packed)) DataStruct {
  int distance;
  String transmitter_mac;
};

DataStruct myData;

unsigned long sentStartTime;
unsigned long lastSentTime;

void sendData() {
  uint8_t bs[sizeof(myData)];
  memcpy(bs, &myData, sizeof(myData));
  
  sentStartTime = micros();
  esp_now_send(NULL, bs, sizeof(myData)); // NULL means send to all peers

  Serial.println("Data sent to all peers added");
  
  digitalWrite(LED_BUILTIN, HIGH);
  delay(50);
  digitalWrite(LED_BUILTIN, LOW);
}

void sendCallBackFunction(const uint8_t* mac, const uint8_t sendStatus) {
  unsigned long sentEndTime = micros();
//  Serial.printf("Send To: %02x:%02x:%02x:%02x:%02x:%02x ", mac[0], mac[1], mac[2], mac[3], mac[4], mac[5]);
//  Serial.printf("Temperature: %.2f ", myData.temperature);
//  Serial.printf("Humidity: %.2f ", myData.humidity);
//  Serial.printf("Trip micros: %4lu, ", sentEndTime - sentStartTime);
//  Serial.printf("Status: %s\n", (sendStatus == 0 ? "Success" : "Failed"));
}

void setup() {
  Serial.begin(115200);
  
  WiFi.mode(WIFI_STA); // Station mode for esp-now controller
  WiFi.disconnect();

  pinMode(LED_BUILTIN, OUTPUT);

  
  Serial.println();
  Serial.println("ESP-Now Transmitter");
  Serial.printf("Transmitter mac: %s \n", WiFi.macAddress().c_str());
  myData.transmitter_mac = WiFi.macAddress().c_str();
  Serial.printf("Receiver mac: %02x:%02x:%02x:%02x:%02x:%02x\n", remoteMac[0], remoteMac[1], remoteMac[2], remoteMac[3], remoteMac[4], remoteMac[5]);
  Serial.printf("WiFi Channel: %i\n", channel);

  if (esp_now_init() != 0) {
    Serial.println("ESP_Now init failed...");
    delay(RETRY_INTERVAL);
    ESP.restart();
  }
    
  esp_now_set_self_role(ESP_NOW_ROLE_CONTROLLER);
  esp_now_add_peer(remoteMac, ESP_NOW_ROLE_SLAVE, channel, NULL, 0);

  pinMode(trigger_pin, OUTPUT); // Sets the trigPin as an Output
  pinMode(echo_pin, INPUT); // Sets the echoPin as an Input

}

void loop() {
  
  if (millis() - lastSentTime >= SEND_INTERVAL) {
    
    // Clears the trigPin
    digitalWrite(trigger_pin, LOW);
    delayMicroseconds(2);
    
    // Sets the trigPin on HIGH state for 10 micro seconds
    digitalWrite(trigger_pin, HIGH);
    delayMicroseconds(10);
    digitalWrite(trigger_pin, LOW);
    
    // Reads the echoPin, returns the sound wave travel time in microseconds
    duration = pulseIn(echo_pin, HIGH);
    
    // Calculating the distance
    distance = duration*0.034/2;

    // Max distance measured 10m, set to 0 if a greater value is obtained (also fix the issue of distance equal to 0, it returns distance = 1195)
    if(distance > 1000){
      distance = 0;
    }
    
    lastSentTime += SEND_INTERVAL;
    myData.distance = distance;   // replace this with your actual sensor reading code
    // myData.transmitter_mac = transmitter_mac;      // replace this with your actual sensor reading code

    // Prints the distance on the Serial Monitor
    Serial.print("Distance: ");
    Serial.println(myData.distance);
    // Prints the distance on the Serial Monitor
    Serial.print("Trasmitter mac adress: ");
    Serial.println(myData.transmitter_mac);
    sendData();  
  }
  
}
