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

def flasher(pin_no, mode):
    pin = machine.Pin(pin_no, machine.Pin.OUT)
    if mode == "on":pin.on()
    elif mode == "off":pin.off()
    else:print("Invalid mode. Use 'on' or 'off'.")

def soft_reset(feed):
    if feed > 3:
        print("Performing soft reset...")
        machine.reset()
    else:pass