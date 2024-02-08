import utime
from arducam import CameraController
from features import features, DataProcessor, mount_sd_card, csv_maker

def init():
    global counter
    counter = 0;results = [0, 0, 0]
    data_processor = features()
    global U_data; U_data = DataProcessor()
    
    try: mount_sd_card(); results[0] = 1
    except Exception as e: print(f"Error mounting SD card: {e}")

    try: global cam; cam = CameraController(); cam.init_camera(); results[1] = 1
    except Exception as e: print(f"Error initializing camera: {e}")

    try: data_processor.connect_to_wifi(); results[2] = 1
    except Exception as e: print(f"Error connecting to WiFi: {e}")
    print("results: ",results)
    return tuple(results)
               
def syncer():
    start_time = utime.ticks_ms()
    U_data.processor()
    end_time = utime.ticks_ms()
    print(f"Loop time: {utime.ticks_diff(end_time, start_time) / 1000} ms, Counter: {counter}")
            
def take_photo(cam):
    start_time = utime.ticks_ms()
    cam.capture_image()
    end_time = utime.ticks_ms()
    print("Photo time: {} ms".format(utime.ticks_diff(end_time, start_time) / 1000))
    utime.sleep(5)


data, failure_count = init(), 0

while True:
    if data[2]:
        syncer()
        counter, _ = (counter + 1, csv_maker()) if (counter + 1) % 10 == 0 else (counter + 1, None)
    else:
        failure_count += 1
        if failure_count > 10:
            data = initialize_data()
            failure_count = 0



            

    
            
