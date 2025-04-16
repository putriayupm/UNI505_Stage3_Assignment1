#include <WiFi.h>
#include <esp_camera.h>
#include <HTTPClient.h>

// WiFi
const char* ssid = "";
const char* password = "";

// Flask server
const char* serverName = "http://192.168.0.110:5000/upload"; // GANTI dengan IP Flask kamu

// Pin untuk tombol
const int buttonPin = 15;
bool lastButtonState = HIGH;

void setup() {
  Serial.begin(115200);
  delay(1000);

  // Setup tombol
  pinMode(buttonPin, INPUT_PULLUP); 

  // Connect to WiFi
  WiFi.begin(ssid, password);
  Serial.print("Connecting to WiFi");
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("\nWiFi connected!");
  Serial.println(WiFi.localIP());

  // Konfigurasi kamera
  camera_config_t config;
  config.ledc_channel = LEDC_CHANNEL_0;
  config.ledc_timer = LEDC_TIMER_0;
  config.pin_d0 = 5;
  config.pin_d1 = 18;
  config.pin_d2 = 19;
  config.pin_d3 = 21;
  config.pin_d4 = 36;
  config.pin_d5 = 39;
  config.pin_d6 = 34;
  config.pin_d7 = 35;
  config.pin_xclk = 0;
  config.pin_pclk = 22;
  config.pin_vsync = 25;
  config.pin_href = 23;
  config.pin_sscb_sda = 26;
  config.pin_sscb_scl = 27;
  config.pin_pwdn = 32;
  config.pin_reset = -1;
  config.xclk_freq_hz = 20000000;
  config.pixel_format = PIXFORMAT_JPEG;

  // Resolusi
  if(psramFound()){
    config.frame_size = FRAMESIZE_QVGA;
    config.jpeg_quality = 12;
    config.fb_count = 1;
  } else {
    config.frame_size = FRAMESIZE_QQVGA;
    config.jpeg_quality = 15;
    config.fb_count = 1;
  }

  // Camera init
  esp_err_t err = esp_camera_init(&config);
  if (err != ESP_OK) {
    Serial.printf("Camera init failed with error 0x%x", err);
    return;
  }
}

void loop() {
  bool buttonState = digitalRead(buttonPin);

  // Cek apakah tomtol baru ditejan
  if (buttonState == LOW && lastButtonState == HIGH) {
    delay(50); // debounce
    if (digitalRead(buttonPin) == LOW) {
      Serial.println("Tombol ditekan, mengambil foto...");
      sendPhoto();
    }
  }

  lastButtonState = buttonState;
}

void sendPhoto() {
  camera_fb_t * fb = esp_camera_fb_get();
  if (!fb) {
    Serial.println("Camera capture failed");
    return;
  }

  WiFiClient client;
  HTTPClient http;

  http.begin(client, serverName);
  http.addHeader("Content-Type", "image/jpeg");

  int httpResponseCode = http.POST(fb->buf, fb->len);
  if (httpResponseCode > 0) {
    Serial.printf("Image sent! Response: %d\n", httpResponseCode);
  } else {
    Serial.printf("Error sending image. Code: %d\n", httpResponseCode);
  }

  http.end();
  esp_camera_fb_return(fb);
}
