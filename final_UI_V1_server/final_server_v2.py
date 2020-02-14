import socket  

import multiprocessing

import cv2
import io
import struct
import time
import pickle
import zlib
import subprocess
#print_lock = threading.Lock()

##### rfid #####
from time import sleep
import sys
from mfrc522 import SimpleMFRC522
reader = SimpleMFRC522()

###### GPIO Port #####
import RPi.GPIO as GPIO 
GPIO.setwarnings(False) 
GPIO.setmode(GPIO.BOARD) 
GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)
######################

dis_h = 720
dis_w = 1020

data = b""
payload_size = struct.calcsize(">L")

print("number of cpu : ", multiprocessing.cpu_count())

port_1 = 8402
port_2 = 8602

def rfid_check(q):     

    host = '172.16.35.196'  
    bashCommand ='lsof -nti:'+str(port_2)+' | xargs kill -9'
    while True:
        try:
            rfid_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            rfid_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            rfid_socket.bind((host, port_2)) 
            print("rfid_socket binded to port", port_2) 
            rfid_socket.listen(5) 
            print("rfid_socket is listening")
            rfid_sock, addr2 = rfid_socket.accept()
            
        except Exception as e:
            print(e)
            print("Check Server Ip")
            time.sleep(1)
            continue
        else:
            print('Connected to :', addr2[0], ':', addr2[1])
            break    

    GPIO.setwarnings(False)
    GPIO.cleanup()
    reader=SimpleMFRC522()
    while True:    
        try: 
            a,b = reader.read()
            ID = str(a)
            if not ID:
                print("Recieved empty string")
                GPIO.cleanup()
                time.sleep(1)
                continue
            if len(ID) < 12:
                print("Recieved bad string")
                GPIO.cleanup()
                time.sleep(1)
                continue
            print("ID = ",ID)
            rfid_sock.send(ID.encode())
            
        except:
            continue;
        finally:
            GPIO.cleanup()
        
        data = b""
        payload_size = struct.calcsize(">L")
        
        while len(data) < payload_size:
                
            data += rfid_sock.recv(2048)

            #print("Done Recv: {}".format(len(data)))
        packed_msg_size = data[:payload_size]
        data = data[payload_size:]
        msg_size = struct.unpack(">L", packed_msg_size)[0]
            #print("msg_size: {}".format(msg_size))
        while len(data) < msg_size:
            data += rfid_sock.recv(2048)
        frame_data = data[:msg_size]
        data = data[msg_size:]
        
        q.put(frame_data,False)
        print("queue size_rfid : ", q.qsize())
        #time.sleep(0.1)
        print("RFID - img recieved")        
           
    rfid_sock.close()
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()    

def fr_check(q):
    host = '172.16.35.196'  
    
    bashCommand ='lsof -nti:'+str(port_1)+' | xargs kill -9'

    while True:
        try:
            fr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            fr_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            fr_socket.bind((host, port_1)) 
            print("fr_socket binded to port", port_1) 
            fr_socket.listen(5) 
            print("fr_socket is listening")
            fr_sock, addr1 = fr_socket.accept()
            
        except Exception as e:
            print(e)
            print("Check Server Ip")
            time.sleep(1)
            continue
        else:
            print('Connected to :', addr1[0], ':', addr1[1])
            break
    
    data = b""
    payload_size = struct.calcsize(">L")
    
    while True:
        try:
            while len(data) < payload_size:
                
                data += fr_sock.recv(2048)

            #print("Done Recv: {}".format(len(data)))
            packed_msg_size = data[:payload_size]
            data = data[payload_size:]
            msg_size = struct.unpack(">L", packed_msg_size)[0]
            #print("msg_size: {}".format(msg_size))
            while len(data) < msg_size:
                data += fr_sock.recv(2048)
            frame_data = data[:msg_size]
            data = data[msg_size:]
            
            q.put(frame_data,False)
            print("queue size_FR : ", q.qsize())
            #time.sleep(0.1)
            print("FR - Img recieved")

        except Exception as e:
            print(e)
            fr_sock.close()
            cv2.destroyAllWindows()
            fr_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) 
            fr_socket.bind((host, port_1)) 
            print("fr_socket binded to port", port_1) 
            fr_socket.listen(5) 
            print("fr_socket is listening")
            fr_sock, addr1 = fr_socket.accept()
            continue
    
    fr_sock.close()
    process = subprocess.Popen(bashCommand.split(), stdout=subprocess.PIPE)
    output, error = process.communicate()
    
# def img_display(q):
#     print("img_display")
#     #cv2.destroyAllWindows()
#     frame_1=cv2.imread('/home/pi/ajith/fr_vs_pi_imagesync/edited_background.jpg')
#     frame_1=cv2.resize(frame_1, (dis_w,dis_h) )
#     winname = "ImageWindow"
#     cv2.namedWindow(winname)       
#     cv2.moveWindow(winname, 0,0)
#     cv2.imshow(winname,frame_1)
#     cv2.waitKey(5)
#     
#     while True:
#         try:
#             data = q.get(False)
#             print("queue size_img_dis : ", q.qsize()) 
#             frame=pickle.loads(data, fix_imports=True, encoding="bytes")
#             frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
#             frame=cv2.resize(frame, (dis_w,dis_h))
#                          
#             winname = "ImageWindow"
#             cv2.namedWindow(winname)       
#             cv2.moveWindow(winname, 0,0)
#             cv2.imshow(winname,frame)  
#             
#             GPIO.setmode(GPIO.BOARD) 
#             GPIO.setup(8, GPIO.OUT, initial=GPIO.LOW)
#             GPIO.output(8, GPIO.HIGH) 
#             sleep(.1)
#             cv2.waitKey(1000)
#             GPIO.output(8, GPIO.LOW) 
#             sleep(.1) 
#             
#             frame_1=cv2.imread('/home/pi/ajith/fr_vs_pi_imagesync/edited_background.jpg')
#             frame_1=cv2.resize(frame_1, (dis_w,dis_h) )
#             winname = "ImageWindow"
#             cv2.namedWindow(winname)       
#             cv2.moveWindow(winname, 0,0)
#             cv2.imshow(winname,frame_1)
#             cv2.waitKey(5)
#         
#         except Exception as e:
#             continue
        


# if __name__ == '__main__': 
#     Main() 
