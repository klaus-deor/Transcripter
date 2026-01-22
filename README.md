<p align="center">
  <img src="https://img.icons8.com/fluency/96/000000/microphone.png" alt="Transcripter Logo"/>
</p>

<h1 align="center">Transcripter</h1>

<p align="center">
  <strong>Transform your voice into text instantly!</strong>
</p>

<p align="center">
  <a href="https://github.com/klaus-deor/Transcripter/blob/main/LICENSE">
    <img src="https://img.shields.io/badge/license-MIT-blue.svg" alt="License"/>
  </a>
  <a href="https://www.python.org/downloads/">
    <img src="https://img.shields.io/badge/python-3.8+-green.svg" alt="Python"/>
  </a>
  <img src="https://img.shields.io/badge/platform-Linux%20%7C%20macOS%20%7C%20Windows-orange.svg" alt="Platform"/>
</p>

---

## What is Transcripter?

**Transcripter** is a cross-platform audio transcription tool that converts your speech to text using the powerful Groq Whisper API.

With just a keyboard shortcut, you can:
1. Record your voice
2. Have the audio transcribed automatically
3. Get the text copied to your clipboard

That simple!

---

## Quick Demo

```
1. Press Ctrl+Alt+R (or Ctrl+Option+R on Mac) → Start recording
2. Speak whatever you want
3. Press the hotkey again → Stop recording
4. Wait 2-3 seconds
5. Use Ctrl+V anywhere → Transcribed text!
```

---

## Features

| Feature | Description |
|---------|-------------|
| **Global Hotkey** | Record audio from anywhere with `Ctrl+Alt+R` |
| **Fast Transcription** | Uses Groq Whisper API (extremely fast) |
| **Auto Clipboard** | Text automatically copied to clipboard |
| **History** | Access previous transcriptions |
| **Multi-language** | Supports Portuguese, English, Spanish, and more |
| **System Tray** | Discrete icon in system tray |
| **Notifications** | Visual feedback of status |
| **Configurable** | Customize hotkeys, language, and more |
| **Cross-Platform** | Works on Linux, macOS, and Windows |

---

## Requirements

### Supported Operating Systems
- **Linux** (Ubuntu, Debian, Fedora, Arch, etc.)
- **macOS** (10.14 Mojave or later)
- **Windows** (10/11)

### Dependencies
- Python 3.8 or higher
- Internet connection (for Groq API)

---

## Installation

### Linux (Ubuntu/Debian)

#### Step 1: Clone the Repository

```bash
git clone https://github.com/klaus-deor/Transcripter.git
cd Transcripter
```

#### Step 2: Install System Dependencies

```bash
./install_system_deps.sh
```

Or manually:
```bash
sudo apt install python3-gi python3-gi-cairo gir1.2-gtk-3.0 \
    gir1.2-appindicator3-0.1 portaudio19-dev xclip
```

#### Step 3: Set Up Python Environment

```bash
python3 -m venv --system-site-packages venv
source venv/bin/activate
pip install -r requirements.txt
pip install -e .
```

#### Step 4: Run

```bash
# GTK version (native Linux experience)
transcripter

# Or cross-platform version
transcripter-cross
```

---

### macOS

#### Step 1: Clone the Repository

```bash
git clone https://github.com/klaus-deor/Transcripter.git
cd Transcripter
```

#### Step 2: Run the Installer

```bash
./install_mac.sh
```

Or manually:

```bash
# Install portaudio (requires Homebrew)
brew install portaudio

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
pip install -e .
```

#### Step 3: Run

```bash
source venv/bin/activate
transcripter-cross
```

> **Note:** On macOS, you may need to grant accessibility permissions for global hotkeys to work. Go to System Preferences → Security & Privacy → Privacy → Accessibility and add your terminal or the app.

---

### Windows

#### Step 1: Clone the Repository

```powershell
git clone https://github.com/klaus-deor/Transcripter.git
cd Transcripter
```

#### Step 2: Run the Installer

**Using PowerShell:**
```powershell
.\install_windows.ps1
```

**Or using Command Prompt:**
```cmd
install_windows.bat
```

Or manually:

```powershell
# Create virtual environment
python -m venv venv
.\venv\Scripts\Activate.ps1

# Install dependencies
pip install -r requirements.txt
pip install win10toast  # Optional: for toast notifications
pip install -e .
```

#### Step 3: Run

```powershell
.\venv\Scripts\Activate.ps1
transcripter-cross
```

---

## Getting Your API Key

