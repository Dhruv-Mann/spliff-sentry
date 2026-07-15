# Tokyo Focus Agent 🌸

A functional focus timer and productivity assistant that runs in the background, helping you track work sessions and stay accountable with smart session management and real-time progress tracking.

---

## Features

### 🎯 Core Productivity
* **Session Tracking**: Track your focus sessions with automatic numbering (#1, #2, #3...) and completion counts
* **Smart Timer Management**: Pause/resume functionality without losing progress
* **Real-Time Status Window**: See time remaining, progress percentage, and session stats at a glance
* **Multiple Session Actions**:
  - **Continue** - Mark session as complete and start the next one
  - **Done for Now** - Pause without resetting your progress
  - **Reset** - Start fresh from session #1 if you got off track
  
### 🎨 Interface & UX
* **Custom Timer Setup**: Configure intervals in Hours, Minutes, and Seconds with a sleek dark-themed UI
* **Slide-In Notification**: Character slides in from bottom-right when timer completes
* **Opaque Card Interface**: Dark-themed (`#121212`) widget with retro terminal aesthetic
* **Animated Buttons**: Color-inversion hover effects and pointing-hand cursors

### ⚡ Performance & Integration
* **Zero CPU Overhead**: Runs silently on background thread with 0% idle CPU usage
* **Enhanced System Tray**:
  - Show/hide status window
  - Pause/resume timer
  - Quick quit
* **Automatic Desktop Icon**: Generates `.ico` and creates desktop shortcut on first run
* **Single Instance**: Prevents multiple copies from running simultaneously

---

## 🛠️ Step-by-Step Installation

### Step 1: Install Python 3.x
Ensure you have Python 3 installed on your system. You can verify this by opening a terminal and running:
```bash
python --version
```

### Step 2: Install Required Dependencies
The application requires `Pillow` (for image processing/scaling) and `pystray` (for system tray integration). Install them using `pip`:
```bash
pip install Pillow pystray
```
*Note: If you have multiple Python versions installed, make sure to install dependencies on the correct interpreter version you intend to use.*

### Step 3: Verify the Artwork Asset
Ensure that the file `tokyospliff.png` is placed in the project root directory alongside `main.py`. The application loads this image dynamically.

---

## 🚀 How to Run

### Option A: Run from Source (Python)
To start the application from your terminal:
```bash
python main.py
```
* On your first run, the app will:
  1. Generate `tokyospliff.ico` from your artwork.
  2. Create a **Tokyo Focus** shortcut directly on your Windows Desktop.
  3. Load the system tray icon in the taskbar.

### Option B: Run the Precompiled Executable
If you don't want to run Python scripts directly, you can launch the compiled standalone executable:
```bash
dist/main.exe
```
You can also double-click the **Tokyo Focus** shortcut created on your desktop.

---

## 💡 How to Use

1. **Start a Session**: Set your desired time and click "Start Focus"
2. **Track Progress**: Right-click the system tray icon → "Show Status" to see real-time progress
3. **Pause/Resume**: Right-click tray icon → "Pause/Resume" or use the status window
4. **When Timer Completes**:
   - **Cookin' Cuh - Continue**: Session marked complete, new session starts
   - **Done for Now**: Minimize to tray, resume later
   - **Caught Slacking... Reset**: Reset all progress back to session #1
5. **View Stats**: Status window shows session number and total completed sessions

---

## ⚙️ Building the Standalone Executable (`.exe`)

The project is preconfigured with a PyInstaller specification (`main.spec`) to bundle the code, PIL, pystray, and the character artwork asset into a single executable that runs silently (no console window).

### Step 1: Install PyInstaller
```bash
pip install pyinstaller
```

### Step 2: Run the Compile Command
Open a terminal in the project directory and run:
```bash
pyinstaller main.spec --noconfirm
```

### Step 3: Access the Executable
Once the build completes, your standalone executable `main.exe` will be located in the `dist/` directory:
`D:\GitHub\Tokyospliff\dist\main.exe`

---

## 📁 Repository Structure
* [main.py](file:///d:/GitHub/Tokyospliff/main.py): Core Tkinter GUI, countdown thread, system tray, and shortcut setup logic.
* [main.spec](file:///d:/GitHub/Tokyospliff/main.spec): PyInstaller build configuration.
* [tokyospliff.png](file:///d:/GitHub/Tokyospliff/tokyospliff.png): High-resolution artwork of the focus character.
* [tokyospliff.ico](file:///d:/GitHub/Tokyospliff/tokyospliff.ico): Windows desktop icon (auto-generated from the PNG).
* [README.md](file:///d:/GitHub/Tokyospliff/README.md): Step-by-step setup guide.
* `.gitignore`: Configured to ignore compiled binaries (`dist/`, `build/`) and raw assets to keep your GitHub commits lightweight.
