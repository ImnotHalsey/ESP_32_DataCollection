# feature
from machine import UART
from sdcard import SDCard
import urequests, uos, ujson
from machine import SPI, Pin
import os, network, time, utime, errno, ntptime, gc,ujson, uos,urequests

class features:
    def __init__(self):
        self.ssid = "RD"
        self.password =  "Farmrobo@123*"
        self.wlan = network.WLAN(network.STA_IF)
        #self.is_year_valid = self.connect_to_wifi() and self.sync_time()

    def sync_time(self):
        try:
            ntptime.settime()
            print("Time synchronized successfully.")
            return True
        except OSError as e:
            print("Error syncing time:", e)
            return False

    def get_current_time(self):
        try:
            current_time = utime.localtime()
            formatted_time = "{:04}-{:02}-{:02} {:02}:{:02}:{:02}".format(current_time[0], current_time[1], current_time[2], current_time[3], current_time[4], current_time[5])
            return formatted_time
        except Exception as e:
            print("Error getting current time:", e)
            return None

    def connect_to_wifi(self):
        if self.wlan.isconnected():
            return True
        for _ in range(5):
            print('Connecting to WiFi...')
            self.wlan.active(True);self.wlan.connect(self.ssid, self.password)
            if self.wlan.isconnected():
                print('Connected to WiFi and IP Address :', self.wlan.ifconfig()[0])
                return True
            time.sleep(1)
        print('Failed to connect to WiFi after 5 attempts')
        return False

            
class DataProcessor:
    def __init__(self, uart_tx=5, uart_rx=22):
        self.uart = UART(2, 115200, tx=uart_tx, rx=uart_rx)
        self.buffer = bytearray()
        self.timestamp = features()
    
    def write_csv(self,data_list):
        row_str = ','.join(str(item) for item in data_list) + '\n'
        with open('/SD/data.csv', 'a+') as file:
            file.write(row_str)
    
    def processor(self,start_char=b'<', end_char=b'>', success_code='2020'):
        while True:
            if self.uart.any():
                byte = self.uart.read(1)
                if start_char in byte:
                    self.buffer = byte
                else:
                    self.buffer += byte

                if self.buffer.endswith(end_char):
                    try:
                        data_str = self.buffer.decode('utf-8').strip(start_char.decode() + end_char.decode())
                        data_list = data_str.split(',')

                        if len(data_list) == 42 or len(data_list) == 37:
                            data_list.extend([self.timestamp.get_timestamp(), '1234'])
                            print("Processed data:", data_list)
                            self.uart.write(success_code + '\n')
                            self.write_csv(data_list)
                            return data_list, len(data_list)
                        else:
                            print("Skipping: Missing delimiters in data")
                            self.buffer = bytearray()
                            return False, False

                    except Exception as e:
                        print("Error processing data:", e)
                        self.buffer = bytearray()
                        return False, False
    
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
            
def csv_maker():
    try:
        gc.collect()
        with open('/SD/data.csv', 'r') as file:
            csv_content = file.readlines()
        con = [i for i in csv_content]
        payload = {'csv_content': con}
        json_payload = ujson.dumps(payload)
        #print("JSON Sent and Length", len(json_payload))
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
