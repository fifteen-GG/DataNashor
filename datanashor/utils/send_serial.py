import serial
import time

def send_serial(port):
    py_serial = serial.Serial(
    port=port,
    baudrate=9600,
    )
    while True:
        command = 'a'
        py_serial.write(command.encode())
        time.sleep(0.1)
        if py_serial.readable():        
            response = py_serial.readline()
            print(response[:len(response)-1].decode())
            break