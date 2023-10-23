import cv2
import tkinter as tk
from tkinter import Canvas, Button, filedialog, Label
from PIL import Image, ImageTk
from datetime import datetime
from pynput import keyboard 
import threading
import time
import numpy as np
import os
import imutils
import serial

_DIR = os.path.dirname(__file__)
_VIDEO_DIR = os.path.join(_DIR, "Videos_Saved")
_PNG_DIR = os.path.join(_DIR, "imagenes")
print(_PNG_DIR)
idx = '0'
last_idx = '0'

if not os.path.exists(_VIDEO_DIR):
    os.makedirs(_VIDEO_DIR)

last_view_change_time = 0
camera_active = False
recording_active = False
record_start_time = 0
r_video = False
tmr = False
view_change_interval = 2
png_list = ["-26", "-25", "-24", "-23", "-22", "-21", "-20", "-19", "-18", "-17", "-16", "-15", "-14", "-13", "-12", "-11", "-10", "-9", "-8", "-7", "-6", "-5", "-4", "-3", "-2", "-1", "0",
            "1", "2", "3", "4", "5", "6", "7", "8", "9", "10", "11", "12", "13", "14", "15", "16", "17", "18", "19", "20", "21", "22", "23", "24", "25", "26"]


class TimerThread(threading.Thread):
    def __init__(self):
        super().__init__()
        self.start_time = None
        self.end_time = None
        self.exit_event = threading.Event()
        self.time_elapsed = 0

    def run(self):
        self.start_time = time.time()
        while not self.exit_event.is_set():
            self.time_elapsed = time.time() - self.start_time
            time.sleep(0.001)

    def stop(self):
        self.exit_event.set()
        self.end_time = time.time()

    def get_elapsed_time(self):
        if self.end_time is not None:
            return self.end_time - self.start_time
        else:
            return self.time_elapsed 

def electronic():
    global idx, counter, ser
    try:
        while True:
            if counter == 1:
                counter = 1
            
            data_received = str(ser.readline().decode().strip())
            if counter > 0:
                d = data_received.split(",")
                try:
                    if d[0] != '':
                        distance = d[0]
                        idx = d[1]
                        if int(idx) > 26 or int(idx) < -26:
                            idx = last_idx
                        last_idx = idx
                        last_distance = distance
                        print(d)
                except:
                    idx = last_idx
                    distance = last_distance

            if counter == 0:
                counter = 1
    except KeyboardInterrupt:
        ser.close()



