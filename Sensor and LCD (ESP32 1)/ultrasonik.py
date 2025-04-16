from machine import Pin, I2C, time_pulse_us
import time
import network
from i2c_lcd import I2cLcd

# === SETUP ULTRASONIC ===
TRIG1 = Pin(4, Pin.OUT)
ECHO1 = Pin(5, Pin.IN)
TRIG2 = Pin(18, Pin.OUT)
ECHO2 = Pin(19, Pin.IN)

def trigger_sensor(trig):
    trig.off()
    time.sleep_us(2)
    trig.on()
    time.sleep_us(10)
    trig.off()

# === SETUP LCD ===
i2c = I2C(0, scl=Pin(22), sda=Pin(21), freq=400000)
lcd_addr = i2c.scan()[0]
lcd = I2cLcd(i2c, lcd_addr, 2, 16)
lcd.putstr("LCD Siap!")

# === SETUP WIFI ===
lcd.clear()
lcd.putstr("Menghubungkan...")
SSID = "botax"
PASSWORD = "cakrawala"
wifi = network.WLAN(network.STA_IF)
wifi.active(True)
wifi.connect(SSID, PASSWORD)

timeout = 20
while not wifi.isconnected() and timeout > 0:
    time.sleep(0.5)
    timeout -= 1

lcd.clear()
if wifi.isconnected():
    lcd.putstr("WiFi Terhubung!")
else:
    lcd.putstr("WiFi Gagal")
    time.sleep(5)

# === VARIABEL ===
start_time = 0
waktu_tempuh = 0
objek_terdeteksi_1 = False
objek_terdeteksi_2 = False

# === Batas Jarak (cm) ===
MAX_DISTANCE = 10  # Batasi deteksi hanya untuk objek yang jaraknya <= 10 cm

# === LOOP UTAMA ===
while True:
    try:
        print("=== Loop ===")

        # Sensor 1: Deteksi objek pertama kali
        if not objek_terdeteksi_1:
            trigger_sensor(TRIG1)
            durasi1 = time_pulse_us(ECHO1, 1, 30000)
            if durasi1 > 0:
                jarak1 = durasi1 / 58  # Menghitung jarak dalam cm
                if jarak1 <= MAX_DISTANCE:  # Deteksi hanya jika jarak <= MAX_DISTANCE (10 cm)
                    start_time = time.ticks_ms()
                    objek_terdeteksi_1 = True
                    print("Objek lewat sensor 1")

        # Sensor 2: Deteksi objek setelah lewat sensor 1
        if objek_terdeteksi_1 and not objek_terdeteksi_2:
            trigger_sensor(TRIG2)
            durasi2 = time_pulse_us(ECHO2, 1, 30000)
            if durasi2 > 0:
                jarak2 = durasi2 / 58  # Menghitung jarak dalam cm
                if jarak2 <= MAX_DISTANCE:  # Deteksi hanya jika jarak <= MAX_DISTANCE (10 cm)
                    finish_time = time.ticks_ms()
                    waktu_tempuh = time.ticks_diff(finish_time, start_time) / 1000
                    objek_terdeteksi_2 = True
                    print("Objek lewat sensor 2. Waktu tempuh:", waktu_tempuh)

                    # Output waktu tempuh hanya setelah objek lewat sensor 2
                    lcd.move_to(0, 0)
                    lcd.putstr("Waktu Tempuh:  ")
                    lcd.move_to(0, 1)
                    lcd.putstr("%.2f detik     " % waktu_tempuh)

        # Reset status deteksi setelah output selesai
        if objek_terdeteksi_2:
            objek_terdeteksi_1 = False
            objek_terdeteksi_2 = False
            waktu_tempuh = 0  # Reset waktu tempuh setelah setiap perhitungan

    except Exception as e:
        print("Error utama:", e)
        lcd.clear()
        lcd.putstr("Error Umum")

    time.sleep(0.3)
