import os, gc, utime, uos, time
from utime import sleep_ms
from server import upload_photo
from arducam import CameraController
from utilities import get_timestamp, flasher, mount_sd_card, connect_to_wifi

ssid = 'FARMROBO_2G'
password = 'powertiller1'


connect_to_wifi(ssid, password)
time.sleep(2)
mount_sd_card()
camera_controller = CameraController()
camera_controller.init_camera()

while 1:
    flasher(13, "off")
    flasher(12, "on")
    path = camera_controller.capture_image()
    flasher(12, "off")
    flasher(13, "on")
    #upload_photo(path)
    time.sleep(3)
     