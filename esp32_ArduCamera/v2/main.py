# main.py

import utime,machine
from machine import SPI, Pin
from arducam import CameraController
from server import csv_maker, upload_photo
from features import connect_to_wifi, read_and_process_data, add_row_to_csv, mount_sd_card


def init():
    global cam 
    machine.freq(240000000)    
    cam = CameraController()
    cam.init_camera()
    return cam 

def take_photo():
    start_time = utime.ticks_ms()
    path = cam.capture_image()
    print(path)
    upload_photo(path)
    end_time = utime.ticks_ms()
    print("Loop time: {} ms".format(utime.ticks_diff(end_time, start_time) / 1000))
    return 

def loop_with_net():
    global times  # Declare 'times' as a global variable
    # try:
    if connect_to_wifi("HeisenBerg", "9885666252"):
        log, length = read_and_process_data()
        if length == 38:
            add_row_to_csv('/SD/low_data.csv', log)
            times += 1
        elif length == 43:
            add_row_to_csv('/SD/data.csv', log)
            times += 1

        if times > 5:
            csv_maker('/SD/low_data.csv')
            csv_maker('/SD/data.csv')
            take_photo()
            times = 0  # Reset times after taking a photo

    else:
        print("Move to Without Internet Mode")  # TODO: Implement handling without internet
    # except Exception as e:
    #     print(f"Error: {e}, This Exception needs to be posted to the server")  # TODO: Implement error reporting


def just_loop():
    # Handles data where the internet is not available
    # Get back to the loop with the internet when the internet comes back to active mode
    return

global times


def main():
    init()
    if mount_sd_card():
        global times  # Declare 'times' as a global variable
        times = 0
        while True:
            loop_with_net()
    else:
        print("SD card Error")


if __name__ == "__main__":
    main()


        
        
        
        