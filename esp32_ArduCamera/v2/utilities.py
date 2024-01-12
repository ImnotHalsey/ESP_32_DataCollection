import os, network, time
from sdcard import SDCard
import utime, ntptime, machine, errno
from machine import Pin, SPI, UART


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
    
def add_row_to_csv(file_path, row_data):
    with open(file_path, 'a') as file:
        row_str = ','.join(str(item) for item in row_data) + '\n'
        file.write(row_str)

def read_and_process_data(start_char, end_char, success_code, error_occurance):
    uart = UART(2, 115200, tx=Pin(17), rx=Pin(16))
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
                    if len(data_list) == 41 or len(data_list) == 44:
                        uart.write(success_code + '\n')
                        print("Processed data:", data_list, "error_occurance: ", error_occurance)
                        return data_list, error_occurance
                    else:
                        print("Skipping: Missing delimiters in data")
                        buffer = bytearray()
                        error_occurance += 1 
                        return False, error_occurance
                except Exception as e:
                    print("Error processing data:", e)
                    buffer = bytearray()
                    return False, error_occurance