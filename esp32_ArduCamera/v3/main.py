import utime
from arducam import CameraController 
from features import process_uart_data, mount_sd_card, connect_to_wifi, csv_maker

def init():
    results = [0, 0, 0]

    try: mount_sd_card(); results[0] = 1
    except Exception as e: print(f"Error mounting SD card: {e}")

    try: cam = CameraController(); cam.init_camera(); results[1] = 1
    except Exception as e: print(f"Error initializing camera: {e}")

    try: connect_to_wifi("HemaRayala", "Hema_76600"); results[2] = 1
    except Exception as e: print(f"Error connecting to WiFi: {e}")

    return tuple(results)


def primary():
    global t; t = 0
    while True:
        try:
            start, log = utime.ticks_ms(), process_uart_data()
            if log:
                if t == 9 and pilaka[2]:
                    csv_maker(); t = 0
                end = utime.ticks_ms();t = t + 1
                print(f"Loop time: {(end - start) / 1000} ms, Loop Cycle: {t}")
        except Exception as error:
            print(f"An error occurred from PRIMARY: {error}")

def take_photo(cam):
    start_time = utime.ticks_ms()
    cam.capture_image()
    end_time = utime.ticks_ms()
    print("Photo time: {} ms".format(utime.ticks_diff(end_time, start_time) / 1000))
    utime.sleep(5)
               


pilaka = init()

if pilaka[0]:
    primary()   #--> Run this in main core 
    #take_photo #--> Run this in Second core
    #Add multi threading and wifi check and sync mode update!
