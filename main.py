from cam import take_photo
import uos, machine, gc, time
from utilities import get_timestamp, flasher
from wifimanager import Call_Manager
from send_server import upload_photo, hit_api_with_json

wifimanager = Call_Manager()

def runner():
    if wifimanager:
        uos.mount(machine.SDCard(), "/SD")

        while 1:
            status, path = take_photo(flash=1)
            if status:upload_photo(path);gc.collect()
            else:print("Bad Error");gc.collect()
            
            j_son = {"Bot_ID": 2, "Temperature" : 2, "Humidity" : 23, "Time": get_timestamp()}
            hit_api_with_json(j_son)
            time.sleep(3)
    else:
        print("Error while connecting to WiFi")

        
runner()