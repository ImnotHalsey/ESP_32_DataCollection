from cam import take_photo
import uos, machine, gc, time
from utilities import get_timestamp, flasher
from wifimanager import Call_Manager
from send_server import upload_photo, hit_api_with_json

wifimanager = Call_Manager()

def runner():
    try:
        if wifimanager:
            try:
                uos.mount(machine.SDCard(), "/SD")
            except OSError as mount_error:
                print(f"Error mounting SD Card: {mount_error}")
                return

            while 1:
                try:
                    status, path = take_photo(flash=1)
                    if status:
                        try:
                            upload_photo(path)
                        except Exception as upload_error:
                            print(f"Error uploading photo: {upload_error}")
                        finally:
                            gc.collect()
                    else:
                        print("Bad Error")
                        gc.collect()

                    try:
                        j_son = {"Bot_ID": 2, "Temperature": 2, "Humidity": 23, "Time": get_timestamp()}
                        hit_api_with_json(j_son)
                    except Exception as api_error:
                        print(f"Error hitting API: {api_error}")
                    finally:
                        time.sleep(3)

                except Exception as inner_error:
                    print(f"Inner Exception: {inner_error}")
                    # Handle specific exceptions if needed
                    gc.collect()

        else:
            print("Error while connecting to WiFi")
    except Exception as outer_error:
        print(f"Outer Exception: {outer_error}")
        machine.reset()


runner()       
