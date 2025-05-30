import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk

# Define color range for drawing (HSV)
# Define color range for blue (HSV)
LOWER_COLOR = np.array([100, 150, 70])
UPPER_COLOR = np.array([140, 255, 255])


# Global canvas
canvas_points = []

# Track drawing state
drawing = True

# Clear the canvas
def clear_canvas():
    global canvas_points
    canvas_points = []

# Toggle drawing on/off
def toggle_draw():
    global drawing
    drawing = not drawing
    toggle_btn.config(text="Draw: ON" if drawing else "Draw: OFF")

# Update video frame in GUI
def update_frame():
    global canvas_points

    ret, frame = cap.read()
    if not ret:
        return

    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, LOWER_COLOR, UPPER_COLOR)
    mask = cv2.erode(mask, None, iterations=2)
    mask = cv2.dilate(mask, None, iterations=2)

    cnts, _ = cv2.findContours(mask.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    center = None

    if len(cnts) > 0:
        c = max(cnts, key=cv2.contourArea)
        if cv2.contourArea(c) > 500:
            ((x, y), radius) = cv2.minEnclosingCircle(c)
            M = cv2.moments(c)
            if M["m00"] > 0:
                center = (int(M["m10"] / M["m00"]), int(M["m01"] / M["m00"]))
                if drawing:
                    canvas_points.append(center)

    for i in range(1, len(canvas_points)):
        if canvas_points[i - 1] is None or canvas_points[i] is None:
            continue
        cv2.line(frame, canvas_points[i - 1], canvas_points[i], (0, 255, 255), 5)

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)

    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)
    video_label.after(10, update_frame)

# ------------------- GUI Setup ------------------- #

root = tk.Tk()
root.title("🎨 AI Doodle Cam")
root.geometry("800x600")
root.resizable(False, False)
root.configure(bg="#1e1e1e")

video_label = tk.Label(root)
video_label.pack(pady=10)

btn_frame = tk.Frame(root, bg="#1e1e1e")
btn_frame.pack()

clear_btn = ttk.Button(btn_frame, text="🧹 Clear Canvas", command=clear_canvas)
clear_btn.grid(row=0, column=0, padx=10)

toggle_btn = ttk.Button(btn_frame, text="Draw: ON", command=toggle_draw)
toggle_btn.grid(row=0, column=1, padx=10)

# Start the webcam
cap = cv2.VideoCapture(0)

# Start the loop
update_frame()
root.mainloop()

# Release camera when app closes
cap.release()
cv2.destroyAllWindows()
