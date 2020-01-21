import socket  
#from _thread import *
#import threading 

#print_lock = threading.Lock()

import multiprocessing

import cv2
import random
import string
import os 
import mysql.connector as frdb
from mysql.connector import Error
from datetime import datetime
import time
# Socket programing
#import socket
import sys
import pickle
import numpy as np
import struct
import zlib
import subprocess

print("number of cpu", multiprocessing.cpu_count())

fr_result_dir ='/home/ajith/vijnalabs/Executables_18_04/FR/syncdata/up/result/'
fr_thumbnails_dir = '/home/ajith/vijnalabs/Executables_18_04/FR/syncdata/down/thumbnails/'
background_img = cv2.imread("/home/ajith/vijnalabs/Assignments/RPI_live_stream/python-video-stream/fr_vs_pi_imagesync/edited_background.jpg")

dis_h = 550
dis_w = 750

port_1 = 8401
port_2 = 8601

img_counter = 0
encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 80]
time.sleep(.5) 

def overlay_image_alpha(img, img_overlay, pos, alpha_mask):

    x, y = pos

    # Image ranges
    y1, y2 = max(0, y), min(img.shape[0], y + img_overlay.shape[0])
    x1, x2 = max(0, x), min(img.shape[1], x + img_overlay.shape[1])

    # Overlay ranges
    y1o, y2o = max(0, -y), min(img_overlay.shape[0], img.shape[0] - y)
    x1o, x2o = max(0, -x), min(img_overlay.shape[1], img.shape[1] - x)

    # Exit if nothing to do
    if y1 >= y2 or x1 >= x2 or y1o >= y2o or x1o >= x2o:
        return

    channels = img.shape[2]

    alpha = alpha_mask[y1o:y2o, x1o:x2o]
    alpha_inv = 1.0 - alpha

    for c in range(channels):
        img[y1:y2, x1:x2, c] = (alpha * img_overlay[y1o:y2o, x1o:x2o, c] +
                                alpha_inv * img[y1:y2, x1:x2, c])
    return img 

