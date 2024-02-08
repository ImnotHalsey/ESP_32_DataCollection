# feature
from machine import UART
from sdcard import SDCard
import urequests, uos, ujson
from machine import SPI, Pin, SoftSPI
import os, network, time, utime, errno, ntptime, gc,ujson, uos,urequests

class features:
    def __init__(self):
        self.ssid = "HeisenBerg"
        self.password =  "9885666252"
        self.wlan = network.WLAN(network.STA_IF)
        self.is_year_valid = self.connect_to_wifi() and utime.localtime()[0] > 2022 and (not ntptime.settime() if True else False)

    def get_timestamp(self):
        if self.is_year_valid:pass
        else:
            try:ntptime.settime()
            except OSError as e:
                if e.args[0] == errno.ETIMEDOUT:print("Error: NTP server timed out. Using local time instead.")
                else:raise e
        return "{:04}{:02}{:02}{:02}{:02}{:02}".format(*utime.localtime(utime.time() + (5 * 60 * 60 + 30 * 60))[:6])

    def connect_to_wifi(self):
        if self.wlan.isconnected():
            return True
        for _ in range(5):
            print('Connecting to WiFi...')
            self.wlan.active(True);self.wlan.connect(self.ssid, self.password)
            for _ in range(10):
                if self.wlan.isconnected():
                    print('Connected to WiFi and IP Address :', self.wlan.ifconfig()[0])
                    return
                time.sleep(1)
            self.wlan.disconnect()
        print('Failed to connect to WiFi after 5 attempts')
        return False

            
class DataProcessor:
    def __init__(self, uart_tx=5, uart_rx=22):
        self.uart = UART(1, 115200, tx=uart_tx, rx=uart_rx)
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
                            data_list.extend([self.timestamp.get_timestamp(), '4812'])
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

class W25QxxFlashMemory:
    def __init__(self):
        self.spi = SoftSPI(baudrate=1000000, polarity=0, phase=0, sck=Pin(26), mosi=Pin(25), miso=Pin(27))
        self.cs = Pin(5, Pin.OUT)
        print("External Flash Activated")

    def read_jedec_id(self):
        self.cs.value(0)
        self.spi.write(bytearray([0x9F]))
        manufacturer_id = self.spi.read(1)[0]
        memory_type = self.spi.read(1)[0]
        capacity_id = self.spi.read(1)[0]
        self.cs.value(1)
        print("Manufacturer ID: 0x{:02X}".format(manufacturer_id))
        print("Memory Type: 0x{:02X}".format(memory_type))
        print("Capacity ID: 0x{:02X}".format(capacity_id))

    def write_data(self, start_address, data):
        self.cs.value(0)
        self.spi.write(bytearray([0x02]))
        self.spi.write(bytearray([(start_address >> 16) & 0xFF, (start_address >> 8) & 0xFF, start_address & 0xFF]))
        for byte in data:
            self.spi.write(bytearray([byte]))
        self.cs.value(1)

    def read_data(self, start_address, num_bytes):
        self.cs.value(0)
        self.spi.write(bytearray([0x03]))
        self.spi.write(bytearray([(start_address >> 16) & 0xFF, (start_address >> 8) & 0xFF, start_address & 0xFF]))
        data = bytearray(self.spi.read(num_bytes))
        self.cs.value(1)
        return data

    def delete_data(self, start_address, num_bytes):
        zeros = bytearray([0x00] * num_bytes)
        self.write_data(start_address, zeros)

    def send_self(self):
        return self.cs, self.spi

    def write_data_to_flash(self, data):
        start_address = 0x100000 
        self.write_data(start_address, data)


