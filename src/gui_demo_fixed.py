import tkinter as tk
from tkinter import ttk
import numpy as np
from PIL import Image, ImageTk
import cv2
import time

class StandaloneGui:
    def __init__(self, root):
        self.root = root
        self.root.title("Control System GUI")
        
        # Set window size and make it non-resizable
        self.root.geometry("1200x800")
        self.root.resizable(False, False)
        
        # Initialize state
        self.current_state = "OFF"
        self.button_styles = {
            "OFF": {"bg": "#ff6b6b", "activebackground": "#ff5252"},
            "STANDBY": {"bg": "#4dabf7", "activebackground": "#339af0"},
            "CALIBRATE": {"bg": "#ffd43b", "activebackground": "#fcc419"},
            "READY": {"bg": "#69db7c", "activebackground": "#51cf66"},
            "ACTIVE": {"bg": "#9775fa", "activebackground": "#845ef7"}
        }
        
        # Create main container
        self.main_container = ttk.Frame(root)
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Create camera feeds frame with fixed height
        self.camera_frame = ttk.Frame(self.main_container)
        self.camera_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create camera feed labels with fixed size
        self.camera_labels = []
        for i in range(2):
            frame = ttk.Frame(self.camera_frame, height=200)  # Fixed height
            frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=5)
            frame.pack_propagate(False)  # Prevent frame from shrinking
            
            label = ttk.Label(frame)
            label.pack(fill=tk.BOTH, expand=True)
            self.camera_labels.append(label)
        
        # Create visualization frame with fixed height
        self.vis_frame = ttk.Frame(self.main_container)
        self.vis_frame.pack(fill=tk.X, pady=(0, 10))
        
        # Create trajectory visualization canvas with fixed height
        self.trajectory_canvas = tk.Canvas(
            self.vis_frame,
            width=400,
            height=150,  # Reduced height
            bg='black'
        )
        self.trajectory_canvas.pack(fill=tk.X, expand=True)
        
        # Create control panel underneath trajectory
        self.control_panel = ttk.Frame(self.vis_frame)
        self.control_panel.pack(fill=tk.X, pady=(10, 0))
        
        # Create buttons
        self.buttons = {}
        button_texts = ["OFF", "STANDBY", "CALIBRATE", "READY", "ACTIVE"]
        for text in button_texts:
            btn = tk.Button(
                self.control_panel,
                text=text,
                font=("Arial", 12, "bold"),
                width=15,
                height=2,
                command=lambda t=text: self.handle_button_click(t)
            )
            btn.pack(side=tk.LEFT, padx=5)
            self.buttons[text] = btn
        
        # Create log panel with scrollbar
        self.log_frame = ttk.Frame(self.main_container)
        self.log_frame.pack(fill=tk.BOTH, expand=True)
        
        # Add scrollbar
        scrollbar = ttk.Scrollbar(self.log_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.log_text = tk.Text(
            self.log_frame,
            height=8,  # Reduced height
            font=("Courier", 10),
            bg="#2d3436",
            fg="#dfe6e9",
            wrap=tk.WORD,
            yscrollcommand=scrollbar.set
        )
        self.log_text.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)
        
        # Initialize mock camera data
        self.mock_frame = np.zeros((480, 640, 3), dtype=np.uint8)
        self.mock_mask = np.zeros((480, 640), dtype=np.uint8)
        
        # Initialize trajectory data
        self.trajectory_points = []
        
        # Start update loops
        self.update_cameras()
        self.update_trajectory()
        
        # Add initial log
        self.add_log("System initialized")
    
    def update_cameras(self):
        # Generate mock camera frames
        # Raw camera feed
        self.mock_frame = np.random.randint(0, 255, (480, 640, 3), dtype=np.uint8)
        cv2.putText(
            self.mock_frame,
            "Mock Camera Feed",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )
        
        # Processed mask
        self.mock_mask = np.random.randint(0, 255, (480, 640), dtype=np.uint8)
        cv2.putText(
            self.mock_mask,
            "Processed Mask",
            (50, 50),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )
        
        # Resize frames to fit the smaller display
        raw_frame = cv2.resize(self.mock_frame, (320, 180))
        mask_frame = cv2.resize(self.mock_mask, (320, 180))
        
        # Convert and display frames
        raw_frame = cv2.cvtColor(raw_frame, cv2.COLOR_BGR2RGB)
        raw_image = Image.fromarray(raw_frame)
        raw_photo = ImageTk.PhotoImage(image=raw_image)
        self.camera_labels[0].configure(image=raw_photo)
        self.camera_labels[0].image = raw_photo
        
        mask_frame = cv2.cvtColor(mask_frame, cv2.COLOR_GRAY2RGB)
        mask_image = Image.fromarray(mask_frame)
        mask_photo = ImageTk.PhotoImage(image=mask_image)
        self.camera_labels[1].configure(image=mask_photo)
        self.camera_labels[1].image = mask_photo
        
        # Schedule next update
        self.root.after(100, self.update_cameras)
    
    def update_trajectory(self):
        self.trajectory_canvas.delete("all")
        
        # Draw grid
        width = self.trajectory_canvas.winfo_width()
        height = self.trajectory_canvas.winfo_height()
        
        # Draw horizontal lines
        for i in range(0, height, 20):
            self.trajectory_canvas.create_line(0, i, width, i, fill='#333333')
        
        # Draw vertical lines
        for i in range(0, width, 20):
            self.trajectory_canvas.create_line(i, 0, i, height, fill='#333333')
        
        # Generate mock trajectory point
        if len(self.trajectory_points) < 10:
            x = width // 2 + int(50 * np.sin(time.time()))
            y = height // 2 + int(50 * np.cos(time.time()))
            self.trajectory_points.append((x, y))
        
        # Draw trajectory points
        for i in range(len(self.trajectory_points) - 1):
            x1, y1 = self.trajectory_points[i]
            x2, y2 = self.trajectory_points[i + 1]
            self.trajectory_canvas.create_line(x1, y1, x2, y2, fill='#4ecdc4', width=2)
        
        # Keep only last 10 points
        if len(self.trajectory_points) > 10:
            self.trajectory_points.pop(0)
        
        # Schedule next update
        self.root.after(50, self.update_trajectory)
    
    def handle_button_click(self, state):
        if state == self.current_state:
            return
        
        self.current_state = state
        self.add_log(f"State changed to {state}")
        
        # Update button colors
        for btn_text, btn in self.buttons.items():
            if btn_text == state:
                btn.configure(**self.button_styles[btn_text])
            else:
                btn.configure(bg="#e9ecef", activebackground="#dee2e6")
    
    def add_log(self, message):
        timestamp = time.strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {message}\n"
        self.log_text.insert(tk.END, log_entry)
        self.log_text.see(tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = StandaloneGui(root)
    root.mainloop() 