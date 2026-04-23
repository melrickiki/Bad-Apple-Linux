# Bad Apple Linux Troll Edition 🍎

A recreation of the iconic "Bad Apple" animation using actual OS windows on Linux. This program spawns, moves, and resizes windows dynamically to form the silhouettes of the animation.

![Bad Apple Setup](https://raw.githubusercontent.com/your-username/bad-apple-linux-troll/main/preview.png) *(Note: Replace with actual screenshot link)*

## Features

- **Window-based Rendering**: Each white part of the video is rendered using real OS windows.
- **Optimized Performance**: Uses a greedy rectangle algorithm to minimize the number of windows needed.
- **Adwaita Interface**: A modern setup GUI to choose resolution and display modes.
- **Audio Sync**: Automatically plays audio via `ffplay` or `mpv` with frame-skipping logic to keep everything in sync.
- **Standalone Binary**: Can be compiled into a single executable that includes the video and icon.

## Installation

### Prerequisites

You need `python3` installed. For audio playback, it is recommended to have `ffplay` (from ffmpeg) or `mpv`.

```bash
# On Fedora/RedHat
sudo dnf install ffmpeg mpv python3-tkinter
```

### Running from source

1. Clone the repository.
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run the script:
   ```bash
   python main.py
   ```

## Compiling to Standalone Binary

To create a single binaire containing everything:

```bash
pip install pyinstaller
pyinstaller --onefile --noconsole --add-data "bad_apple.mp4:." --add-data "icon.png:." --name bad_apple_troll main.py
```

The executable will be generated in the `dist/` folder.

## Controls

- **Esc** or **q**: Close the animation (especially useful in borderless mode).

## Acknowledgments

- Original "Bad Apple!!" animation by Alstroemeria Records.
- Inspired by various "window manager troll" projects.

## License

MIT
