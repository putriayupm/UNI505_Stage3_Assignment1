from machine import Pin, I2C, ADC
import dht
import time
import network
import urequests
from i2c_lcd import I2cLcd

# === SETUP DHT11 ===
dht_sensor = dht.DHT11(Pin(15))

# === SETUP SOIL SENSOR ===
soil = ADC(Pin(34))
soil.atten(ADC.ATTN_11DB)  # Supaya bisa baca 0-3.3V

# Nilai ADC saat tanah basah & kering
sensorMin = 1000   # tanah sangat basah
sensorMax = 3000   # tanah sangat kering

# === SETUP LCD ===
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
lcd = I2cLcd(i2c, 0x27, 2, 16)

# === SETUP WIFI ===
SSID = "botax"
PASSWORD = "cakrawala"

wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

lcd.putstr("Menghubungkan...")
while not wifi.isconnected():
    time.sleep(0.5)
lcd.clear()
lcd.putstr("WiFi Terhubung!")

# === SETUP UBIDOTS ===
UBIDOTS_TOKEN = "BBUS-p13cnjjzx6LgVKJEjlrIeQjnT33xOz"
DEVICE_LABEL = "sic6"
URL = f"http://industrial.api.ubidots.com/api/v1.6/devices/{DEVICE_LABEL}/"
HEADERS = {
    "X-Auth-Token": UBIDOTS_TOKEN,
    "Content-Type": "application/json"
}

def kirim_ubidots(suhu, kelembapan_tanah):
    data = {
        "suhu": suhu,
        "kelembapan_tanah": kelembapan_tanah
    }
    try:
        res = urequests.post(URL, json=data, headers=HEADERS)
        print("Dikirim ke Ubidots:", res.text)
        res.close()
    except Exception as e:
        print("Gagal kirim:", e)

# === LOOP UTAMA ===
while True:
    try:
        dht_sensor.measure()
        suhu = dht_sensor.temperature()
        soil_value = soil.read()

        # Mapping nilai ADC ke persen
        kelembapan_tanah = (sensorMax - soil_value) * 100 / (sensorMax - sensorMin)
        kelembapan_tanah = max(0, min(100, kelembapan_tanah))  # Batasi di 0-100%

        print("Suhu:", suhu, "°C")
        print("Kelembapan Tanah: {:.1f}%".format(kelembapan_tanah))

        lcd.clear()
        lcd.putstr("Suhu:%dC\nKelembapan:%.0f%%" % (suhu, kelembapan_tanah))
        
        kirim_ubidots(suhu, kelembapan_tanah)

    except Exception as e:
        print("Error:", e)
        lcd.clear()
        lcd.putstr("Error Baca Data")

    time.sleep(10)