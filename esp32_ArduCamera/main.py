import os, time, network, gc
from sdcard import SDCard
from machine import SPI, Pin
from arducam import Camera
from utime import sleep_ms
from server import upload_photo
from utilities import get_timestamp, flasher

ssid = 'FARMROBO_2G'
password = 'powertiller1'

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

def mountSD():
    spi = SPI(2, sck=26, miso=14, mosi=27)
    cs_pin = Pin(25, Pin.OUT)
    sd = SDCard(spi, cs=cs_pin)
    vfs = os.VfsFat(sd)
    os.mount(vfs, '/SD')
    return True

def init_camera():
    spi_camera = SPI(1, sck=Pin(18), miso=Pin(19), mosi=Pin(23))
    cs_camera = Pin(4, Pin.OUT) 
    cam = Camera(spi_camera, cs_camera)
    sleep_ms(1000)
    return cam

def take_two(cam):
    gc.collect()
    cam.set_resolution(cam.RESOLUTION_320X240)
    data = cam.capture_jpg()
    gc.collect()
    return data

connect_to_wifi(ssid, password)
mountSD()
scam = init_camera()

while 1:
    flasher(12, "on")
    file_path = f"SD/{get_timestamp()}.jpg"
    with open(file_path, "wb") as file:
        file.write(take_two(scam))
    file.close()
    gc.collect()
    #upload_photo(file_path)
    flasher(12, "off")
    print("Done")
    sleep_ms(200)




    

