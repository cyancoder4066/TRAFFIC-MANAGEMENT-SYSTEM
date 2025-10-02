import cv2
import numpy as np
import os
import tkinter as tk
from PIL import Image, ImageTk

# YOLO setup
net = cv2.dnn.readNet("yolov7.weights", "yolov7.cfg")
with open("coco.names", "r") as f:
    classes = f.read().strip().split("\n")
vehicle_classes = ['car', 'bus', 'truck']

# Image directories
image_dir = "test_images"
output_dir = "output_images"
os.makedirs(output_dir, exist_ok=True)
image_files = [f for f in os.listdir(image_dir) if f.endswith(".jpg")]
current_index = 0

# Tkinter window
root = tk.Tk()
root.title("Vehicle Detection Viewer")

# Buttons frame (above the image)
btn_frame = tk.Frame(root)
btn_frame.pack(pady=10)
tk.Button(btn_frame, text="Next", command=lambda: next_image(), width=10).pack(side=tk.LEFT, padx=5)
tk.Button(btn_frame, text="Close", command=lambda: close_window(), width=10).pack(side=tk.LEFT, padx=5)

# Image display label
label = tk.Label(root)
label.pack()

# Image processing function
def process_image(image_path):
    image = cv2.imread(image_path)
    height, width, _ = image.shape
    blob = cv2.dnn.blobFromImage(image, 0.00392, (416,416), (0,0,0), True, crop=False)
    net.setInput(blob)
    output_layers = net.getUnconnectedOutLayersNames()
    detections = net.forward(output_layers)

    for out in detections:
        for obj in out:
            scores = obj[5:]
            class_id = np.argmax(scores)
            confidence = scores[class_id]
            if confidence > 0.5:
                label_text = classes[class_id]
                if label_text in vehicle_classes:
                    cx = int(obj[0]*width)
                    cy = int(obj[1]*height)
                    w = int(obj[2]*width)
                    h = int(obj[3]*height)
                    x = int(cx - w/2)
                    y = int(cy - h/2)
                    cv2.rectangle(image, (x,y), (x+w, y+h), (0,255,0), 2)
                    cv2.putText(image, label_text, (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0,0,0),2)
    return cv2.cvtColor(image, cv2.COLOR_BGR2RGB)

# Show current image
def show_image():
    global current_index
    img_path = os.path.join(image_dir, image_files[current_index])
    processed_img = process_image(img_path)
    img_pil = Image.fromarray(processed_img)
    img_tk = ImageTk.PhotoImage(img_pil)
    label.imgtk = img_tk
    label.configure(image=img_tk)

# Button actions
def next_image():
    global current_index
    if current_index < len(image_files)-1:
        current_index += 1
        show_image()

def close_window():
    root.destroy()

# Show first image
show_image()
root.mainloop()
