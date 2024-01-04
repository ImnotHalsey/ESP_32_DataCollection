from machine import UART, Pin


def read_and_process_data(start_char, end_char, success_code):
    uart = UART(2, 115200, tx=Pin(17), rx=Pin(16))
    buffer = bytearray()
    while True:
        if uart.any():
            byte = uart.read(1)
            
            if start_char in byte:
                buffer = byte
            else:
                buffer += byte

            if buffer.endswith(end_char):
                try:
                    data_str = buffer.decode('utf-8').strip(start_char.decode() + end_char.decode())
                    data_list = data_str.split(',')
                    uart.write(success_code + '\n')
                    print("Processed data:", data_list)
                    return data_list
                except Exception as e:
                    print("Error processing data:", e)
                buffer = bytearray()

while True:
    log = read_and_process_data(b'<', b'>', '2020')
