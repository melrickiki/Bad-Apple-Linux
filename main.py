import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import sys
import time
import os
from screeninfo import get_monitors
import subprocess

import subprocess
import os

def resource_path(relative_path):
    """ Get absolute path to resource, works for dev and for PyInstaller """
    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

def find_largest_rect(grid):
    # Returns (x, y, w, h) of the largest rectangle of 1s in the 2D array `grid`
    # or None if no 1s.
    rows, cols = grid.shape
    max_area = 0
    best_rect = None
    
    heights = np.zeros(cols, dtype=int)
    for i in range(rows):
        heights = np.where(grid[i] == 1, heights + 1, 0)
        
        # Largest rectangle in histogram algorithm
        stack = []
        for j in range(cols + 1):
            h = heights[j] if j < cols else 0
            start = j
            while stack and stack[-1][1] > h:
                pos, height = stack.pop()
                area = height * (j - pos)
                if area > max_area:
                    max_area = area
                    best_rect = (pos, i - height + 1, j - pos, height)
                start = pos
            stack.append((start, h))
            
    return best_rect

def get_rectangles(grid):
    rects = []
    # Make a copy since we will mutate it
    work_grid = grid.copy()
    while True:
        rect = find_largest_rect(work_grid)
        if not rect:
            break
        x, y, w, h = rect
        rects.append(rect)
        # zero out the rectangle
        work_grid[y:y+h, x:x+w] = 0
    return rects

class BadAppleWindows:
    def __init__(self, video_path, borderless=False, grid_w=64, grid_h=48):
        self.video_path = video_path
        self.borderless = borderless
        self.cap = cv2.VideoCapture(video_path)
        if not self.cap.isOpened():
            print(f"Error: Could not open video {video_path}")
            sys.exit(1)
            
        self.grid_w = grid_w
        self.grid_h = grid_h
        
        # Get screen width and height using a temporary Tk instance and screeninfo
        self.root = tk.Tk()
        self.root.withdraw()
        
        # Load icon
        self.icon_img = None
        icon_path = resource_path("icon.png")
        if os.path.exists(icon_path):
            try:
                self.icon_img = tk.PhotoImage(file=icon_path)
            except Exception:
                pass
        
        try:
            monitors = get_monitors()
            pm = next((m for m in monitors if m.is_primary), monitors[0])
            self.offset_x = pm.x
            self.offset_y = pm.y
            self.screen_w = pm.width
            self.screen_h = pm.height
        except Exception as e:
            print("Could not get screen info, falling back to tkinter")
            self.offset_x = 0
            self.offset_y = 0
            self.screen_w = self.root.winfo_screenwidth()
            self.screen_h = self.root.winfo_screenheight()
        
        self.block_w = self.screen_w // self.grid_w
        self.block_h = self.screen_h // self.grid_h
        
        self.windows = []
        self.fps = self.cap.get(cv2.CAP_PROP_FPS)
        if not self.fps or self.fps < 1:
            self.fps = 30.0
            
        self.frame_time = 1.0 / self.fps
        
        # Bind keys to exit
        self.root.bind("<Escape>", lambda e: self.stop())
        self.root.bind("q", lambda e: self.stop())
        
    def stop(self):
        self.running = False
        
    def _create_window(self):
        win = tk.Toplevel(self.root)
        win.title("Bad Apple")
        if self.icon_img:
            win.iconphoto(True, self.icon_img)
        if self.borderless:
            win.overrideredirect(True)
        win.attributes('-topmost', True)
        win.configure(bg='white')
        win.geometry("0x0+0+0")
        return win
        
    def update_windows(self, rects):
        # We need as many windows as there are rects
        while len(self.windows) < len(rects):
            self.windows.append(self._create_window())
            
        # Hide extra windows
        for i in range(len(rects), len(self.windows)):
            self.windows[i].geometry("0x0+-100+-100")
            
        # Update positions
        for i, (x, y, w, h) in enumerate(rects):
            screen_x = self.offset_x + x * self.block_w
            screen_y = self.offset_y + y * self.block_h
            screen_w = w * self.block_w
            screen_h = h * self.block_h
            self.windows[i].geometry(f"{screen_w}x{screen_h}+{screen_x}+{screen_y}")
            
    def play(self):
        audio_proc = None
        try:
            audio_proc = subprocess.Popen(
                ['ffplay', '-nodisp', '-autoexit', '-loglevel', 'quiet', self.video_path],
                stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )
        except FileNotFoundError:
            try:
                audio_proc = subprocess.Popen(
                    ['mpv', '--no-video', self.video_path],
                    stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
                )
            except FileNotFoundError:
                print("Warning: Neither ffplay nor mpv found. Playing without audio.")

        try:
            self.running = True
            start_time = time.time()
            frame_idx = 0
            while self.running:
                ret, frame = self.cap.read()
                if not ret:
                    break
                
                frame_idx += 1
                expected_time = frame_idx * self.frame_time
                current_time = time.time() - start_time
                
                # Skip frame if we are lagging behind by more than 1 frame
                if current_time > expected_time + self.frame_time:
                    continue
                    
                # Convert to grayscale and resize
                gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
                resized = cv2.resize(gray, (self.grid_w, self.grid_h), interpolation=cv2.INTER_AREA)
                
                # Threshold
                _, thresh = cv2.threshold(resized, 128, 1, cv2.THRESH_BINARY)
                
                # Get rects
                rects = get_rectangles(thresh)
                
                # Update UI
                self.update_windows(rects)
                self.root.update()
                
                # Sleep to maintain fps exactly to the expected timeline
                current_time = time.time() - start_time
                sleep_time = expected_time - current_time
                if sleep_time > 0:
                    time.sleep(sleep_time)
        except KeyboardInterrupt:
            print("Stopped.")
        finally:
            self.cap.release()
            self.root.destroy()
            if audio_proc:
                try:
                    audio_proc.terminate()
                except Exception:
                    pass

