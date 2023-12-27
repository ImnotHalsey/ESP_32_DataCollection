from cam import take_photo
import uos, machine, gc, time
from wifimanager import Call_Manager
from send_server import upload_photo, hit_api_with_json

wifimanager = Call_Manager()
if wifimanager:
    print("Connected to WiFi...")
    uos.mount(machine.SDCard(), "/SD")
    while 1:
        status, path = take_photo(flash=1)
        if status: 
            upload_photo(path)
            j_son = {"Bot_ID": 7, "Temperature" : 2, "Humidity" : 23, "Time": 34}
            hit_api_with_json(j_son)
            gc.collect()
            time.sleep(3)
        else:
            print("Bad Error")
            gc.collect()
else:
    print("Error while connecting to WiFi")


