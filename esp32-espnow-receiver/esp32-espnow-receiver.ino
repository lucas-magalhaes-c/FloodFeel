/*
 * This ESP-NOW slave is an access point (AP) with SSID Slave:<<AP_MAC_ADDRESS>>.
 * You don't need to hard-code the master's MAC address.
 * It also works as a station, being able to connect to a Wi-Fi network.
 * Make sure to set the channel number, the SSID and the password of your Wi-Fi network.
 */

#include <esp_now.h>
#include <WiFi.h>
#include <HTTPClient.h>

// Channel number is automatic. Check Wi-Fi channel print on Serial Monitor.
#define CHANNEL 1

HTTPClient http;

// Flag that indicates if there is data to be sent to the cloud
bool dataToSend = false;

// SSID and password of your Wi-Fi network
const char* ssid = "WIFI-SSID";
const char* password = "WIFI-PASSWORD";

// Data received via ESP-NOW
uint16_t distance;

void OnDataRecv(const uint8_t *mac_addr, const uint8_t *data, int data_len);

// Init ESP Now with fallback
void InitESPNow() {
  if (esp_now_init() == ESP_OK) {
    Serial.println("ESPNow Init Success");
  }
  else {
    Serial.println("ESPNow Init Failed");
    ESP.restart();
  }
}

// config AP SSID
void configDeviceAP() {
  String Prefix = "Slave:";
  String Mac = WiFi.macAddress();
  String SSID = Prefix + Mac;
  String Password = "123456789"; // Not sure where this password is used
  bool result = WiFi.softAP(SSID.c_str(), Password.c_str(), CHANNEL, 0);
  if (!result) {
    Serial.println("AP Config failed.");
  } else {
    Serial.println("AP Config Success. Broadcasting with AP: " + String(SSID));
  }
}

void setup() {
  Serial.begin(115200);
  Serial.println("ESPNow/Basic/Slave Example");

  //Set device in AP mode to begin with
  WiFi.mode(WIFI_AP_STA);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Setting as a Wi-Fi Station..");
  }
  Serial.print("Station IP Address: ");
  Serial.println(WiFi.localIP());
  Serial.print("Wi-Fi Channel: ");
  Serial.println(WiFi.channel());

  // configure device AP mode
  configDeviceAP();
  // This is the mac address of the Slave in AP Mode
  Serial.print("AP MAC: "); Serial.println(WiFi.softAPmacAddress());

  // Init ESPNow with a fallback logic
  InitESPNow();
  // Once ESPNow is successfully Init, we will register for recv CB to
  // get recv packer info.
  esp_now_register_recv_cb(OnDataRecv);
}

// callback when data is recv from Master
void OnDataRecv(const uint8_t *mac_addr, const uint8_t *data, int data_len) {
  memcpy(&distance, data, data_len);
  char macStr[18];
  snprintf(macStr, sizeof(macStr), "%02x:%02x:%02x:%02x:%02x:%02x",
           mac_addr[0], mac_addr[1], mac_addr[2], mac_addr[3], mac_addr[4], mac_addr[5]);
  Serial.print("Last Packet Recv from: "); Serial.println(macStr);
  // Prints the distance on the Serial Monitor
  Serial.print("Distance: ");
  Serial.println(distance);
  Serial.println("");
  dataToSend = true;
}

void loop() {
  if (dataToSend) {
    http.begin("http://loripsum.net/api/short/1");
  
      // Send HTTP GET request
    int httpResponseCode = http.GET();
    
    if (httpResponseCode>0) {
      Serial.print("HTTP Response code: ");
      Serial.println(httpResponseCode);
      String payload = http.getString();
      Serial.println(payload);
    }
    else {
      Serial.print("Error code: ");
      Serial.println(httpResponseCode);
    }
    http.end();
    dataToSend = false;
  }
}
