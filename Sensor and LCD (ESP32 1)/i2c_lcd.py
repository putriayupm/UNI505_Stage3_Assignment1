from lcd_api import LcdApi
from machine import I2C
from time import sleep_ms

class I2cLcd(LcdApi):
    def __init__(self, i2c, i2c_addr, num_lines, num_columns):
        self.i2c = i2c
        self.i2c_addr = i2c_addr
        self.i2c.writeto(self.i2c_addr, bytearray([0]))
        sleep_ms(20)
        self.hal_write_init_nibble(0x03)
        sleep_ms(5)
        self.hal_write_init_nibble(0x03)
        sleep_ms(1)
        self.hal_write_init_nibble(0x03)
        sleep_ms(1)
        self.hal_write_init_nibble(0x02)
        sleep_ms(1)
        super().__init__(num_lines, num_columns)
        self.backlight = True
        self.hal_backlight_on()

    def hal_backlight_on(self):
        self.backlight = True
        self.i2c.writeto(self.i2c_addr, bytearray([0x08]))

    def hal_backlight_off(self):
        self.backlight = False
        self.i2c.writeto(self.i2c_addr, bytearray([0x00]))

    def hal_write_init_nibble(self, nibble):
        byte = (nibble << 4) & 0xF0
        self.i2c.writeto(self.i2c_addr, bytearray([byte | 0x0C]))
        self.i2c.writeto(self.i2c_addr, bytearray([byte | 0x08]))

    def hal_write_command(self, cmd):
        self.hal_write_byte(cmd, False)

    def hal_write_data(self, data):
        self.hal_write_byte(data, True)

    def hal_write_byte(self, byte, is_data):
        upper = byte & 0xF0
        lower = (byte << 4) & 0xF0
        self.write_half_byte(upper, is_data)
        self.write_half_byte(lower, is_data)

    def write_half_byte(self, half_byte, is_data):
        control = 0x0D if is_data else 0x0C
        self.i2c.writeto(self.i2c_addr, bytearray([half_byte | control]))
        self.i2c.writeto(self.i2c_addr, bytearray([half_byte | (control & ~0x04)]))