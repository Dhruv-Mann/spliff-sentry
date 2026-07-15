import tkinter as tk
import time
import threading
import os
import sys
import subprocess
from datetime import datetime
from PIL import Image, ImageTk

class TokyoFocusAgent:
    def __init__(self):
        # Enable Windows DPI awareness to ensure precise screen coordinate math
        try:
            from ctypes import windll
            windll.shcore.SetProcessDpiAwareness(1)
        except Exception:
            pass

        # Prevent multiple instances of the application from running
        import socket
        from tkinter import messagebox
        try:
            self.lock_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.lock_socket.bind(('127.0.0.1', 54321))
        except socket.error:
            # Another copy is already running. Warn the user and exit cleanly.
            temp_root = tk.Tk()
            temp_root.withdraw()
            messagebox.showinfo("Tokyo Focus", "Tokyo Focus is already running in the background.\nCheck your system tray to configure or quit.")
            temp_root.destroy()
            sys.exit()

        self.root = tk.Tk()
        self.root.title("Tokyo Focus Setup")
        self.root.config(bg="#121212")
        
        # Locate image in the execution directory
        if getattr(sys, 'frozen', False):
            # If compiled as .exe via PyInstaller
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(__file__)
            
        self.asset_path = os.path.join(base_path, "tokyospliff.png")
        
        # Load asset if available, resized to fit the larger popup window layout
        self.display_img = self._fit_image(400, 260)
        self.character_window = None
        self.total_seconds = 1800 # Default to 30 mins
        
        # Session tracking
        self.session_count = 0
        self.completed_sessions = 0
        self.is_paused = False
        self.is_running = False
        self.timer_thread = None
        self.remaining_seconds = 0
        self.status_window = None
        self.session_start_time = None
        
        # Setup Desktop integrations
        self.create_desktop_shortcut()
        self.setup_system_tray()
        
        # Build custom styled startup setup window inside self.root
        self.build_setup_ui()
        self.root.mainloop()

    def create_desktop_shortcut(self):
        # Determine the directory where the .exe / main.py is running
        if getattr(sys, 'frozen', False):
            exe_dir = os.path.dirname(sys.executable)
            exe_path = sys.executable
        else:
            exe_dir = os.path.dirname(os.path.abspath(__file__))
            exe_path = os.path.abspath(__file__)
            
        icon_path = os.path.join(exe_dir, "tokyospliff.ico")
        
        # 1. Convert PNG to ICO dynamically if it doesn't exist in the exe directory
        if not os.path.exists(icon_path) and os.path.exists(self.asset_path):
            try:
                img = Image.open(self.asset_path)
                # Convert and save as ICO with standard sizes
                img.save(icon_path, format="ICO", sizes=[(256, 256), (128, 128), (64, 64), (32, 32), (16, 16)])
            except Exception as e:
                print(f"Error creating ico file: {e}")
                
        # 2. Create/update the shortcut on Desktop
        try:
            desktop = os.path.join(os.environ["USERPROFILE"], "Desktop")
            shortcut_path = os.path.join(desktop, "Tokyo Focus.lnk")
            
            # Build PowerShell command to create shortcut
            if exe_path.endswith(".py"):
                # For python script, TargetPath must be pythonw.exe to run without console window
                target = sys.executable.replace("python.exe", "pythonw.exe")
                args = f'"{exe_path}"'
                ps_cmd = (
                    f'$s = (New-Object -ComObject WScript.Shell).CreateShortcut("{shortcut_path}"); '
                    f'$s.TargetPath = "{target}"; '
                    f'$s.Arguments = \'{args}\'; '
                    f'$s.IconLocation = "{icon_path}"; '
                    f'$s.Save()'
                )
            else:
                # For compiled exe, TargetPath is simply the exe path
                ps_cmd = (
                    f'$s = (New-Object -ComObject WScript.Shell).CreateShortcut("{shortcut_path}"); '
                    f'$s.TargetPath = "{exe_path}"; '
                    f'$s.Arguments = ""; '
                    f'$s.IconLocation = "{icon_path}"; '
                    f'$s.Save()'
                )
            # Run PowerShell silently without flashing a command prompt window on Windows
            creation_flags = 0
            if sys.platform == "win32":
                creation_flags = subprocess.CREATE_NO_WINDOW

            subprocess.run(
                ["powershell", "-Command", ps_cmd],
                capture_output=True,
                check=True,
                creationflags=creation_flags
            )
        except Exception as e:
            print(f"Error creating desktop shortcut: {e}")

    def setup_system_tray(self):
        try:
            import pystray
            # Use Pillow to open and scale image for system tray
            if os.path.exists(self.asset_path):
                tray_img = Image.open(self.asset_path)
            else:
                # Fallback blank image if asset doesn't exist
                tray_img = Image.new("RGBA", (64, 64), (18, 18, 18, 255))
            
            # Tray icon standard size is 64x64 or 16x16. Thumbnailing to 64x64 works nicely.
            tray_img.thumbnail((64, 64), Image.Resampling.LANCZOS)
            
            # Define menu actions
            def show_status(icon, item):
                self.root.after(0, self.toggle_status_window)
                
            def pause_resume(icon, item):
                self.root.after(0, self.toggle_pause)
                
            def quit_action(icon, item):
                icon.stop()
                self.root.after(0, self.quit_app)

            menu = pystray.Menu(
                pystray.MenuItem("Show Status", show_status),
                pystray.MenuItem("Pause/Resume", pause_resume),
                pystray.Menu.SEPARATOR,
                pystray.MenuItem("Quit", quit_action)
            )
            self.tray_icon = pystray.Icon("tokyo_focus", tray_img, "Tokyo Focus", menu)
            
            # Run in a separate thread so it doesn't block Tkinter loop
            threading.Thread(target=self.tray_icon.run, daemon=True).start()
        except Exception as e:
            print(f"Error setting up system tray: {e}")

    def _fit_image(self, max_width, max_height):
        if not os.path.exists(self.asset_path):
            return None
        try:
            # Use Pillow to load and scale the image smoothly with aspect ratio matching
            pil_image = Image.open(self.asset_path)
            pil_image.thumbnail((max_width, max_height), Image.Resampling.LANCZOS)
            return ImageTk.PhotoImage(pil_image)
        except Exception as e:
            print(f"Error loading image: {e}")
            return None

    def build_setup_ui(self):
        # Center the setup window on the screen
        self.screen_width = self.root.winfo_screenwidth()
        self.screen_height = self.root.winfo_screenheight()
        setup_w, setup_h = 450, 280
        x = (self.screen_width - setup_w) // 2
        y = (self.screen_height - setup_h) // 2
        self.root.geometry(f"{setup_w}x{setup_h}+{x}+{y}")
        self.root.resizable(False, False)
        
        # Styled elements matching the opaque dark-theme card layout
        title_lbl = tk.Label(self.root, text="TOKYO FOCUS TIMER SETUP", fg="#00FF00", bg="#121212", font=("Consolas", 14, "bold"))
        title_lbl.pack(pady=(25, 15))
        
        entry_frame = tk.Frame(self.root, bg="#121212")
        entry_frame.pack(pady=10)
        
        # Hours Entry
        h_frame = tk.Frame(entry_frame, bg="#121212")
        h_frame.pack(side="left", padx=15)
        h_lbl = tk.Label(h_frame, text="HOURS", fg="#FFFFFF", bg="#121212", font=("Consolas", 9, "bold"))
        h_lbl.pack(pady=(0, 5))
        self.h_entry = tk.Entry(h_frame, width=4, bg="#1e1e1e", fg="#FFFFFF", insertbackground="#FFFFFF",
                                font=("Consolas", 14, "bold"), justify="center", bd=1, relief="solid", highlightcolor="#333333", highlightthickness=1)
        self.h_entry.insert(0, "0")
        self.h_entry.pack()
        
        # Minutes Entry
        m_frame = tk.Frame(entry_frame, bg="#121212")
        m_frame.pack(side="left", padx=15)
        m_lbl = tk.Label(m_frame, text="MINUTES", fg="#FFFFFF", bg="#121212", font=("Consolas", 9, "bold"))
        m_lbl.pack(pady=(0, 5))
        self.m_entry = tk.Entry(m_frame, width=4, bg="#1e1e1e", fg="#FFFFFF", insertbackground="#FFFFFF",
                                font=("Consolas", 14, "bold"), justify="center", bd=1, relief="solid", highlightcolor="#333333", highlightthickness=1)
        self.m_entry.insert(0, "30")
        self.m_entry.pack()
        
        # Seconds Entry
        s_frame = tk.Frame(entry_frame, bg="#121212")
        s_frame.pack(side="left", padx=15)
        s_lbl = tk.Label(s_frame, text="SECONDS", fg="#FFFFFF", bg="#121212", font=("Consolas", 9, "bold"))
        s_lbl.pack(pady=(0, 5))
        self.s_entry = tk.Entry(s_frame, width=4, bg="#1e1e1e", fg="#FFFFFF", insertbackground="#FFFFFF",
                                font=("Consolas", 14, "bold"), justify="center", bd=1, relief="solid", highlightcolor="#333333", highlightthickness=1)
        self.s_entry.insert(0, "0")
        self.s_entry.pack()
        
        # Action buttons
        btn_frame = tk.Frame(self.root, bg="#121212")
        btn_frame.pack(pady=(20, 0))
        
        self.start_btn = tk.Button(btn_frame, text="[ Start Focus ]", fg="#00FF00", bg="#1e1e1e", activebackground="#00FF00", activeforeground="black",
                                   font=("Consolas", 11, "bold"), command=self.on_start_focus, highlightthickness=0, bd=1, width=15)
        self.start_btn.pack(side="left", padx=10)
        self._setup_btn_hover(self.start_btn, "#1e1e1e", "#00FF00", "#00FF00", "black")
        
        self.cancel_btn = tk.Button(btn_frame, text="[ Cancel ]", fg="#FF3333", bg="#1e1e1e", activebackground="#FF3333", activeforeground="black",
                                    font=("Consolas", 11, "bold"), command=sys.exit, highlightthickness=0, bd=1, width=15)
        self.cancel_btn.pack(side="right", padx=10)
        self._setup_btn_hover(self.cancel_btn, "#1e1e1e", "#FF3333", "#FF3333", "black")
        
        # Bind focus auto-fill behaviors
        self._setup_entry_focus(self.h_entry)
        self._setup_entry_focus(self.m_entry)
        self._setup_entry_focus(self.s_entry)
        
        # Handle X button window close cleanly
        self.root.protocol("WM_DELETE_WINDOW", sys.exit)

    def on_start_focus(self):
        try:
            h = int(self.h_entry.get().strip() or 0)
            m = int(self.m_entry.get().strip() or 0)
            s = int(self.s_entry.get().strip() or 0)
        except ValueError:
            h, m, s = 0, 30, 0
            
        self.total_seconds = h * 3600 + m * 60 + s
        if self.total_seconds <= 0:
            self.total_seconds = 1800 # Fallback default to 30 mins
            
        # Hide root setup window
        self.root.withdraw()
        
        # Start new session
        self.session_count += 1
        self.session_start_time = datetime.now()
        self.start_countdown()

    def start_countdown(self):
        self.remaining_seconds = self.total_seconds
        self.is_running = True
        self.is_paused = False
        self.timer_thread = threading.Thread(target=self.countdown_worker, daemon=True)
        self.timer_thread.start()

    def countdown_worker(self):
        while self.remaining_seconds > 0 and self.is_running:
            if not self.is_paused:
                time.sleep(1)
                self.remaining_seconds -= 1
                # Update status window if open
                if self.status_window and self.status_window.winfo_exists():
                    self.root.after(0, self.update_status_display)
            else:
                time.sleep(0.1)  # Check pause state frequently
        
        if self.is_running and self.remaining_seconds <= 0:
            # Push execution back to main UI thread safely
            self.root.after(0, self.summon_character)

    def summon_character(self):
        self.character_window = tk.Toplevel(self.root)
        self.character_window.overrideredirect(True) # Borderless frame
        self.character_window.attributes("-topmost", True) # Force front-focus
        self.character_window.config(bg="#121212") # Sleek solid dark background
        
        self.screen_width = self.character_window.winfo_screenwidth()
        self.screen_height = self.character_window.winfo_screenheight()
        
        # Fixed canvas boundary box (Enlarged)
        self.window_w = 520
        self.window_h = 460
        
        # Start coordinate: completely off-screen to the right
        self.current_x = self.screen_width
        self.target_x = max(self.screen_width - self.window_w - 20, 0)
        
        # Bottom-right positioning, leaving 60px margin for the taskbar
        self.y_pos = max(self.screen_height - self.window_h - 60, 0)
        
        self.character_window.geometry(f"{self.window_w}x{self.window_h}+{self.current_x}+{self.y_pos}")
        
        # Use solid background matching the theme (completely opaque)
        self.canvas = tk.Canvas(self.character_window, width=self.window_w, height=self.window_h, bg="#121212", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        if self.display_img:
            # Center the image horizontally in the upper region of the canvas
            self.canvas.create_image(self.window_w//2, 145, image=self.display_img)
        else:
            # Safe runtime fallback vector box if image is missing
            self.canvas.create_rectangle(120, 40, 400, 240, fill="#333333", outline="#00FF00")
            self.canvas.create_text(260, 140, text="[TokyoSpliff PNG\nMissing]", fill="#00FF00", justify="center")
            
        self.slide_in()

    def slide_in(self):
        # Medium-speed linear translation script
        if self.current_x > self.target_x:
            self.current_x -= 20 # Step interval rate
            self.character_window.geometry(f"{self.window_w}x{self.window_h}+{self.current_x}+{self.y_pos}")
            self.character_window.after(10, self.slide_in) # ~60hz redraw rate
        else:
            self.show_dialogue_ui()

    def show_dialogue_ui(self):
        self.is_running = False  # Stop the timer
        
        ui_frame = tk.Frame(self.character_window, bg="#121212", bd=2, relief="solid", highlightbackground="#333333")
        ui_frame.place(relx=0.5, rely=0.82, anchor="center", width=480, height=180)
        
        # Session info
        session_duration = self.format_time(self.total_seconds)
        info_text = f"Session #{self.session_count} complete!\nDuration: {session_duration} | Completed today: {self.completed_sessions}"
        info_lbl = tk.Label(ui_frame, text=info_text, fg="#888888", bg="#121212", 
                           font=("Consolas", 8), justify="center")
        info_lbl.pack(side="top", pady=(8, 2))
        
        # Upgraded Dialogue Text
        msg = tk.Label(ui_frame, text="Yo, check the clock. Are we locked in,\nor are we just wasting generational time?", 
                       fg="#FFFFFF", bg="#121212", font=("Consolas", 10, "bold"), justify="center")
        msg.pack(side="top", pady=(4, 8))
        
        btn_frame = tk.Frame(ui_frame, bg="#121212")
        btn_frame.pack(side="top", fill="x", padx=15, pady=(4, 4))
        
        # Action buttons
        btn1 = tk.Button(btn_frame, text="[ Cookin' Cuh - Continue ]", fg="#00FF00", bg="#1e1e1e", activebackground="#00FF00", activeforeground="black",
                          font=("Consolas", 9, "bold"), command=self.continue_session, highlightthickness=0, bd=1)
        btn1.pack(side="left", expand=True, fill="x", padx=5)
        self._setup_btn_hover(btn1, "#1e1e1e", "#00FF00", "#00FF00", "black")
        
        btn2 = tk.Button(btn_frame, text="[ Done for Now ]", fg="#FFA500", bg="#1e1e1e", activebackground="#FFA500", activeforeground="black",
                          font=("Consolas", 9, "bold"), command=self.pause_session, highlightthickness=0, bd=1)
        btn2.pack(side="right", expand=True, fill="x", padx=5)
        self._setup_btn_hover(btn2, "#1e1e1e", "#FFA500", "#FFA500", "black")

        btn_frame2 = tk.Frame(ui_frame, bg="#121212")
        btn_frame2.pack(side="top", fill="x", padx=15, pady=(4, 4))
        
        btn3 = tk.Button(btn_frame2, text="[ Caught Slacking... Reset ]", fg="#FF3333", bg="#1e1e1e", activebackground="#FF3333", activeforeground="black",
                          font=("Consolas", 8), command=self.reset_progress, highlightthickness=0, bd=1)
        btn3.pack(side="top", fill="x")
        self._setup_btn_hover(btn3, "#1e1e1e", "#FF3333", "#FF3333", "black")
        
        # Clear Exit button below to stop the application from the UI
        btn4 = tk.Button(ui_frame, text="[ Exit App ]", fg="#FFFFFF", bg="#2a2a2a", activebackground="#FFFFFF", activeforeground="black",
                         font=("Consolas", 9, "bold"), command=self.quit_app, highlightthickness=0, bd=1)
        btn4.pack(side="top", pady=(6, 6))
        self._setup_btn_hover(btn4, "#2a2a2a", "#FFFFFF", "#FFFFFF", "black")

    def _setup_btn_hover(self, btn, normal_bg, normal_fg, hover_bg, hover_fg):
        btn.config(cursor="hand2")
        btn.bind("<Enter>", lambda e: btn.config(bg=hover_bg, fg=hover_fg))
        btn.bind("<Leave>", lambda e: btn.config(bg=normal_bg, fg=normal_fg))

    def _setup_entry_focus(self, entry):
        entry.bind("<FocusIn>", lambda e: self._on_focus_in(entry))
        entry.bind("<FocusOut>", lambda e: self._on_focus_out(entry))

    def _on_focus_in(self, entry):
        val = entry.get().strip()
        if val in ("0", "00"):
            entry.delete(0, tk.END)

    def _on_focus_out(self, entry):
        val = entry.get().strip()
        if not val:
            entry.insert(0, "00")
        elif val.isdigit() and len(val) == 1:
            entry.delete(0, tk.END)
            entry.insert(0, f"0{val}")

    def quit_app(self):
        try:
            if hasattr(self, 'tray_icon') and self.tray_icon:
                self.tray_icon.stop()
        except Exception:
            pass

        if self.character_window:
            self.character_window.destroy()
            self.character_window = None
        self.root.quit()
        self.root.destroy()

    def continue_session(self):
        """Mark session as completed and start a new one"""
        self.completed_sessions += 1
        self.session_count += 1
        self.session_start_time = datetime.now()
        if self.character_window:
            self.character_window.destroy()
        self.start_countdown()

    def pause_session(self):
        """Pause and minimize to tray without starting new session"""
        if self.character_window:
            self.character_window.destroy()
        self.is_running = False

    def reset_progress(self):
        """Reset all progress and restart from session 1"""
        self.session_count = 0
        self.completed_sessions = 0
        if self.character_window:
            self.character_window.destroy()
        # Show setup window again
        self.root.deiconify()

    def toggle_pause(self):
        """Pause/Resume the current timer"""
        if self.is_running:
            self.is_paused = not self.is_paused
            if self.status_window and self.status_window.winfo_exists():
                self.update_status_display()

    def toggle_status_window(self):
        """Show or hide the status window"""
        if self.status_window and self.status_window.winfo_exists():
            self.status_window.destroy()
            self.status_window = None
        else:
            self.create_status_window()

    def create_status_window(self):
        """Create a floating status window showing current progress"""
        self.status_window = tk.Toplevel(self.root)
        self.status_window.title("Tokyo Focus Status")
        self.status_window.config(bg="#121212")
        self.status_window.attributes("-topmost", True)
        
        # Position in bottom-right with increased height for buttons
        sw, sh = 320, 240
        x = self.root.winfo_screenwidth() - sw - 20
        y = self.root.winfo_screenheight() - sh - 100
        self.status_window.geometry(f"{sw}x{sh}+{x}+{y}")
        
        # Title
        title = tk.Label(self.status_window, text="[ TOKYO FOCUS STATUS ]", 
                        fg="#00FF00", bg="#121212", font=("Consolas", 11, "bold"))
        title.pack(pady=(10, 5))
        
        # Status frame
        self.status_frame = tk.Frame(self.status_window, bg="#1e1e1e", bd=1, relief="solid")
        self.status_frame.pack(fill="both", expand=False, padx=10, pady=(5, 5))
        
        # Control buttons frame (created before update_status_display)
        btn_frame = tk.Frame(self.status_window, bg="#121212")
        btn_frame.pack(side="bottom", pady=(5, 10), padx=10)
        
        pause_btn = tk.Button(btn_frame, text="[ Pause/Resume ]", fg="#FFA500", bg="#1e1e1e",
                              font=("Consolas", 8, "bold"), command=self.toggle_pause, 
                              highlightthickness=0, bd=1, width=18)
        pause_btn.pack(side="left", padx=3)
        self._setup_btn_hover(pause_btn, "#1e1e1e", "#FFA500", "#FFA500", "black")
        
        close_btn = tk.Button(btn_frame, text="[ Close ]", fg="#FFFFFF", bg="#2a2a2a",
                              font=("Consolas", 8, "bold"), command=self.toggle_status_window,
                              highlightthickness=0, bd=1, width=12)
        close_btn.pack(side="left", padx=3)
        self._setup_btn_hover(close_btn, "#2a2a2a", "#FFFFFF", "#FFFFFF", "black")
        
        # Update status display after buttons are created
        self.update_status_display()
        
        # Force geometry update to ensure buttons are visible
        self.status_window.update()
        self.status_window.update_idletasks()

    def update_status_display(self):
        """Update the status window with current timer state"""
        if not self.status_frame or not self.status_frame.winfo_exists():
            return
            
        # Clear existing content
        for widget in self.status_frame.winfo_children():
            widget.destroy()
        
        if self.is_running:
            state_color = "#FFA500" if self.is_paused else "#00FF00"
            state_text = "PAUSED" if self.is_paused else "RUNNING"
            
            state_lbl = tk.Label(self.status_frame, text=f"Status: {state_text}", 
                                fg=state_color, bg="#1e1e1e", font=("Consolas", 9, "bold"))
            state_lbl.pack(pady=(10, 5))
            
            time_remaining = self.format_time(self.remaining_seconds)
            time_lbl = tk.Label(self.status_frame, text=f"Time Left: {time_remaining}", 
                               fg="#FFFFFF", bg="#1e1e1e", font=("Consolas", 12, "bold"))
            time_lbl.pack(pady=5)
            
            progress_pct = ((self.total_seconds - self.remaining_seconds) / self.total_seconds) * 100
            progress_lbl = tk.Label(self.status_frame, text=f"Progress: {progress_pct:.0f}%", 
                                   fg="#888888", bg="#1e1e1e", font=("Consolas", 8))
            progress_lbl.pack(pady=5)
        else:
            state_lbl = tk.Label(self.status_frame, text="Status: IDLE", 
                                fg="#888888", bg="#1e1e1e", font=("Consolas", 9, "bold"))
            state_lbl.pack(pady=(10, 5))
            
            idle_lbl = tk.Label(self.status_frame, text="No active session", 
                               fg="#FFFFFF", bg="#1e1e1e", font=("Consolas", 10))
            idle_lbl.pack(pady=5)
        
        # Session stats
        stats_lbl = tk.Label(self.status_frame, 
                            text=f"Session: #{self.session_count} | Completed: {self.completed_sessions}", 
                            fg="#888888", bg="#1e1e1e", font=("Consolas", 8))
        stats_lbl.pack(side="bottom", pady=(5, 10))
        
        # Force the window to update and redraw
        self.status_frame.update_idletasks()
        if self.status_window and self.status_window.winfo_exists():
            self.status_window.update_idletasks()

    def format_time(self, seconds):
        """Format seconds into HH:MM:SS"""
        h = seconds // 3600
        m = (seconds % 3600) // 60
        s = seconds % 60
        if h > 0:
            return f"{h:02d}:{m:02d}:{s:02d}"
        return f"{m:02d}:{s:02d}"

if __name__ == "__main__":
    TokyoFocusAgent()