def rfid_check():
    # message_2 = "rfid socket is working"
    # fr_sock.send(message_1.encode('ascii')) 
    print("rfid_check")
    host = "172.16.35.198"  
    
    
    while True:
        try:
            rfid_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            rfid_sock.connect((host,port_2))

        except Exception as e:
            print(e)
            print("Waiting for Main Server to Respond")
            print("Please Check Ip addr and Port Number")
            rfid_sock.close()
            time.sleep(1)
            continue
        else:
            print("Connected to Server")
            break     

    print("rfid socket is connected")

    while True:

        data = rfid_sock.recv(1024) 
        
        if not data:
            print("Recieved Void Data_1")
            continue
        if len(data) < 12:
            print("Recieved Void Data_2")
            continue

        print('Received from the client :',str(data.decode()))
        data = str(data.decode())
        connection = frdb.connect(host='localhost',database='suspecttrackerdb',
                                user='root',password='vijnalabs')

        user_table = "select * from user where RFID_Number =" + data
        cursor= connection.cursor()
        cursor.execute(user_table)
        user = cursor.fetchall()
        cursor.close()
        connection.close()

        user_list = [item for t in user for item in t] 

        person_name = 'Name : ' +str(user_list[1])
        person_id = 'Person ID : ' + str(user_list[0])
        
        print(person_name)
        print(person_id)

        background_img = cv2.imread("/home/ajith/vijnalabs/Assignments/RPI_live_stream/python-video-stream/fr_vs_pi_imagesync/edited_background.jpg")
        fr_thumbnails_dir = "/home/ajith/vijnalabs/Executables_18_04/FR/syncdata/down/thumbnails/"
        result_img = cv2.imread(fr_thumbnails_dir + str(user_list[0]) + '/thumbnail.jpg')
        cv2.imshow("result image",result_img)
        cv2.waitKey(500)
        cv2.destroyAllWindows()
        
        result_img_cropped = cv2.resize(result_img, (210,210))
        
        result_img_edit = cv2.cvtColor(result_img_cropped, cv2.COLOR_RGB2RGBA).copy()
        rpi_img = overlay_image_alpha(background_img,
                        result_img_cropped[:, :, 0:3],
                        (50, 100),
                        result_img_edit[:, :, 3] / 255.0)
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(rpi_img, person_name, (50,350), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
        cv2.putText(rpi_img, person_id, (50,380), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

        result, frame = cv2.imencode('.jpg', rpi_img, encode_param)
        data = pickle.dumps(frame, 0)
        size = len(data)

        try:
            rfid_sock.sendall(struct.pack(">L", size) + data)  
        except Exception as e: 
            print(e)
            rfid_sock.close()
            time.sleep(.1)
            rfid_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            rfid_sock.connect((host,port_2))
            continue

    rfid_sock.close()

def fr_check():
    
    print("FR_Check") 
    host = '172.16.35.198' 
    
    while True:
        try:
            fr_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
            fr_sock.connect((host,port_1))

        except Exception as e:
            print(e)
            print("Waiting for Main Server to Respond")
            print("Please Check Ip addr and Port Number")
            fr_sock.close()
            time.sleep(.5)
            continue
        else:
            print("Connected to Server_1")
            break  

    print("FR Socket is connected")

    while True:
        connection = frdb.connect(host='localhost',database='suspecttrackerdb',
                                user='root',password='vijnalabs')

        select_table = "select * from fr_algorithm_log_upload"
        cursor= connection.cursor()
        cursor.execute(select_table)
        table = cursor.fetchall()
        last_entry = cursor.rowcount

        print("last entry", last_entry)
        
        if last_entry > 1 :
            request_id = table[(last_entry-1)][0]
            sql_Delete_query = "Delete from fr_algorithm_log_upload where RequestID =" + str(request_id)
            cursor.execute(sql_Delete_query)
            connection.commit()
            # sql_select_query = "select * from fr_algorithm_log_upload"
            # cursor.execute(sql_select_query)
            # records = cursor.fetchall()
            # if len(records) == 0:
            #     print("\nRecord Deleted successfully ")    

        user_table = "select * from user"
        cursor.execute(user_table)
        user = cursor.fetchall()
        cursor.close()
        connection.close()

        print("Total entries in table : ", last_entry)
        last_entry=last_entry-1
        time_date_last_entry = table[last_entry][2]
        
        DetectedPersonID = table[last_entry][3]
    
        current_time = datetime.now()

        tdelta= (current_time - time_date_last_entry)

        diff_minutes = divmod(tdelta.seconds, 60) 

        diff_seconds = ((diff_minutes[0]*60)+diff_minutes[1])
        print("diff_seconds", diff_seconds)
        
        if diff_seconds <= 4 :
            background_img = cv2.imread("/home/ajith/vijnalabs/Assignments/RPI_live_stream/python-video-stream/fr_vs_pi_imagesync/edited_background.jpg")
            result = table[last_entry][1]
            print("DetectedPersonID", DetectedPersonID)
            result_img = cv2.imread(fr_thumbnails_dir+str(DetectedPersonID)+'/thumbnail.jpg')
            
            DetectedPersonID = DetectedPersonID -1
            user_name = user[DetectedPersonID][1]

            result_img_cropped=cv2.resize(result_img, (220,220)) 

            result_img_edit = cv2.cvtColor(result_img_cropped, cv2.COLOR_RGB2RGBA).copy()
            rpi_img = overlay_image_alpha(background_img,
                        result_img_cropped[:, :, 0:3],
                        (50, 100),
                        result_img_edit[:, :, 3] / 255.0)
            #print(rpi_img.shape)
            font = cv2.FONT_HERSHEY_SIMPLEX
            user_name = 'Name : ' + user_name
            Person_ID = 'Person ID : ' + str(table[last_entry][3])
            print(user_name)
            print(Person_ID)
            cv2.putText(rpi_img, user_name, (50,350), font, 1, (0, 255, 0), 2, cv2.LINE_AA)
            cv2.putText(rpi_img, Person_ID, (50,380), font, 1, (0, 255, 0), 2, cv2.LINE_AA)

            result, frame = cv2.imencode('.jpg', rpi_img, encode_param)
            data = pickle.dumps(frame, 0)
            size = len(data)

        #   print("{}: {}".format(img_counter, size))
        # print(socket_connection.recv(1024))
            
            try:
                fr_sock.sendall(struct.pack(">L", size) + data)   
                cv2.imshow("result image",result_img)
                cv2.waitKey(500)
                cv2.destroyAllWindows() 
            except Exception as e: 
                print(e)
                fr_sock.close()
                time.sleep(.1)
                fr_sock = socket.socket(socket.AF_INET,socket.SOCK_STREAM) 
                fr_sock.connect((host,port_1))
                continue
        else:
            print("No Detection")
            time.sleep(.5)
    fr_sock.close()


def Main():

    print("main start")

    fr = multiprocessing.Process(target=fr_check)
    rfid = multiprocessing.Process(target=rfid_check)
    fr.start()
    rfid.start()

#    print_lock.acquire()
#    start_new_thread(fr_check, ())
#    start_new_thread(rfid_check, ()) 
#    data = fr_sock.recv(1024) 
#    print('Received from the server :',str(data.decode('ascii')))
    print("main end")

if __name__ == '__main__': 
    Main() 
       

       	
 
