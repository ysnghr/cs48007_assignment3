import datetime as dt
import picamera
import time
import os
from subprocess import call
destination =  os.getcwd()

filename = ''
def get_file_name():
    return os.path.join(destination, dt.datetime.now().strftime('%Y-%m-%d_%H.%M.%S.h264'))
    
def record_video(seconds):
    camera = picamera.PiCamera()
    
    camera.start_preview()
    camera.start_recording(filename)
    time.sleep(seconds)
    camera.stop_recording()
    camera.stop_preview()

filename = get_file_name()
record_video(10)

command  = 'MP4Box -add  '+filename + ' ' + filename.replace('h264', 'mp4')

call([command], shell = True)