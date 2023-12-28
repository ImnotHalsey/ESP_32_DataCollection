from time import sleep 
import camera, machine,uos
from utilities import get_timestamp, flasher

def take_photo(flash=None):
    try:
        try: 
            camera.init(0, format=camera.JPEG)
            camera.framesize(camera.FRAME_HD)
            if flash:flasher(4, "on")
            img = camera.capture()
            if flash:flasher(4, "off")
            try:
                file_path = f"SD/{get_timestamp()}.jpg"
                with open(file_path, "wb") as file:
                    file.write(bytearray(img))
                return True, file_path
            except Exception as e:
                print(f"Error saving photo: {e}")
                return False, None
        except Exception as e:
            print(f"Error Initiating Camera: {e}")
            return False, None
    finally:
        camera.deinit()

