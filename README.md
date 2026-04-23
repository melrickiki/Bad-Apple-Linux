# 🍎 Bad Apple — Linux (Window Renderer)

A recreation of the iconic **Bad Apple!!** animation rendered using real OS windows on Linux.

Instead of drawing pixels, this program dynamically spawns, moves, and resizes windows to reproduce each frame of the animation.

![Preview](https://raw.githubusercontent.com/melrickiki/Bad-Apple-Linux/main/preview.png)

---

## ✨ Features

* **Window-Based Rendering**
  Bright areas of each frame are represented using real OS windows.

* **Rectangle Merging Optimization**
  Uses a greedy rectangle algorithm to reduce the total number of windows per frame.

* **Simple GUI (Adwaita)**
  Allows selection of resolution and display mode before playback.

* **Audio Playback & Sync**
  Uses `ffplay` (FFmpeg) or `mpv`. Basic frame-skipping is used to reduce desync under load.

* **Standalone Build Support**
  Can be packaged into a single executable including assets.

---

## ⚠️ Limitations

Don’t skip this — it’s where most similar projects lose credibility:

* Performance heavily depends on:

  * your CPU
  * your window manager / compositor
* May behave differently on:

  * X11 vs Wayland
* High resolutions can cause:

  * lag
  * desynchronization
  * excessive window spawning

This is not a video player — it’s a rendering experiment.

---

## ⚙️ Installation

### Requirements

* Python 3
* `tkinter` (for GUI)
* Optional (audio):

  * `ffplay` (from FFmpeg)
  * or `mpv`

### Fedora / RedHat

```bash
sudo dnf install ffmpeg mpv python3-tkinter
```

---

## 🚀 Run from Source

```bash
git clone https://github.com/your-username/bad-apple-linux-troll.git
cd bad-apple-linux-troll

pip install -r requirements.txt
python main.py
```

---

## 📦 Build Standalone Binary

```bash
pip install pyinstaller

pyinstaller \
  --onefile \
  --noconsole \
  --add-data "bad_apple.mp4:." \
  --add-data "icon.png:." \
  --name bad_apple_troll \
  main.py
```

Output:

```
dist/
```

---

## 🎮 Controls

| Key         | Action         |
| ----------- | -------------- |
| `Esc` / `q` | Exit animation |

---

## 🙏 Credits

* **Bad Apple!!** — Alstroemeria Records
* Concept inspired by window-based rendering experiments

---
