"""
[F08_LS.py]
Purpose: Linear stage functions.
Author: Meng-Chi Ed Chen
Date: 2023-06-06
Reference:
    1.
    2.

Status: Complete.
"""





import os, sys, cv2, datetime, serial, time
import numpy as np

import C03_ImageProcessor as C03_ImageProcessor
import F03_Image as F03_Image # type: ignore
import F09_OMcam as F09_OMcam # type: ignore





def stream_movement_capture(dir_captured_images, step_to_try):
    global X_coord_mm, Y_coord_mm, Z_coord_mm
    X_coord_mm = 0
    Y_coord_mm = 0
    Z_coord_mm = 0
    #[] Open serial port
    ser = serial.Serial('COM3', 9600, timeout=2)
    time.sleep(2) 
    print('Serial opened. Wait for 2 seconds.')
    time.sleep(2)  
    
    print('Opening VideoCapture. Wait for about 10 seconds.')
    capture = cv2.VideoCapture(1) # Open the first camera device

    if not capture.isOpened():
        print("Error: Couldn't open the camera.")
        return

    while True:
        """
        [Key Lists]
        '=': capture frame
        '-': quit
        ' ': start your thing
        '/': start your thing

        """
        

        ret, frame = capture.read() # Capture frame-by-frame
        if not ret:
            print("Error: Couldn't capture a frame.")
            break

        cv2.imshow('Camera Stream', frame) # Display the resulting frame
        key = cv2.waitKey(1) & 0xFF
        
        if key == ord('='): #[] Capture the frame if '=' is pressed
            F09_OMcam.capture_image(frame, dir_captured_images)
            F09_OMcam.calculate_blur_metric(frame)
            
        # Break the loop if '-' is pressed
        elif key == ord('-'):
            ser.close()  # Close the serial connection when done
            break
        
        
        
        #[] We don't need to put movement order with mutiplication here, such as "P3" means do P for 3 times, and P is -0.1 mm on x-axis.
        elif key == ord('/'):
            print('Provide movement order in capitalized alphabet with mutiplication from 2-9. e.g. "P3"')
            #user_input = input("Please enter a message and press Enter: ")
            #message = 'user_input' + '\n'
            #ser.write(message.encode())


        elif key == ord(' '):
            print('Start moving X until see edge.')
            
            for iter_step in range(step_to_try):
                print('\n\n[step_to_try]', iter_step, 'of', step_to_try)
                edge_found = 0
                ret, frame = capture.read()
                time.sleep(1) 
                
                #[] Move X right(+) for 0.1 mm.
                ser.write('M\n'.encode())
                X_coord_mm = X_coord_mm + 0.1000
                print('Moved X right(+) for 100 um. X_coord_mm =', "%0.4f" %X_coord_mm)
                
                #[] Capture image.
                just_captured_image_path = F09_OMcam.capture_image(frame, dir_captured_images)
                F09_OMcam.calculate_blur_metric(frame)
                
                #[] Find edge.
                edge_found = 0
                ImgP = C03_ImageProcessor.ImageProcessor(just_captured_image_path)  
                blue_channel = ImgP.image_color_channel_extract(compress = 10, channel='B')
                std_blue_channel = ImgP.single_channel_std(blue_channel, 10, 10)
                print('std_blue_channel:\n', std_blue_channel)
                #print('ImgP.max_std:\n', ImgP.max_std)
                square_std_blue_channel = F03_Image.ndarray_to_square(std_blue_channel)
                print('square_std_blue_channel:\n', square_std_blue_channel)
                filter = F03_Image.square_matrix_center_1s(F03_Image.shape)
                dot_result = np.sum(square_std_blue_channel * filter)
                print('[dot_result] =', dot_result)
                
                if dot_result > 300:
                    edge_found = 0
                    print('Edge found! (High blue channel contrast.)')
                    path_image = ImgP.save_PIL_image(blue_channel, replace_old_dis = '.png', with_new_dis = '_1-blue.png')
                    F03_Image.quick_correction(path_image, 1)
                    F03_Image.find_Hough_Line(path_image)
                    print('line_direction_deg:', F03_Image.line_direction_deg)
                    break
                
                print('\n\n')
                
                
                
                
                
                
                
                
                
                
                if edge_found == 1:
                    break
            
            
        #[1 step = 0.0025 mm = 2.5 um]
        elif key == ord('A'):
            try: #[] Move X right(+) for 0.0025 mm = 2.5 um.
                message = 'A' + '\n'
                ser.write(message.encode())
                X_coord_mm = X_coord_mm + 0.0025
                print('Moved X right(+) for 2.5 um. X_coord_mm =', "%0.4f" %X_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('B'):
            try: #[] Move Y right(+) for 0.0025 mm = 2.5 um..
                message = 'B' + '\n'
                ser.write(message.encode())
                Y_coord_mm = Y_coord_mm + 0.0025
                print('Moved Y right(+) for 2.5 um. Y_coord_mm =', "%0.4f" %Y_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('C'):
            try: #[] Move Z up(+) for 0.0025 mm = 2.5 um.
                message = 'C' + '\n'
                ser.write(message.encode())
                Z_coord_mm = Z_coord_mm + 0.0025
                print('Moved Z up(+) for 2.5 um. Z_coord_mm =', "%0.4f" %Z_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('D'):
            try: #[] Move X left(-) for 0.0025 mm = 2.5 um.
                message = 'D' + '\n'
                ser.write(message.encode())
                X_coord_mm = X_coord_mm - 0.0025
                print('Moved X left(-) for 2.5 um. X_coord_mm =', "%0.4f" %X_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('E'):
            try: #[] Move Y back(-) for 0.0025 mm = 2.5 um.
                message = 'E' + '\n'
                ser.write(message.encode())
                Y_coord_mm = Y_coord_mm - 0.0025
                print('Moved Y back(-) for 2.5 um. Y_coord_mm =', "%0.4f" %Y_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('F'):
            try: #[] Move Z down(-) for 0.0025 mm = 2.5 um.
                message = 'F' + '\n'
                ser.write(message.encode())
                Z_coord_mm = Z_coord_mm - 0.0025
                print('Moved Z down(-) for 2.5 um. Z_coord_mm =', "%0.4f" %Z_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")






        #[4 steps = 0.01 mm = 10 um]
        elif key == ord('G'):
            try: #[] Move X right(+) for 0.01 mm = 10 um.
                message = 'G' + '\n'
                ser.write(message.encode())
                X_coord_mm = X_coord_mm + 0.01
                print('Moved X right(+) for 10 um. X_coord_mm =', "%0.4f" %X_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('H'):
            try: #[] Move Y right(+) for 0.01 mm = 10 um.
                message = 'H' + '\n'
                ser.write(message.encode())
                Y_coord_mm = Y_coord_mm + 0.01
                print('Moved Y right(+) for 10 um. Y_coord_mm =', "%0.4f" %Y_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('I'):
            try: #[] Move Z up(+) for 0.01 mm = 10 um.
                message = 'I' + '\n'
                ser.write(message.encode())
                Z_coord_mm = Z_coord_mm + 0.01
                print('Moved Z up(+) for 10 um. Z_coord_mm =', "%0.4f" %Z_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('J'):
            try: #[] Move X left(-) for 0.01 mm = 10 um.
                message = 'J' + '\n'
                ser.write(message.encode())
                X_coord_mm = X_coord_mm - 0.01
                print('Moved X left(-) for 10 um. X_coord_mm =', "%0.4f" %X_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('K'):
            try: #[] Move Y back(-) for 0.01 mm = 10 um..
                message = 'K' + '\n'
                ser.write(message.encode())
                Y_coord_mm = Y_coord_mm - 0.01
                print('Moved Y back(-) for 10 um. Y_coord_mm =', "%0.4f" %Y_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('L'):
            try: #[] Move Z down(-) for 0.01 mm = 10 um.
                message = 'L' + '\n'
                ser.write(message.encode())
                Z_coord_mm = Z_coord_mm - 0.01
                print('Moved Z down(-) for 10 um. Z_coord_mm =', "%0.4f" %Z_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        
        
        
        
        
        
        
        
        #[40 steps = 0.1 mm = 100 um]
        elif key == ord('M'):
            try: #[] Move X right(+) for 0.1 mm = 100 um.
                message = 'M' + '\n'
                ser.write(message.encode())
                X_coord_mm = X_coord_mm + 0.1
                print('Moved X right(+) for 0.1 mm = 100 um. X_coord_mm =', "%0.4f" %X_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('N'):
            try: #[] Move Y right(+) for 0.1 mm = 100 um.
                message = 'N' + '\n'
                ser.write(message.encode())
                Y_coord_mm = Y_coord_mm + 0.1
                print('Moved Y right(+) for 0.1 mm = 100 um. Y_coord_mm =', "%0.4f" %Y_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('O'):
            try: #[] Move Z up(+) for 0.1 mm = 100 um.
                message = 'O' + '\n'
                ser.write(message.encode())
                Z_coord_mm = Z_coord_mm + 0.1
                print('Moved Z up(+) for 0.1 mm = 100 um. Z_coord_mm =', "%0.4f" %Z_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('P'):
            try: #[] Move X left(-) for 0.1 mm = 100 um.
                message = 'P' + '\n'
                ser.write(message.encode())
                X_coord_mm = X_coord_mm - 0.1
                print('Moved X left(-) for 0.1 mm = 100 um. X_coord_mm =', "%0.4f" %X_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('Q'):
            try: #[] Move Y back(-) for 0.1 mm = 100 um..
                message = 'Q' + '\n'
                ser.write(message.encode())
                Y_coord_mm = Y_coord_mm - 0.1
                print('Moved Y back(-) for 0.1 mm = 100 um. Y_coord_mm =', "%0.4f" %Y_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('R'):
            try: #[] Move Z down(-) for 0.1 mm = 100 um.
                message = 'R' + '\n'
                ser.write(message.encode())
                Z_coord_mm = Z_coord_mm - 0.1
                print('Moved Z down(-) for 0.1 mm = 100 um. Z_coord_mm =', "%0.4f" %Z_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        
        
        
        
        
        
        #[400 steps = 1 mm = 1000 um]
        elif key == ord('S'):
            try: #[] Move X right(+) for 1 mm = 1000 um.
                message = 'S' + '\n'
                ser.write(message.encode())
                X_coord_mm = X_coord_mm + 1
                print('Moved X right(+) for 1 mm = 1000 um. X_coord_mm =', "%0.4f" %X_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('T'):
            try: #[] Move Y right(+) for 1 mm = 1000 um.
                message = 'T' + '\n'
                ser.write(message.encode())
                Y_coord_mm = Y_coord_mm + 1
                print('Moved Y right(+) for 1 mm = 1000 um. Y_coord_mm =', "%0.4f" %Y_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('U'):
            try: #[] Move Z up(+) for 1 mm = 1000 um.
                message = 'U' + '\n'
                ser.write(message.encode())
                Z_coord_mm = Z_coord_mm + 1
                print('Moved Z up(+) for 1 mm = 1000 um. Z_coord_mm =', "%0.4f" %Z_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('V'):
            try: #[] Move X left(-) for 1 mm = 1000 um.
                message = 'V' + '\n'
                ser.write(message.encode())
                X_coord_mm = X_coord_mm - 1
                print('Moved X left(-) for 1 mm = 1000 um. X_coord_mm =', "%0.4f" %X_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('W'):
            try: #[] Move Y back(-) for 1 mm = 1000 um.
                message = 'W' + '\n'
                ser.write(message.encode())
                Y_coord_mm = Y_coord_mm - 1
                print('Moved Y back(-) for 1 mm = 1000 um. Y_coord_mm =', "%0.4f" %Y_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('X'):
            try: #[] Move Z down(-) for 1 mm = 1000 um.
                message = 'X' + '\n'
                ser.write(message.encode())
                Z_coord_mm = Z_coord_mm - 1
                print('Moved Z down(-) for 1 mm = 1000 um. Z_coord_mm =', "%0.4f" %Z_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")







        #[4000 steps = 10 mm = 10000 um]
        elif key == ord('4'):
            try: #[] Move X right(+) for 10 mm = 10000 um.
                message = '4' + '\n'
                ser.write(message.encode())
                X_coord_mm = X_coord_mm + 1
                print('Moved X right(+) for 10 mm = 10000 um. X_coord_mm =', "%0.4f" %X_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('5'):
            try: #[] Move Y right(+) for 10 mm = 10000 um.
                message = '5' + '\n'
                ser.write(message.encode())
                Y_coord_mm = Y_coord_mm + 1
                print('Moved Y right(+) for 10 mm = 10000 um. Y_coord_mm =', "%0.4f" %Y_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('6'):
            try: #[] Move Z up(+) for 10 mm = 10000 um.
                message = '6' + '\n'
                ser.write(message.encode())
                Z_coord_mm = Z_coord_mm + 1
                print('Moved Z up(+) for 10 mm = 10000 um. Z_coord_mm =', "%0.4f" %Z_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('7'):
            try: #[] Move X left(-) for 10 mm = 10000 um.
                message = '7' + '\n'
                ser.write(message.encode())
                X_coord_mm = X_coord_mm - 1
                print('Moved X left(-) for 10 mm = 10000 um. X_coord_mm =', "%0.4f" %X_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('8'):
            try: #[] Move Y back(-) for 10 mm = 10000 um.
                message = '8' + '\n'
                ser.write(message.encode())
                Y_coord_mm = Y_coord_mm - 1
                print('Moved Y back(-) for 10 mm = 10000 um. Y_coord_mm =', "%0.4f" %Y_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")
        
        elif key == ord('9'):
            try: #[] Move Z down(-) for 10 mm = 10000 um.
                message = '9' + '\n'
                ser.write(message.encode())
                Z_coord_mm = Z_coord_mm - 1
                print('Moved Z down(-) for 10 mm = 10000 um. Z_coord_mm =', "%0.4f" %Z_coord_mm)
            except KeyboardInterrupt:
                print("Serial communication stopped.")