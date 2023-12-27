import utime, onewire, ntptime, machine, ds18x20, time

def get_timestamp():
    timezone_offset = 5 * 60 * 60 + 30 * 60
    try: ntptime.settime()
    except ImportError: pass  
    current_time = utime.time()
    ist_time = current_time + timezone_offset
    formatted_time = utime.localtime(ist_time)
    timestamp = "{:04}{:02}{:02}{:02}{:02}{:02}".format(*formatted_time[:6])
    return str(timestamp)

class TemperatureProbe:
    def __init__(self, pin_num):
        self.onewire = onewire.OneWire(machine.Pin(pin_num))
        self.sensor = ds18x20.DS18X20(self.onewire)
        self.probe_address = self.sensor.scan()[0]  # Assuming only one temperature probe connected

    def read_temperature(self):
        self.sensor.convert_temp()
        time.sleep_ms(750)
        temperature = self.sensor.read_temp(self.probe_address)
        return int(temperature)


