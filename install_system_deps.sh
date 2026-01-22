#!/bin/bash
# Installation script for Transcripter system dependencies

set -e

echo "==================================="
echo "Transcripter System Dependencies"
echo "==================================="
echo ""

# Detect distribution
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VER=$VERSION_ID
else
    echo "Cannot detect Linux distribution"
    exit 1
fi

echo "Detected OS: $OS"
echo ""

case $OS in
    ubuntu|debian|pop|linuxmint)
        echo "Installing dependencies for Debian/Ubuntu-based system..."
        sudo apt update
        sudo apt install -y \
            python3 \
            python3-pip \
            python3-venv \
            python3-gi \
            python3-gi-cairo \
            gir1.2-gtk-3.0 \
            gir1.2-appindicator3-0.1 \
            gir1.2-notify-0.7 \
            portaudio19-dev \
            libportaudio2 \
            libasound2-dev \
            libcairo2-dev \
            libgirepository1.0-dev \
            python3-dev \
            libx11-dev \
            pkg-config \
            xclip

        # For GNOME users, install AppIndicator extension
        if [ "$XDG_CURRENT_DESKTOP" = "GNOME" ]; then
            echo ""
            echo "GNOME detected. Installing AppIndicator extension..."
            sudo apt install -y gnome-shell-extension-appindicator
            echo ""
            echo "NOTE: You may need to enable the AppIndicator extension in 'Extensions' or 'Tweaks'"
        fi
        ;;

    fedora|rhel|centos)
        echo "Installing dependencies for Fedora/RHEL-based system..."
        sudo dnf install -y \
            python3 \
            python3-pip \
            python3-gobject \
            gtk3 \
            libappindicator-gtk3 \
            portaudio-devel \
            alsa-lib-devel \
            python3-devel \
            libX11-devel \
            xclip
        ;;

    arch|manjaro)
        echo "Installing dependencies for Arch-based system..."
        sudo pacman -S --noconfirm \
            python \
            python-pip \
            python-gobject \
            gtk3 \
            libappindicator-gtk3 \
            portaudio \
            alsa-lib \
            libx11 \
            xclip
        ;;

    opensuse*)
        echo "Installing dependencies for openSUSE..."
        sudo zypper install -y \
            python3 \
            python3-pip \
            python3-gobject \
            gtk3 \
            libappindicator3-1 \
            portaudio-devel \
            alsa-devel \
            libX11-devel \
            xclip
        ;;

    *)
        echo "Unsupported distribution: $OS"
        echo "Please install dependencies manually. See README.md for requirements."
        exit 1
        ;;
esac

echo ""
echo "==================================="
echo "System dependencies installed!"
echo "==================================="
echo ""
echo "Next steps:"
echo "1. Create a virtual environment WITH system packages access:"
echo "   python3 -m venv --system-site-packages venv"
echo ""
echo "2. Activate it:"
echo "   source venv/bin/activate"
echo ""
echo "3. Install Python packages:"
echo "   pip install -r requirements.txt"
echo ""
echo "4. Install the application:"
echo "   pip install -e ."
echo ""
echo "5. Run the application:"
echo "   transcripter"
echo ""
echo "IMPORTANT: Check if your user is in the 'audio' group:"
echo "  groups | grep audio"
echo ""
echo "If not, add yourself to the audio group:"
echo "  sudo usermod -a -G audio $USER"
echo "  (then logout and login again)"
echo ""
