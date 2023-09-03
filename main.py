import cv2
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk
from datetime import datetime
from pynput import keyboard
import threading


# Función para mostrar la hora en el canvas de Tkinter
def show_hour():
    canvas.delete("all")  # Borra todo en el canvas
    current_hour = datetime.now().strftime("%H:%M:%S")
    canvas.create_text(window_width // 2, window_height // 2, text=current_hour, font=("Helvetica", 48), fill="white")
    canvas.after(1000, show_hour)  # Cada segundo la hora se actualiza


# Función para cambiar entre la hora y el video de la cámara
def change_view():
    global showing_hour
    showing_hour = not showing_hour

    if showing_hour:
        canvas.delete("all")
        show_hour()
    else:
        canvas.delete("all")


# Función para capturar y mostrar el video en el lienzo de Tkinter
def show_video():
    if not showing_hour:
        ret, frame = cap.read()
        if ret:
            # Escala el fotograma al tamaño de la ventana
            frame = cv2.resize(frame, (window_width, window_height))
            # Convierte el fotograma en formato RGB
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            # Convierte la imagen en un formato compatible con Tkinter
            img = Image.fromarray(frame_rgb)
            img = ImageTk.PhotoImage(image=img)
            canvas.create_image(0, 0, anchor=tk.NW, image=img)
            canvas.img = img
    if not exit:  # Verifica si la bandera de salir está en False
        root.after(10, show_video)  # Llama a esta función recursivamente para obtener una actualización continua


# Función para manejar la pulsación de teclas
def on_key_press(key):
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
