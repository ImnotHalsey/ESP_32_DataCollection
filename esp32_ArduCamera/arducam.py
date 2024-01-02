from utime import sleep_ms
from machine import SPI, Pin
import utime, uos, ujson
from utilities import get_timestamp

class Camera:
    CAM_REG_SENSOR_RESET = 0x07
    CAM_SENSOR_RESET_ENABLE = 0x40

    CAM_REG_SENSOR_ID = 0x40
    SENSOR_5MP_1 = 0x81
    SENSOR_3MP_1 = 0x82
    SENSOR_5MP_2 = 0x83
    SENSOR_3MP_2 = 0x84

    CAM_REG_COLOR_EFFECT_CONTROL = 0x27
    SPECIAL_NORMAL = 0x00
    SPECIAL_BW = 0x04
    SPECIAL_GREENISH = 0x20

    CAM_REG_BRIGHTNESS_CONTROL = 0X22

    CAM_REG_CONTRAST_CONTROL = 0X23
    CONTRAST_MINUS_3 = 6
    CONTRAST_MINUS_2 = 4
    CONTRAST_MINUS_1 = 2
    CONTRAST_DEFAULT = 0
    CONTRAST_PLUS_1 = 1
    CONTRAST_PLUS_2 = 3
    CONTRAST_PLUS_3 = 5

    CAM_REG_SATURATION_CONTROL = 0X24

    CAM_REG_WB_MODE_CONTROL = 0X26
    WB_MODE_AUTO = 0
    WB_MODE_SUNNY = 1
    WB_MODE_OFFICE = 2
    WB_MODE_CLOUDY = 3
    WB_MODE_HOME = 4

    CAM_REG_SHARPNESS_CONTROL = 0X28
    CAM_REG_AUTO_FOCUS_CONTROL = 0X29
    CAM_REG_IMAGE_QUALITY = 0x2A

    CAM_REG_DEBUG_DEVICE_ADDRESS = 0x0A
    deviceAddress = 0x78

    CAM_REG_SENSOR_STATE = 0x44
    CAM_REG_SENSOR_STATE_IDLE = 0x01

    CAM_REG_FORMAT = 0x20
    CAM_IMAGE_PIX_FMT_JPG = 0x01
    CAM_IMAGE_PIX_FMT_RGB565 = 0x02
    CAM_IMAGE_PIX_FMT_YUV = 0x03

    CAM_REG_CAPTURE_RESOLUTION = 0x21
    RESOLUTION_160X120 = 0X00
    RESOLUTION_320X240 = 0X01
    RESOLUTION_640X480 = 0X02
    RESOLUTION_800X600 = 0X03
    RESOLUTION_1280X720 = 0X04
    RESOLUTION_1280X960 = 0X05
    RESOLUTION_1600X1200 = 0X06
    RESOLUTION_1920X1080 = 0X07
    RESOLUTION_2048X1536 = 0X08
    RESOLUTION_2592X1944 = 0X09
    RESOLUTION_96X96 = 0X0a
    RESOLUTION_128X128 = 0X0b
    RESOLUTION_320X320 = 0X0c

    ARDUCHIP_FIFO = 0x04
    FIFO_CLEAR_ID_MASK = 0x01
    FIFO_START_MASK = 0x02

    ARDUCHIP_TRIG = 0x44
    CAP_DONE_MASK = 0x04

    FIFO_SIZE1 = 0x45
    FIFO_SIZE2 = 0x46
    FIFO_SIZE3 = 0x47

    SINGLE_FIFO_READ = 0x3D
    BURST_FIFO_READ = 0X3C

    WHITE_BALANCE_WAIT_TIME_MS = 500

    def __init__(self, spi_bus, cs):
        self.cs = cs
        self.spi_bus = spi_bus

        self._write_reg(self.CAM_REG_SENSOR_RESET, self.CAM_SENSOR_RESET_ENABLE)
        self._wait_idle()
        self._get_sensor_config()
        self._wait_idle()
        self._write_reg(self.CAM_REG_DEBUG_DEVICE_ADDRESS, self.deviceAddress)
        self._wait_idle()

        self.run_start_up_config = True
        self.pixel_format = self.CAM_IMAGE_PIX_FMT_JPG
        self.old_pixel_format = self.pixel_format
        self.resolution = self.RESOLUTION_1280X720
        self.old_resolution = self.resolution
        self.set_filter(self.SPECIAL_NORMAL)
        self.received_length = 0
        self.total_length = 0
        self.burst_first_flag = False
        self.start_time = utime.ticks_ms()

        print('Camera initialized')
    
    def capture_jpg(self):
        if utime.ticks_diff(utime.ticks_ms(), self.start_time) >= self.WHITE_BALANCE_WAIT_TIME_MS:
            print('Starting capture JPG')
            if (self.old_pixel_format != self.pixel_format) or self.run_start_up_config:
                self.old_pixel_format = self.pixel_format
                self._write_reg(self.CAM_REG_FORMAT, self.pixel_format)
                self._wait_idle()

            if (self.old_resolution != self.resolution) or self.run_start_up_config:
                self.old_resolution = self.resolution
                self._write_reg(self.CAM_REG_CAPTURE_RESOLUTION, self.resolution)
                print('Setting resolution:', self.resolution)
                self._wait_idle()

            self.run_start_up_config = False
            self._clear_fifo_flag()
            self._wait_idle()
            self._start_capture()
            while self._get_bit(self.ARDUCHIP_TRIG, self.CAP_DONE_MASK) == 0:
                sleep_ms(1)
            self.received_length = self._read_fifo_length()
            self.total_length = self.received_length
            self.burst_first_flag = False

            # Read and return the captured data as a bytearray
            image_data = self._read_fifo_data()
            print('Image Captured')
            return image_data

    def _read_fifo_data(self):
        file_path = f"SD/{get_timestamp()}.jpg"
        with open(file_path, "wb") as file:
            while self.received_length > 0:
                chunk = self._read_byte()
                file.write(chunk)
        return file_path

    def _read_byte(self):
        self.cs.off()
        self.spi_bus.write(bytes([self.SINGLE_FIFO_READ]))
        data = self.spi_bus.read(1)
        data = self.spi_bus.read(1)
        self.cs.on()
        self.received_length -= 1
        return data

    def set_resolution(self, new_resolution):
        self.resolution = new_resolution

    def set_pixel_format(self, new_pixel_format):
        self.pixel_format = new_pixel_format

    def set_brightness_level(self):
        print('TODO: COMPLETE THIS FUNCTION')

    def set_filter(self, effect):
        self._write_reg(self.CAM_REG_COLOR_EFFECT_CONTROL, effect)
        self._wait_idle()

    def set_white_balance(self, environment):
        register_value = self.WB_MODE_AUTO

        if environment == 'sunny':
            register_value = self.WB_MODE_SUNNY
        elif environment == 'office':
            register_value = self.WB_MODE_OFFICE
        elif environment == 'cloudy':
            register_value = self.WB_MODE_CLOUDY
        elif environment == 'home':
            register_value = self.WB_MODE_HOME
        elif self.camera_idx == '3MP':
            print('TODO UPDATE: For best results set a White Balance setting')

        self.white_balance_mode = register_value
        self._write_reg(self.CAM_REG_WB_MODE_CONTROL, register_value)
        self._wait_idle()

    def _clear_fifo_flag(self):
        self._write_reg(self.ARDUCHIP_FIFO, self.FIFO_CLEAR_ID_MASK)

    def _start_capture(self):
        self._write_reg(self.ARDUCHIP_FIFO, self.FIFO_START_MASK)

    def _read_fifo_length(self):
        len1 = int.from_bytes(self._read_reg(self.FIFO_SIZE1), 1)
        len2 = int.from_bytes(self._read_reg(self.FIFO_SIZE2), 1)
        len3 = int.from_bytes(self._read_reg(self.FIFO_SIZE3), 1)
        print(len1, len2, len3)
        return ((len3 << 16) | (len2 << 8) | len1) & 0xffffff

    def _get_sensor_config(self):
        camera_id = self._read_reg(self.CAM_REG_SENSOR_ID)
        self._wait_idle()
        if int.from_bytes(camera_id, 1) in [self.SENSOR_3MP_1, self.SENSOR_3MP_2]:
            self.camera_idx = '3MP'
        elif int.from_bytes(camera_id, 1) in [self.SENSOR_5MP_1, self.SENSOR_5MP_2]:
            self.camera_idx = '5MP'

    def _bus_write(self, addr, val):
        self.cs.off()
        self.spi_bus.write(bytes([addr]))
        self.spi_bus.write(bytes([val]))
        self.cs.on()
        sleep_ms(1)
        return 1

    def _bus_read(self, addr):
        self.cs.off()
        self.spi_bus.write(bytes([addr]))
        data = self.spi_bus.read(1)
        data = self.spi_bus.read(1)
        self.cs.on()
        return data

    def _write_reg(self, addr, val):
        self._bus_write(addr | 0x80, val)

    def _read_reg(self, addr):
        data = self._bus_read(addr & 0x7F)
        return data

    def _set_FIFO_burst(self):
        self.spi_bus.write(bytes([self.BURST_FIFO_READ]))

    def _wait_idle(self):
        data = self._read_reg(self.CAM_REG_SENSOR_STATE)
        while int.from_bytes(data, 1) & 0x03 == self.CAM_REG_SENSOR_STATE_IDLE:
            data = self._read_reg(self.CAM_REG_SENSOR_STATE)
            sleep_ms(2)

    def _get_bit(self, addr, bit):
        data = self._read_reg(addr)
        return int.from_bytes(data, 1) & bit


