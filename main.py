import cv2
import tkinter as tk
from tkinter import Canvas, Button, filedialog
from PIL import Image, ImageTk
from datetime import datetime
from pynput import keyboard 
import threading
import time
import numpy as np
import math
import subprocess
import os

_DIR = os.path.dirname(__file__)
_VIDEO_DIR = os.path.join(_DIR, "Videos_Saved")
# Variable donde se guarda el rastreo del ultimo cambio de vista
last_view_change_time = 0

# Intervalo de tiempo en segundos
view_change_interval = 2  # Cambio de vista permitido cada 2 segundos

#Define las dimensiones del trapecio (0-1)
base_mayor = 0.6
base_menor = 0.4
altura = 0.35

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
            time.sleep(0.001)  # update time every second

    def stop(self):
        self.exit_event.set()
        self.end_time = time.time()

    def get_elapsed_time(self):
        if self.end_time is not None:
            return self.end_time - self.start_time
        else:
            return self.time_elapsed 


# Función para mostrar la hora en el canvas de Tkinter
def show_hour():
    canvas.delete("all")  # Borra todo en el canvas

    current_hour = datetime.now().strftime("%H:%M:%S")
    canvas.create_text(window_width // 2, window_height // 2, text=current_hour, font=("Helvetica", 48), fill="white")
    canvas.after(1000, show_hour)  # Cada segundo la hora se actualiza

def open_list_folder():
    global folder_path
    folder_path = filedialog.askdirectory()

# Función para cambiar entre la hora y el video de la cámara
def change_view():
    global showing_hour, last_view_change_time, camera_active
    current_time = time.time()

    if current_time - last_view_change_time >= view_change_interval:
        last_view_change_time = current_time
        showing_hour = not showing_hour

        if showing_hour:
            canvas.delete("all")
            show_hour()
            folder_btn.config(state=tk.NORMAL)
            folder_btn.place(x=window_width - 120, y=10)
            camera_active = False
        else:
            canvas.delete("all")
            folder_btn.config(state=tk.DISABLED)
            folder_btn.place(x=3000, y=10)
            camera_active = True


# Función para capturar y mostrar el video en el lienzo de Tkinter
def show_video():
    global camera_active
    if not showing_hour and camera_active:
        ret, frame = cap.read()
        if ret:
            # Escala el fotograma al tamaño de la ventana
            frame = cv2.resize(frame, (window_width, window_height))
            # Convierte el fotograma en formato RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            
            # Calcula las coordenadas de los vértices del trapecio en función de las medidas definidas
            trapezoid_vertices = [
                (int(window_width * (0.5 - base_mayor / 2)), window_height),
                (int(window_width * (0.5 + base_mayor / 2)), window_height),
                (int(window_width * (0.5 + base_menor / 2)), int(window_height * (1 - altura))),
                (int(window_width * (0.5 - base_menor / 2)), int(window_height * (1 - altura)))
            ]
            
            # Dibuja las líneas del trapecio en la imagen original
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            cv2.polylines(frame_rgb, [np.array(trapezoid_vertices)], isClosed=True, color=(255, 0, 0), thickness=2)
            
            # Convierte la imagen en un formato compatible con Tkinter
            img = Image.fromarray(frame_rgb)
            img = ImageTk.PhotoImage(image=img)
            canvas.create_image(0, 0, anchor=tk.NW, image=img)
            canvas.img = img
    if not exit:  # Verifica si la bandera de salir está en False
        root.after(10, show_video)  # Llama a esta función recursivamente para obtener una actualización continua


# Función para manejar la pulsación de teclas
def on_key_press(key):
    global exit
    if key == keyboard.Key.esc:
        exit = True
        root.quit()
    elif key == keyboard.KeyCode.from_char('r'):
        change_view()


# Cambia estos valores según tus preferencias
window_width = 640
window_height = 360
# Inicializa la ventana de Tkinter
root = tk.Tk()
root.title("Reproducción de Video") 

# Inicializa la cámara (cambia el índice a 0 si quieres usar la cámara predeterminada)
cap = cv2.VideoCapture(0)  # Utiliza la cámara predeterminada (cambia el índice si es necesario)

# Establece la geometría de la ventana con valores predeterminados
root.geometry(f"{window_width}x{window_height}")

# Inicializa el canvas para mostrar la hora al inicio
canvas = Canvas(root, width=window_width, height=window_height, bg='black')
canvas.pack()

folder_btn = Button(root, text="Open Folder", command=open_list_folder, state=tk.NORMAL)
folder_btn.place(x=window_width - 120, y=10)

# Bandera para controlar qué se está mostrando True para que se muestre primero la fecha
showing_hour = True

# Bandera para controlar si el programa debe salir
exit = False

# Llama a la función para mostrar la hora al inicio
show_hour()

# Configura la función para cambiar la vista al presionar 'R' o 'r'
keyboard_listener = keyboard.Listener(on_press=on_key_press)
keyboard_listener.start()

# Inicializa un subproceso para mostrar el video de manera continua
video_thread = threading.Thread(target=show_video)
video_thread.start()

# Inicia el bucle principal de Tkinter
root.mainloop()

# Cuando se cierra la ventana, establece la bandera 'salir' en True para detener el hilo del video
exit = True
# Espera a que el hilo del video termine
video_thread.join()  # Espera a que el hilo del video termine

# Libera la cámara y cierra la ventana al salir
cap.release()
cv2.destroyAllWindows()