def run_setup():
    setup_root = tk.Tk()
    setup_root.title("Bad Apple Setup")
    
    # Load icon
    icon_path = resource_path("icon.png")
    if os.path.exists(icon_path):
        try:
            img = tk.PhotoImage(file=icon_path)
            setup_root.iconphoto(True, img)
        except Exception:
            pass
            
    setup_root.geometry("600x480")
    setup_root.configure(bg="#242424")
    
    # Custom colors
    BG_COLOR = "#242424"
    TEXT_COLOR = "#ffffff"
    BUTTON_BG = "#3e3e3e"
    SELECTION_BG = "#3584e4"
    
    borderless_var = tk.BooleanVar(value=False)
    resolution_var = tk.StringVar(value="64x48")
    result = {"start": False}

    # Header
    tk.Label(setup_root, text="Bad Apple", font=("Cantarell", 22, "bold"), 
             bg=BG_COLOR, fg=TEXT_COLOR).pack(pady=30)
    
    # Choice Frame
    choice_frame = tk.Frame(setup_root, bg=BG_COLOR)
    choice_frame.pack(fill="both", expand=True, padx=40)
    
    tk.Label(choice_frame, text="Resolution Choice", font=("Cantarell", 10, "bold"), 
             bg=BG_COLOR, fg="#888888").pack(anchor="w", pady=(0, 5))
    
    # Listbox for resolutions
    lb = tk.Listbox(choice_frame, bg="#1e1e1e", fg=TEXT_COLOR, 
                    selectbackground=SELECTION_BG, borderwidth=0, 
                    highlightthickness=0, font=("Cantarell", 11),
                    activestyle="none")
    lb.pack(fill="both", expand=True)
    
    resolutions = ["32x24", "48x36", "64x48", "80x60", "120x90"]
    for res in resolutions:
        lb.insert(tk.END, f"  Launch in {res}")
    
    lb.selection_set(2) # Default to 64x48
    
    # Borderless Checkbutton
    cb = tk.Checkbutton(choice_frame, text="Enable Borderless Mode", variable=borderless_var,
                        bg=BG_COLOR, fg=TEXT_COLOR, selectcolor="#1e1e1e", 
                        activebackground=BG_COLOR, activeforeground=TEXT_COLOR,
                        font=("Cantarell", 10))
    cb.pack(anchor="w", pady=15)
    
    def on_cancel():
        setup_root.destroy()
        
    def on_ok():
        sel = lb.curselection()
        if sel:
            res_str = resolutions[sel[0]]
            resolution_var.set(res_str)
            result["start"] = True
            setup_root.destroy()

    # Button Frame
    btn_frame = tk.Frame(setup_root, bg=BG_COLOR)
    btn_frame.pack(fill="x", side="bottom", pady=20, padx=40)
    
    cancel_btn = tk.Button(btn_frame, text="Cancel", command=on_cancel, 
                           bg=BUTTON_BG, fg=TEXT_COLOR, relief="flat", 
                           font=("Cantarell", 11, "bold"), width=15, height=2)
    cancel_btn.pack(side="left", expand=True, padx=10)
    
    ok_btn = tk.Button(btn_frame, text="OK", command=on_ok, 
                       bg=BUTTON_BG, fg=TEXT_COLOR, relief="flat", 
                       font=("Cantarell", 11, "bold"), width=15, height=2)
    ok_btn.pack(side="right", expand=True, padx=10)

    setup_root.mainloop()
    
    if not result["start"]:
        return None, False, 0, 0
        
    res_str = resolution_var.get()
    gw, gh = map(int, res_str.split('x'))
    
    # Video path is internal
    video_path = resource_path("bad_apple.mp4")
    return video_path, borderless_var.get(), gw, gh

if __name__ == "__main__":
    if len(sys.argv) >= 2 and not sys.argv[1].endswith('.py') and not sys.argv[1].endswith('.exe'):
        video_path = sys.argv[1]
        borderless = False
        gw, gh = 64, 48
        if len(sys.argv) >= 4:
            gw = int(sys.argv[2])
            gh = int(sys.argv[3])
    else:
        video_path, borderless, gw, gh = run_setup()
        
    if video_path:
        app = BadAppleWindows(video_path, borderless=borderless, grid_w=gw, grid_h=gh)
        app.play()
