#include <WiFi.h>
#include <ESPAsyncWebServer.h>
#include <SPIFFS.h>
#include "AudioFileSourceSPIFFS.h"
#include "AudioGeneratorMP3.h"
#include "AudioOutputI2S.h"

const char* ssid = "Eugenia";
const char* password = "";

// I2S Configuration for MAX98357A
#define I2S_DOUT 25
#define I2S_BCLK 26
#define I2S_LRC 27

AsyncWebServer server(80);
AudioGeneratorMP3 *mp3 = nullptr;
AudioFileSourceSPIFFS *file = nullptr;
AudioOutputI2S *out = nullptr;

void playAudio(const char* path) {
  // Stop any currently playing audio
  if (mp3) {
    mp3->stop();
    delete mp3;
    mp3 = nullptr;
  }
  if (file) {
    delete file;
    file = nullptr;
  }
  
  // Start new playback
  file = new AudioFileSourceSPIFFS(path);
  mp3 = new AudioGeneratorMP3();

  mp3->begin(file, out);
  Serial.printf("Playing: %s\n", path);
}

void handleUpload(AsyncWebServerRequest *request, String filename, size_t index, uint8_t *data, size_t len, bool final) {
  static File uploadFile;
  
  if (!index) {
    Serial.println("Upload started");
    SPIFFS.remove("/audio.mp3"); 
    uploadFile = SPIFFS.open("/audio.mp3", "w");
    if (!uploadFile) {
      Serial.println("Failed to create file");
      request->send(500, "text/plain", "Failed to create file");
      return;
    }
  }
  
  if (uploadFile) {
    if (len) {
      size_t written = uploadFile.write(data, len);
      if (written != len) {
        Serial.println("Write failed");
        uploadFile.close();
        request->send(500, "text/plain", "Write failed");
        return;
      }
    }
    
    if (final) {
      uploadFile.close();
      Serial.println("Upload complete");
      request->send(200, "text/plain", "Upload complete");
      
      delay(100);
      playAudio("/audio.mp3");
    }
  }
}

void setup() {
  Serial.begin(115200);
  
  // Connect to WiFi
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(1000);
    Serial.println("Connecting to WiFi...");
  }
  Serial.println("Connected to WiFi");
  Serial.print("IP Address: ");
  Serial.println(WiFi.localIP());

  // Initialize SPIFFS
  if (!SPIFFS.begin(true)) {
    Serial.println("SPIFFS initialization failed");
    while(1) delay(1000);
  }

  // Audio configuration for MAX98357A
  out = new AudioOutputI2S();
  out->SetPinout(I2S_BCLK, I2S_LRC, I2S_DOUT);
  out->SetOutputModeMono(true);  
  out->SetGain(0.5); 

  // Configure server
  server.on("/play_audio", HTTP_POST, 
    [](AsyncWebServerRequest *request) {
      request->send(200);
    },
    [](AsyncWebServerRequest *request, String filename, size_t index, uint8_t *data, size_t len, bool final) {
      handleUpload(request, filename, index, data, len, final);
    }
  );

  server.begin();
  Serial.println("HTTP server started");
}

void loop() {
  if (mp3 && mp3->isRunning()) {
    if (!mp3->loop()) {
      mp3->stop();
      delete mp3;
      delete file;
      mp3 = nullptr;
      file = nullptr;
      Serial.println("Playback finished");
    
      SPIFFS.remove("/audio.mp3");
    }
  }
  delay(1); 
}
