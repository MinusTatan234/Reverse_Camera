import cv2
import RPi.GPIO
import tkinter as tk
from tkinter import Canvas
from PIL import Image, ImageTk

# funcion que muestra el video dentro de un canvas de tkinter
def show_video():
    ret, frame = cap.read() 
    if ret:
        frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB) # De BGR a RGB
        # Transformación de la imagen para que sea compatible con tkinter
        img = Image.fromarray(frame_rgb)
        img = ImageTk.PhotoImage(image=img)
        canvas.create_image(0, 0, anchor=tk.NW, image=img)
        canvas.img = img
        # Actualización del frame
        canvas.after(10, show_video)

# Inicialización del objeto tkinter
root = tk.Tk()
root.title("Test video")
# Captura de video desde una camara
cap = cv2.VideoCapture(0)
# Creacion del canvas para mostrar el video
canvas = Canvas(root, width=cap.get(6), height=cap.get(8))
canvas.pack()
# Llamada de la función que muestra video
show_video()
# Main loop de tkinter
root.mainloop()
# Cierre de opencv 
cap.release()
cv2.destroyAllWindows()
