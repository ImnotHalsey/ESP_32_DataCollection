# feature
from machine import UART
from sdcard import SDCard
import urequests, uos, ujson
from machine import SPI, Pin
import os, network, time, utime, errno, ntptime, gc,ujson, uos,urequests

def uploader(json_data):
    response = None  
    try:
        api_url = "https://531f5ac0-9df0-4a8c-a737-cf2c52891552-00-2z6iom5vem0nf.sisko.replit.dev/get_data"
        print("Posting...")
        response = urequests.post(api_url, data=json_data, headers={'Content-Type': 'application/json'})
        if response.status_code == 200:
            print("Data POSTED to Server")
            return True
        else:
            print(f"API call failed with status code: {response.status_code}")
    except OSError as e:
        print(f"Network error: {str(e)}")
    except ValueError as e:
        print(f"JSON encoding error: {str(e)}")
    finally:
        if response:
            response.close()
            
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
    wlan = network.WLAN(network.STA_IF)
    if wlan.isconnected():
        return True
    for _ in range(5):
        print('Connecting to WiFi...')
        wlan.active(True)
        wlan.connect(ssid, password)
        for _ in range(10):
            if wlan.isconnected():
                print('Connected to WiFi')
                print('IP Address:', wlan.ifconfig()[0])
                return
            time.sleep(1)
        wlan.disconnect()
    print('Failed to connect to WiFi after 5 attempts')
    return False


def process_uart_data():
    try:
        uart = UART(1, 115200, tx=5, rx=22) 
        buffer = bytearray()
        with open('/SD/data.csv', 'a+') as file: 
            while uart.any():  
                byte = uart.read(1)
                if byte:
                    if byte.startswith(b'<'):
                        buffer = byte
                    elif byte.endswith(b'>'):
                        try:
                            data_str = buffer.decode('utf-8').strip('<>')
                            data_list = data_str.split(',')
                            if len(data_list) == 42 or len(data_list) == 37:
                                data_list.append(get_timestamp()) 
                                data_list.append('4812')
                                print("Data Processed:")
                                uart.write('2020\n')  
                                row_str = ','.join(str(item) for item in data_list) + '\n'
                                file.write(row_str)
                                buffer = bytearray()
                                return 1
                            else:
                                pass
                        except Exception as e:
                            print("Error processing data:", e)
                            buffer = bytearray()  
                    else:
                        buffer += byte
                else:
                    print("No data or UART closed.")
                    break
    except Exception as e:
        print(f"Error in process_uart_data: {e}")
    return 0

def csv_maker():
    try:
        gc.collect()
        with open('/SD/data.csv', 'r') as file:
            csv_content = file.readlines()
        con = [i for i in csv_content]
        payload = {'csv_content': con}
        json_payload = ujson.dumps(payload)
        print("JSON Sent and Length", len(json_payload))
        if uploader(json_payload): (lambda f: f.close())(open('/SD/data.csv', 'w'))
        gc.collect()
    except Exception as e:
        print(f"Error: {e}")

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