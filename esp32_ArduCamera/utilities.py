import utime, ntptime, machine, errno
import os, network, time
from machine import Pin, SPI
from sdcard import SDCard

def flasher(pin_no, mode):
    pin = machine.Pin(pin_no, machine.Pin.OUT)
    if mode == "on":pin.on()
    elif mode == "off":pin.off()
    else:print("Invalid mode. Use 'on' or 'off'.")

def get_timestamp():
    if utime.localtime()[0] > 2022:pass
    else:
        try:ntptime.settime()
        except OSError as e:
            if e.args[0] == errno.ETIMEDOUT:print("Error: NTP server timed out. Using local time instead.")
            else:raise e
    timestamp = "{:04}{:02}{:02}{:02}{:02}{:02}".format(*utime.localtime(utime.time() + (5 * 60 * 60 + 30 * 60))[:6])
    return timestamp

def mount_sd_card():
    try:
        spi = SPI(2, sck=26, miso=14, mosi=27)
        cs_pin = Pin(25, Pin.OUT)
        sd = SDCard(spi, cs=cs_pin)
        vfs = os.VfsFat(sd)
        os.mount(vfs, '/SD')
        print("SD card mounted successfully")
        return True
    except Exception as e:
        print("Failed to mount SD card:", str(e))
        return False

def connect_to_wifi(ssid, password):
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Connected to WiFi')
    print('IP Address:', wlan.ifconfig()[0])
    