1. Go to [console.groq.com](https://console.groq.com/)
2. Create a free account
3. Generate an API Key
4. Save the key
5. On first run, configure your API Key in the Settings window

---

## How to Use

### Method 1: Keyboard Shortcut (Recommended)

| Action | Shortcut |
|--------|----------|
| Start/Stop Recording | `Ctrl + Alt + R` (Windows/Linux) |
| Start/Stop Recording | `Ctrl + Option + R` (macOS) |

### Method 2: System Tray Menu

Right-click the tray icon:

```
┌─────────────────────┐
│ Status: Idle        │
├─────────────────────┤
│ Start Recording     │
├─────────────────────┤
│ History             │
│ Settings            │
│ About               │
├─────────────────────┤
│ Quit                │
└─────────────────────┘
```

---

## Settings

### Accessing Settings

1. Right-click on the tray icon
2. Select "Settings"

### Available Options

| Tab | Settings |
|-----|----------|
| **General** | Notifications, Language, Autostart |
| **Audio** | Input device (microphone) |
| **Groq API** | API Key, Whisper Model |
| **Hotkeys** | Recording shortcut |
| **History** | Maximum history size |

### Configuration File Location

| Platform | Path |
|----------|------|
| Linux | `~/.config/transcripter/config.toml` |
| macOS | `~/Library/Application Support/Transcripter/config.toml` |
| Windows | `%APPDATA%\Transcripter\config.toml` |

---

## Troubleshooting

### Linux: Tray Icon Not Showing (GNOME)

```bash
sudo apt install gnome-shell-extension-appindicator
```
Then enable the extension in "Extensions" or "Tweaks".

### Linux: Hotkeys Not Working on Wayland

Wayland blocks global hotkeys for security. Solutions:

**Option 1:** Switch to X11 at login screen

**Option 2:** Configure shortcut in system settings:
- Command: `/path/to/Transcripter/toggle_recording.sh`

See [WAYLAND_FIX.md](WAYLAND_FIX.md) for more details.

### macOS: Permission Issues

1. Go to **System Preferences** → **Security & Privacy** → **Privacy**
2. Add Terminal (or your IDE) to **Accessibility**
3. If using microphone, also add to **Microphone**

### Windows: Hotkeys Not Working

- Run the application as Administrator
- Check if any other application is using the same hotkey

### API Key Error

1. Verify the API Key is correct
2. Confirm you have credits in your Groq account
3. Test your internet connection

### Complete Diagnosis (Linux)

```bash
./diagnose_hotkeys.sh
```

---

## Project Structure

```
Transcripter/
├── transcripter/               # Main source code
│   ├── __init__.py             # Package info
│   ├── main.py                 # Linux GTK entry point
│   ├── main_cross.py           # Cross-platform entry point
│   ├── config.py               # Configuration management
│   ├── audio.py                # Audio recording
│   ├── transcription.py        # Groq API integration
│   ├── clipboard.py            # Clipboard operations
│   ├── hotkeys.py              # Global hotkey capture
│   ├── tray.py                 # Linux GTK tray icon
│   ├── tray_cross.py           # Cross-platform tray (pystray)
│   ├── platform_utils.py       # Platform detection utilities
│   ├── gui/                    # Linux GTK GUI
│   │   ├── settings.py
│   │   └── history.py
│   └── gui_cross/              # Cross-platform GUI (tkinter)
│       ├── settings.py
│       └── history.py
├── config/
│   └── default_config.toml     # Default configuration
├── requirements.txt            # Python dependencies
├── setup.py                    # Installation script
├── install_mac.sh              # macOS installer
├── install_windows.bat         # Windows installer (batch)
├── install_windows.ps1         # Windows installer (PowerShell)
├── install_system_deps.sh      # Linux dependencies installer
└── README.md                   # This file
```

---

## Technologies Used

| Technology | Use |
|------------|-----|
| **Python 3** | Main language |
| **GTK 3** | Linux GUI interface |
| **tkinter** | Cross-platform GUI |
| **pystray** | Cross-platform system tray |
| **Groq API** | Whisper transcription |
| **pynput** | Global hotkey capture |
| **sounddevice** | Audio recording |
| **keyring** | Secure API key storage |

---

## Contributing

Contributions are welcome!

1. Fork the project
2. Create a branch (`git checkout -b feature/NewFeature`)
3. Commit your changes (`git commit -m 'Add NewFeature'`)
4. Push to the branch (`git push origin feature/NewFeature`)
5. Open a Pull Request

---

## Developers

<table>
  <tr>
    <td align="center">
      <a href="https://github.com/klaus-deor">
        <img src="https://github.com/klaus-deor.png" width="100px;" alt="Klaus Deor"/><br />
        <sub><b>Klaus Deor</b></sub>
      </a>
    </td>
    <td align="center">
      <a href="https://claude.ai">
        <img src="https://img.icons8.com/fluency/100/000000/artificial-intelligence.png" width="100px;" alt="Claude Code"/><br />
        <sub><b>Claude Code</b></sub>
      </a>
      <br />
      <sub>Anthropic AI Assistant</sub>
    </td>
  </tr>
</table>

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Useful Links

- [GitHub Repository](https://github.com/klaus-deor/Transcripter)
- [Groq Console](https://console.groq.com/) - Get API Key
- [Report Bug](https://github.com/klaus-deor/Transcripter/issues)
- [Request Feature](https://github.com/klaus-deor/Transcripter/issues)

---

<p align="center">
  Made with love by <a href="https://github.com/klaus-deor">Klaus Deor</a> and <a href="https://claude.ai">Claude Code</a>
</p>

<p align="center">
  <a href="#transcripter">Back to top</a>
</p>
