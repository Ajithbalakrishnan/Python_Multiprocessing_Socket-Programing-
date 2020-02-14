import os
#os.environ['KIVY_VIDEO'] = "gstplayer"
import kivy
from kivy.app import App
from kivy.uix.widget import Widget
from kivy.properties import ObjectProperty
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.lang import Builder
from kivy.uix.floatlayout import FloatLayout
from kivy.config import Config
from kivy.uix.image import Image
from kivy.properties import StringProperty
from kivy.core.image import Image as CoreImage
from kivy.clock import Clock
from kivy.core.window import Window
import io
import urllib
import multiprocessing
import threading
from collections import deque
import urllib.request
import random
import datetime
import pickle
import zlib
import subprocess
import cv2
from timelabel import Time
import time
window_sizes=Window.size
print("window_sizes : ", window_sizes)
# 
Config.set('graphics', 'width', '600')
Config.set('graphics', 'height', '600')
Config.set('graphics', 'borderless', '0')
Config.set('graphics', 'rotation', '90')
Config.set('graphics', 'kivy_clock', 'default')
Config.set('graphics', 'position', 'custom')
Config.set('graphics','resizable','0')
Config.set('graphics', 'left', 10)
Config.set('graphics', 'top',  10)
Config.write()

Builder.load_string("""
<Newapp>:
    orientation: "vertical"
    imgWall: imgWall
    time:time
    videoin: videoin
    FloatLayout:
        Image:
            id: imgWall
            size : 600,600
            allow_stretch: True

        Time:
            id: time
            size_hint: 0.25, 0.25
            pos_hint: {'right': 0.95, 'top': 0.95}
        Image:
            id: videoin
            size_hint: 0.5, 0.5
            pos_hint: {"x":0.30, "top":.85}

""")
class MjpegViewer(Image):

    url = StringProperty()
    
    def __init__(self,vidid, **kwargs):
        super(MjpegViewer, self).__init__(**kwargs)
        self.videoIn = vidid

    def start(self):
        self.quit = False
        self._queue = deque()
        self._thread = threading.Thread(target=self.read_stream)
        self._thread.daemon = True
        self._thread.start()
        self._image_lock = threading.Lock()
        self._image_buffer = None
        Clock.schedule_interval(self.update_image, 1 / 30.)

    def stop(self):
        self.quit = True
        self._thread.join()
        Clock.unschedule(self.read_queue)

    def read_stream(self):

        stream = urllib.request.urlopen(self.url)
        bytes = b''
        while not self.quit:
            bytes += stream.read(1024)
            
            a = bytes.find(b'\xff\xd8')
            b = bytes.find(b'\xff\xd9')

            if a != -1 and b != -1:
                jpg = bytes[a:b + 2]
                bytes = bytes[b + 2:]

                data = io.BytesIO(jpg)
                im = CoreImage(data,
                               ext="jpeg",
                               nocache=True)
                with self._image_lock:
                    self._image_buffer = im

    def update_image(self, *args):
        im = None
        with self._image_lock:
            im = self._image_buffer
            self._image_buffer = None
        if im is not None:
            self.videoIn.texture = im.texture
            self.videoIn.texture_size = im.texture.size   

class Newapp(FloatLayout):
    
    def __init__(self, **kwargs):
        super(Newapp, self).__init__(**kwargs)
        Clock.schedule_once(self.start_time_updates)
     #   self.start_video_updates()
        Clock.schedule_interval(self.update_img,.5)
    #    Clock.schedule_interval(self.ids.imgWall.source)
    
    def start_time_updates(self, dt):
        t = self.ids.time
        Clock.schedule_interval(t.updateTime,1)

    def start_video_updates(self):
        v = MjpegViewer(url= "http://172.16.35.196:8085/?action=stream", vidid=self.videoin)
        v.start()   

    def update_img(self, dt):
        if img_queue.qsize() == 0 :
            default_img = '/home/pi/ajith_rpi/kivy_UI/edited_background_2.png'
            self.ids.imgWall.source = default_img
            self.ids.imgWall.reload()
            
        else:
            data = img_queue.get()
            frame=pickle.loads(data, fix_imports=True, encoding="bytes")
            frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
            cv2.imwrite("/home/pi/ajith_rpi/final_UI_V1/img/1.jpg", frame)
            time.sleep = .1
            self.ids.imgWall.source = "/home/pi/ajith_rpi/final_UI_V1/img/1.jpg"
            self.ids.imgWall.reload()
            time.sleep = 1
            os.remove("/home/pi/ajith_rpi/final_UI_V1/img/1.jpg")
        
#        self.imgWall.texture =  im.texture
        
#        self.imgWall.source = self.img_update
# '/home/pi/ajith_rpi/kivy_UI/edited_background_2.png'        
#         while True:
#             if img_queue.qsize() > 0 :
#                 print("q size is grater than one")
#                 data = img_queue.get()
#                 frame=pickle.loads(data, fix_imports=True, encoding="bytes")
#                 frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
#                 cv2.imwrite("/home/pi/ajith_rpi/final_UI_V1/img/1.jpg", frame)
#                 self.imgWall.source = "/home/pi/ajith_rpi/final_UI_V1/img/1.jpg"
#                 time.sleep(1)
#             else :
#                self.imgWall.source = '/home/pi/ajith_rpi/kivy_UI/edited_background_2.png'
# 
    
        
#     print("update_img_queue size : ", img_queue.qsize())
#     while True:
#         if img_queue.qsize() > 0 :
#             print("q size is grater than one")
#             data = img_queue.get()
#             frame=pickle.loads(data, fix_imports=True, encoding="bytes")
#             frame = cv2.imdecode(frame, cv2.IMREAD_COLOR)
#             Newapp.display_img(frame)
            
class ButtonsApp(App):
     
     def build(self):
         return Newapp()  

img_queue = None

def start_ui(q):
    global img_queue
    img_queue = q
    ButtonsApp().run()
      