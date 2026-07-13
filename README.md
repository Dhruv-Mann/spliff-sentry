# Tokyo Focus Agent

A lightweight, low-overhead focus assistant desktop widget that slides in from the bottom-right corner at customizable intervals to check on your productivity and keep you accountable.

## Features
* **Customizable Timers**: Prompts for interval length in minutes at startup.
* **Low Footprint**: Countdown sleeps on a background thread with zero idle CPU overhead.
* **Non-Intrusive Display**: Slid-in UI pops up in the bottom-right corner (just above the taskbar) instead of blocking your center viewport.
* **Smooth Rendering**: High-quality aspect-ratio-preserving character image scaling via Pillow.
* **Clean Interactive UI**: Sleek console-style dark mode styling with reactive button hover animations (full color inversion) and pointer cursors.
* **Direct UI Stop**: A clearly visible and clickable Exit button that cleanly terminates the background process.

## Prerequisites
* Python 3.x
* Pillow (PIL)

To install dependencies:
```bash
pip install Pillow
```

## Running the Application
To run via Python:
```bash
python main.py
```
Alternatively, run the compiled binary directly:
```bash
dist/main.exe
```

## Building the Executable
The project is configured for compilation into a single-file executable using PyInstaller.
To rebuild `main.exe`:
```bash
pyinstaller main.spec --noconfirm
```
The compiled output will be generated in the `dist/` directory.
