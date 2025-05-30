# Importing required libraries
import cv2
import numpy as np
import tkinter as tk
from tkinter import ttk
from tkinter import messagebox
from PIL import Image, ImageTk
import datetime
import os

# HSV range for blue color detection
LOWER_COLOR = np.array([100, 150, 70])
UPPER_COLOR = np.array([140, 255, 255])

canvas_points = []
drawing = True
current_color = (255, 0, 0)  # Blue in BGR
brush_thickness = 5

# Create a directory to save doodles
os.makedirs("saved_doodles", exist_ok=True)

# Clear canvas
def clear_canvas():
    global canvas_points
    canvas_points = []

# Toggle drawing mode
def toggle_draw():
    global drawing
    drawing = not drawing
    toggle_btn.config(text="🖊️ Draw: ON" if drawing else "🛑 Draw: OFF")

# Change brush color
def set_color(color_name):
    global current_color
    colors = {
        "Blue": (255, 0, 0),
        "Green": (0, 255, 0),
        "Red": (0, 0, 255),
        "Yellow": (0, 255, 255),
        "White": (255, 255, 255)
    }
    current_color = colors[color_name]

# Save doodle as image
def save_doodle(frame):
    filename = datetime.datetime.now().strftime("saved_doodles/doodle_%Y%m%d_%H%M%S.png")
    cv2.imwrite(filename, frame)
    messagebox.showinfo("Saved", f"Doodle saved as:\n{filename}")

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
        cv2.line(frame, canvas_points[i - 1], canvas_points[i], current_color, brush_slider.get())

    img = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(img)
    imgtk = ImageTk.PhotoImage(image=img)

    video_label.imgtk = imgtk
    video_label.configure(image=imgtk)
    video_label.after(10, update_frame)

# GUI setup
root = tk.Tk()
root.title("🎨 AI-Powered Doodle Cam")
root.geometry("900x700")
root.configure(bg="#202020")

title = tk.Label(root, text="🎨 AI Doodle Cam", font=("Helvetica", 22, "bold"), fg="cyan", bg="#202020")
title.pack(pady=10)

video_label = tk.Label(root)
video_label.pack(pady=10)

control_frame = tk.Frame(root, bg="#202020")
control_frame.pack(pady=5)

clear_btn = ttk.Button(control_frame, text="🧹 Clear", command=clear_canvas)
clear_btn.grid(row=0, column=0, padx=5)

toggle_btn = ttk.Button(control_frame, text="🖊️ Draw: ON", command=toggle_draw)
toggle_btn.grid(row=0, column=1, padx=5)

save_btn = ttk.Button(control_frame, text="📸 Save", command=lambda: save_doodle(cv2.flip(cap.read()[1], 1)))
save_btn.grid(row=0, column=2, padx=5)

brush_slider = tk.Scale(control_frame, from_=1, to=20, orient='horizontal', label="Brush Size", bg="#202020", fg="white")
brush_slider.set(5)
brush_slider.grid(row=0, column=3, padx=10)

# Color palette
palette = tk.Frame(root, bg="#202020")
palette.pack(pady=10)

tk.Label(palette, text="🎨 Colors:", fg="white", bg="#202020", font=("Arial", 12)).pack(side="left", padx=5)

colors = ["Blue", "Green", "Red", "Yellow", "White"]
for color in colors:
    btn = ttk.Button(palette, text=color, command=lambda c=color: set_color(c))
    btn.pack(side="left", padx=5)

# Start video capture
cap = cv2.VideoCapture(0)

update_frame()
root.mainloop()

cap.release()
cv2.destroyAllWindows()

