# Tokyo Focus Agent 🌸

A lightweight, low-overhead focus assistant desktop widget that slides in from the bottom-right corner of your screen at customizable intervals to keep you productive and accountable.

---

## Features
* **Custom Timer Setup**: A styled, DPI-aware startup window where you can configure the interval in **Hours, Minutes, and Seconds**.
* **Zero CPU Overhead**: The countdown runs silently on a background thread with `0%` idle CPU usage.
* **Opaque Card Interface**: A dark-themed opaque widget (`#121212`) containing the assistant character and dialogue options, ensuring no parts of the UI are clipped or cut through.
* **Animated Buttons**: Retro arcade-style terminal buttons featuring color-inversion hover animations and pointing-hand cursors.
* **System Tray Integration**: Running status visibility directly in the Windows system tray. Includes a right-click context menu to cleanly **Quit** the application at any time.
* **Automatic Desktop Icon**: Generates a persistent `.ico` icon and automatically creates a **Tokyo Focus** shortcut on your Windows Desktop on first run.

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