def show_hour():
    global lock_hour
    if not lock_hour:
        canvas.delete("all")

        current_hour = datetime.now().strftime("%H:%M:%S")
        canvas.create_text(window_width // 2, window_height // 2, text=current_hour, font=("Helvetica", 48), fill="white")
        canvas.after(1000, show_hour)


def watch():
    global cap2, video_img, lock_hour
    if cap2 is not None:
        lock_hour = True
        ret, frame = cap2.read()
    if frame is None:
        lock_hour = False
        show_hour()
    if ret == True:
        frame = imutils.resize(frame, width=640)
        im = Image.fromarray(frame)
        video_img = ImageTk.PhotoImage(image=im)
        canvas.delete("all")
        canvas.create_image(0, 0, anchor=tk.NW, image=video_img)
        canvas.update()
        canvas.after(29, watch)
    else:
        #lblinfovid.configure(text="No hay ruta seleccionada")
        lock_hour = False
        video_img= None
        cap2.release() 


def open_list_folder():
    global cap2, video_img, lock_hour

    if cap2 is not None:
        lock_hour = False
        video_img = None
        cap2.release()
        cap2 = None

    vid_path = filedialog.askopenfilename(filetypes=[("all video format", ".avi")])
    print(vid_path)
    if len(vid_path) > 0:
        #lblinfovid.configure(text=vid_path)
        cap2 = cv2.VideoCapture(vid_path)
        watch()
    else:
        #lblinfovid.configure(text="No hay ruta seleccionada")
        pass

def change_view():
    global showing_hour, last_view_change_time, camera_active, out, lock_hour
    current_time = time.time()

    if current_time - last_view_change_time >= view_change_interval:
        last_view_change_time = current_time
        showing_hour = not showing_hour 

        if showing_hour:
            canvas.delete("all")
            lock_hour = False
            show_hour()
            folder_btn.config(state=tk.NORMAL)
            folder_btn.place(x=window_width - 120, y=10)
            camera_active = False
        else:
            canvas.delete("all")
            lock_hour = True
            folder_btn.config(state=tk.DISABLED)
            folder_btn.place(x=3000, y=10)
            hr = datetime.now().strftime("%H:%M:%S")
            video_path = os.path.join(_VIDEO_DIR, hr + "_recorded_video.avi")
            fourcc = cv2.VideoWriter_fourcc(*'XVID')
            out = cv2.VideoWriter(video_path, fourcc, 20.0, (window_width, window_height))
            camera_active = True


def show_video():
    global camera_active, recording_active, record_start_time, recorded_frames, r_video, tmr, out, idx

    if not showing_hour and camera_active:
        ret, frame = cap.read()
        if ret:
            frame = cv2.resize(frame, (window_width, window_height))
            png_img = _PNG_DIR + '/' + png_list[png_list.index(str(idx))] + '.png'
            image = cv2.imread(png_img, cv2.IMREAD_UNCHANGED)
            image = cv2.resize(image, (525, 156))
            x = 50
            y = 180

            y1, y2 = y, y + image.shape[0]
            x1, x2 = x, x + image.shape[1]

            alpha_s = image[:, :, 3] / 255.0
            alpha_l = 1.0 - alpha_s

            for c in range(0, 3):
                frame[y1:y2, x1:x2, c] = (alpha_s * image[:, :, c] +
                                        alpha_l * frame[y1:y2, x1:x2, c])


            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGRA2RGB)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            img = Image.fromarray(frame_rgb)
            img = ImageTk.PhotoImage(image=img)
            canvas.create_image(0, 0, anchor=tk.NW, image=img)
            canvas.img = img

            if r_video is True and tmr is False:
            
                if not recording_active:
                    recording_active = True
                    record_start_time = time.time()
                    recorded_frames = []

                if recording_active and time.time() - record_start_time < 12:
                    out.write(frame_rgb)
                    #recorded_frames.append(frame_rgb)
                    print(time.time() - record_start_time)
                
                elif recording_active and time.time() -record_start_time >= 12:
                    recording_active = False
                    tmr = True
                    out.release()
                    #save_recorded_video()  

    if not exit:
        root.after(10, show_video)


def on_key_press(key):
    global exit, recording_active, record_start_time, recorded_frames, r_video, tmr
    if key == keyboard.Key.esc:
        exit = True
        root.quit()
    elif key == keyboard.KeyCode.from_char('r'):
        r_video = not r_video
        if r_video is False:
            tmr = False
        change_view()

ser = serial.Serial("/dev/ttyS0", 115200, timeout=0.2)
counter = 0

window_width = 640
window_height = 360

root = tk.Tk()
root.title("Reproducción de Video") 

cap = cv2.VideoCapture(0)
cap2 = None
root.geometry(f"{window_width}x{window_height}")

canvas = Canvas(root, width=window_width, height=window_height, bg='black')
canvas.pack()

folder_btn = Button(root, text="Open Folder", command=open_list_folder, state=tk.NORMAL)
folder_btn.place(x=window_width - 120, y=10)

lblVideo = Label(root)
lblVideo.pack()

showing_hour = True
lock_hour = False
exit = False

show_hour()

keyboard_listener = keyboard.Listener(on_press=on_key_press)
keyboard_listener.start()

video_thread = threading.Thread(target=show_video)
video_thread.start()


electronic_thread = threading.Thread(target=electronic)
electronic_thread.start()
root.mainloop()

exit = True
video_thread.join()

cap.release()
cv2.destroyAllWindows()
   