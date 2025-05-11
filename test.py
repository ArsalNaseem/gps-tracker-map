import serial

try:
    ser = serial.Serial('COM5', 115200, timeout=1)
    print("COM5 is open!")
    ser.close()
except Exception as e:
    print("Error:", e)
