"""
[C02_xyzLS.py]
Purpose: store function for XYZ linear motion stage related.
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""
import serial
import time


class xyzLS:
    def __init__(self, X_coord_mm=0.0000, Y_coord_mm=0.0000, Z_coord_mm=0.0000, serial_status=0):
        self.X_coord_mm = X_coord_mm
        self.Y_coord_mm = Y_coord_mm
        self.Z_coord_mm = Z_coord_mm
        self.serial_status = serial_status


    def Ardu_open_serial(self):
        global ser, serial_status
        ser = serial.Serial('COM3', 9600, timeout=2)
        serial_status = 1
        print('Serial opened. Wait for 2 seconds.')
        time.sleep(2)


    def Ardu_close_serial(self):
        global ser, serial_status
        ser.close()
        serial_status = 0
        print('Serial closed.')


    def LS_homing(self):
        try:
            message = '0' + '\n' # Add new line symbol to mark the end of the message. 
            ser.write(message.encode())
            print('Sent message "0" to Arduino through COM3 for homing.')
            response = ''
            start_time = time.time()  # Note the start time
            while True:
                passed_time = round(time.time() - start_time, 2)
                if passed_time > 60:  # Check if 60 seconds have passed
                    print("Timeout: Did not receive expected response within 60 seconds.")
                    ser.close()
                    return
                response = ser.readline().decode().strip()  # Read the response until a newline character
                if response == "Full Homing completed.":  # Replace "READY" with the message you're waiting for
                    print('Received expected response from Arduino:', response)  # Print the received response
                    break
                else:
                    print('Waiting for expected response...', passed_time, 'seconds.', response)
        except KeyboardInterrupt:
            print("Serial communication stopped.")
        finally:
            print('LS_homing finished.')
        if response == '':
            print('No message received.')


    def LS_close_OM(self):
        try:
            message = '1' + '\n' # Add new line symbol to mark the end of the message. 
            ser.write(message.encode())
            print('Sent message "1" to Arduino through COM3 for moving close to microscope.')
            response = ''
            start_time = time.time()  # Note the start time
            while True:
                passed_time = round(time.time() - start_time, 2)
                if passed_time > 120:  # Check if 60 seconds have passed
                    print("Timeout: Did not receive expected response within 120 seconds.")
                    ser.close()
                    return
                response = ser.readline().decode().strip()
                if response == "Complete":
                    print('Received expected response from Arduino:', response)
                    break
                else:
                    print('Waiting for expected response...', passed_time, 'seconds.', response)
        except KeyboardInterrupt:
            print("Serial communication stopped.")
        if response == '':
            print('No message received.')
            
            
    def LS_under_OM(self):
        try:
            message = '21' + '\n' # Add new line symbol to mark the end of the message. 
            ser.write(message.encode())
            print('Sent message "2" to Arduino through COM3 for moving under the microscope.')
            response = ''
            start_time = time.time()  # Note the start time
            while True:
                passed_time = round(time.time() - start_time, 2)
                if passed_time > 120:  # Check if 60 seconds have passed
                    print("Timeout: Did not receive expected response within 120 seconds.")
                    ser.close()
                    return
                response = ser.readline().decode().strip()
                if response == "Complete":
                    print('Received expected response from Arduino:', response)
                    break
                else:
                    print('Waiting for expected response...', passed_time, 'seconds.', response)
        except KeyboardInterrupt:
            print("Serial communication stopped.")
        if response == '':
            print('No message received.')


    def LS_homing(self):
        try:
            message = '0' + '\n' # Add new line symbol to mark the end of the message. 
            ser.write(message.encode())
            print('Sent message "0" to Arduino through COM3 for homing.')
            response = ''
            start_time = time.time()  # Note the start time
            while True:
                passed_time = round(time.time() - start_time, 2)
                if passed_time > 60:  # Check if 60 seconds have passed
                    print("Timeout: Did not receive expected response within 60 seconds.")
                    ser.close()
                    return
                response = ser.readline().decode().strip()  # Read the response until a newline character
                if response == "Full Homing completed.":  # Replace "READY" with the message you're waiting for
                    print('Received expected response from Arduino:', response)  # Print the received response
                    break
                else:
                    print('Waiting for expected response...', passed_time, 'seconds.', response)
        except KeyboardInterrupt:
            print("Serial communication stopped.")
        finally:
            print('LS_homing finished.')
        if response == '':
            print('No message received.')



    def LS_position(self):
        try:
            message = '3' + '\n' # Add new line symbol to mark the end of the message. 
            ser.write(message.encode())
            print('Sent message "3" to Arduino through COM3 to ask for position.')
            response = ser.readline().decode().strip()  # Read the response until a newline character
            print("Received response from Arduino:", response)   # Print the received response
        except KeyboardInterrupt:
            print("Serial communication stopped.")
        finally:
            print('LS_position finished.')
        if response == '':
            print('No message received.')
        else: # Organize respond coordinate update string into values for XYZ.
            XYZ_coord_mm = response.split(' ')[1]
            print('XYZ_coord_mm', XYZ_coord_mm)
            self.X_coord_mm = XYZ_coord_mm.split(',')[0]
            self.Y_coord_mm = XYZ_coord_mm.split(',')[1]
            self.Z_coord_mm = XYZ_coord_mm.split(',')[2]
            print('X_coord_mm: ', self.X_coord_mm, '; Y_coord_mm: ', self.Y_coord_mm, '; Z_coord_mm: ', self.Z_coord_mm, sep='')