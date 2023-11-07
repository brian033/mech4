import serial
import sys


class MotorClass:
    # Initializer / Constructor
    def __init__(self, port,  baud_rate):
        self.left_forward = 0
        self.left_backward = 0
        self.right_forward = 0
        self.right_backward = 0
        self.motor_ser = serial.Serial(port, baud_rate)
        self.sucky = 1

    def send_data(self, left_f, left_b, right_f, right_b, _sucky=None):
        self.left_forward = left_f
        self.left_backward = left_b
        self.right_forward = right_f
        self.right_backward = right_b

        if _sucky == 0 or _sucky == 1:
            self.sucky = _sucky

        data_string = str(left_f) + ',' + str(left_b) + \
            ',' + str(right_f) + ',' + str(right_b) + ',' + str(self.sucky)
        print(data_string)
        self.motor_ser.write(data_string.encode('utf-8'))
        data = None
        while self.motor_ser.in_waiting:
            data_raw = self.motor_ser.readline()
            data = data_raw.decode()
            # print(data)
        return data
