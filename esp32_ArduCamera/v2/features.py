# feature
from sdcard import SDCard
from machine import SPI, Pin
import os, network, time, utime, errno, ntptime
import urequests, uos, ujson
from machine import UART

def add_row_to_csv(file_path, row_data):
    with open(file_path, 'a') as file:
        row_str = ','.join(str(item) for item in row_data) + '\n'
        file.write(row_str)
        file.close()
        print("Row Added")
        
def get_timestamp():
    if utime.localtime()[0] > 2022:pass
    else:
        try:ntptime.settime()
        except OSError as e:
            if e.args[0] == errno.ETIMEDOUT:print("Error: NTP server timed out. Using local time instead.")
            else:raise e
    timestamp = "{:04}{:02}{:02}{:02}{:02}{:02}".format(*utime.localtime(utime.time() + (5 * 60 * 60 + 30 * 60))[:6])
    return timestamp

def connect_to_wifi(ssid, password):
    print("WiFi Mode")
    wlan = network.WLAN(network.STA_IF)
    if not wlan.isconnected():
        print('Connecting to WiFi...')
        wlan.active(True)
        wlan.connect(ssid, password)
        while not wlan.isconnected():
            time.sleep(1)
    print('Connected to WiFi')
    print('IP Address:', wlan.ifconfig()[0])
    return 1

def read_and_process_data(start_char=b'<', end_char=b'>', success_code='2020'):
    uart = UART(1, 115200, tx=05, rx=22)
    buffer = bytearray()
    
    while True:
        if uart.any():
            byte = uart.read(1)
            if start_char in byte:
                buffer = byte
            else:
                buffer += byte

            if buffer.endswith(end_char):
                try:
                    data_str = buffer.decode('utf-8').strip(start_char.decode() + end_char.decode())
                    data_list = data_str.split(',')
                    
                    if len(data_list) == 42:
                        data_list.append(get_timestamp())
                        print("Processed data:", data_list)
                        uart.write(success_code + '\n')
                        return data_list, len(data_list)
                    elif len(data_list) == 37:
                        data_list.append(get_timestamp())
                        print("Processed data:", data_list, )
                        uart.write(success_code + '\n')
                        return data_list,  len(data_list)
                    else:
                        print("Skipping: Missing delimiters in data")
                        buffer = bytearray()
                        
                        return False, False
                    
                except Exception as e:
                    print("Error processing data:", e)
                    buffer = bytearray()
                    return False, False

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
        spi = SPI(2, sck=14, miso=02, mosi=15)
        cs_pin = Pin(13, Pin.OUT)
        sd = SDCard(spi, cs=cs_pin)
        vfs = os.VfsFat(sd)
        os.mount(vfs, '/SD')
        print("SD card mounted successfully")
        return True
    except Exception as e:
        print("Failed to mount SD card:", str(e))
        return False