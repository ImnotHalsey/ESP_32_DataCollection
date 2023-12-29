import utime, ntptime, machine, errno

def flasher(pin_no, mode):
    pin = machine.Pin(pin_no, machine.Pin.OUT)
    if mode == "on":pin.on()
    elif mode == "off":pin.off()
    else:print("Invalid mode. Use 'on' or 'off'.")

def get_timestamp():
    if utime.localtime()[0] > 2022:
        pass
    else:
        try:
            ntptime.settime()
        except OSError as e:
            if e.args[0] == errno.ETIMEDOUT:
                print("Error: NTP server timed out. Using local time instead.")
            else:
                raise e
    
    timestamp = "{:04}{:02}{:02}{:02}{:02}{:02}".format(*utime.localtime(utime.time() + (5 * 60 * 60 + 30 * 60))[:6])
    print(timestamp)
    return timestamp
