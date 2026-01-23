"""GNOME shortcut configuration for Wayland compatibility."""

import subprocess
import os
from typing import Optional


def is_wayland() -> bool:
    """Check if running under Wayland."""
    return os.environ.get('XDG_SESSION_TYPE') == 'wayland'


def get_existing_shortcuts() -> list:
    """Get list of existing custom shortcut paths."""
    try:
        result = subprocess.run(
            ['gsettings', 'get', 'org.gnome.settings-daemon.plugins.media-keys', 'custom-keybindings'],
            capture_output=True, text=True
        )
        if result.returncode == 0:
            # Parse the output like "['path1', 'path2']" or "@as []"
            output = result.stdout.strip()
            if output == '@as []':
                return []
            # Remove brackets and quotes, split by comma
            output = output.strip('[]').replace("'", "").replace(" ", "")
            if output:
                return output.split(',')
        return []
    except Exception:
        return []


def shortcut_exists(name: str = "Transcripter") -> bool:
    """Check if Transcripter shortcut already exists."""
    shortcuts = get_existing_shortcuts()
    for path in shortcuts:
        try:
            result = subprocess.run(
                ['gsettings', 'get', f'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:{path}', 'name'],
                capture_output=True, text=True
            )
            if name in result.stdout:
                return True
        except Exception:
            pass
    return False


def convert_hotkey_to_gnome(hotkey: str) -> str:
    """Convert hotkey format from 'ctrl+alt+r' to '<Ctrl><Alt>r'."""
    parts = hotkey.lower().replace(' ', '').split('+')
    result = ""
    key = ""

    for part in parts:
        if part in ('ctrl', 'control'):
            result += "<Ctrl>"
        elif part in ('alt',):
            result += "<Alt>"
        elif part in ('shift',):
            result += "<Shift>"
        elif part in ('super', 'win', 'meta'):
            result += "<Super>"
        else:
            key = part

    return result + key


def create_gnome_shortcut(
    hotkey: str = "<Ctrl><Alt>r",
    name: str = "Transcripter",
) -> tuple[bool, str]:
    """
    Create a GNOME keyboard shortcut for Transcripter.

    Args:
        hotkey: The keyboard shortcut (e.g., 'ctrl+alt+r' or '<Ctrl><Alt>r')
        name: Name of the shortcut

    Returns:
        Tuple of (success, message)
    """
    try:
        # Convert hotkey format if needed
        if '<' not in hotkey:
            hotkey = convert_hotkey_to_gnome(hotkey)

        # Remove existing shortcut first to update it
        if shortcut_exists(name):
            remove_gnome_shortcut(name)

        # Get existing shortcuts
        existing = get_existing_shortcuts()

        # Find next available slot
        slot = 0
        while f'/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom{slot}/' in existing:
            slot += 1

        path = f'/org/gnome/settings-daemon/plugins/media-keys/custom-keybindings/custom{slot}/'
        schema = f'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:{path}'

        # Command to toggle recording - use dedicated toggle script
        command = "/usr/bin/transcripter-toggle"

        # Set shortcut properties
        subprocess.run(['gsettings', 'set', schema, 'name', name], check=True)
        subprocess.run(['gsettings', 'set', schema, 'command', command], check=True)
        subprocess.run(['gsettings', 'set', schema, 'binding', hotkey], check=True)

        # Add to list of custom keybindings
        existing.append(path)
        shortcuts_str = "['" + "', '".join(existing) + "']"
        subprocess.run([
            'gsettings', 'set',
            'org.gnome.settings-daemon.plugins.media-keys',
            'custom-keybindings',
            shortcuts_str
        ], check=True)

        return True, f"Atalho {hotkey} configurado com sucesso!"

    except subprocess.CalledProcessError as e:
        return False, f"Erro ao configurar atalho: {e}"
    except Exception as e:
        return False, f"Erro: {e}"


def remove_gnome_shortcut(name: str = "Transcripter") -> tuple[bool, str]:
    """Remove the Transcripter GNOME shortcut."""
    try:
        shortcuts = get_existing_shortcuts()
        new_shortcuts = []
        removed = False

        for path in shortcuts:
            try:
                result = subprocess.run(
                    ['gsettings', 'get', f'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:{path}', 'name'],
                    capture_output=True, text=True
                )
                if name not in result.stdout:
                    new_shortcuts.append(path)
                else:
                    # Reset this shortcut
                    schema = f'org.gnome.settings-daemon.plugins.media-keys.custom-keybinding:{path}'
                    subprocess.run(['gsettings', 'reset', schema, 'name'], check=False)
                    subprocess.run(['gsettings', 'reset', schema, 'command'], check=False)
                    subprocess.run(['gsettings', 'reset', schema, 'binding'], check=False)
                    removed = True
            except Exception:
                new_shortcuts.append(path)

        if removed:
            if new_shortcuts:
                shortcuts_str = "['" + "', '".join(new_shortcuts) + "']"
            else:
                shortcuts_str = "@as []"
            subprocess.run([
                'gsettings', 'set',
                'org.gnome.settings-daemon.plugins.media-keys',
                'custom-keybindings',
                shortcuts_str
            ], check=True)
            return True, "Atalho removido!"

        return False, "Atalho não encontrado"

    except Exception as e:
        return False, f"Erro: {e}"


def setup_wayland_shortcut_interactive() -> None:
    """Interactive setup for Wayland shortcut."""
    print("")
    print("=" * 50)
    print("Configuração de Atalho para Wayland/GNOME")
    print("=" * 50)
    print("")

    if shortcut_exists():
        print("Atalho já está configurado!")
        print("Use Ctrl+Alt+R para iniciar/parar gravação.")
        return

    print("Deseja configurar o atalho Ctrl+Alt+R automaticamente?")
    print("Isso permitirá usar hotkeys mesmo no Wayland.")
    print("")

    try:
        response = input("Configurar agora? [S/n]: ").strip().lower()
        if response in ('', 's', 'sim', 'y', 'yes'):
            success, msg = create_gnome_shortcut()
            print(msg)
            if success:
                print("")
                print("Pronto! Use Ctrl+Alt+R para gravar/parar.")
        else:
            print("Configuração cancelada.")
            print("Você pode configurar manualmente em:")
            print("  Configurações > Teclado > Atalhos Personalizados")
    except EOFError:
        # Non-interactive mode
        pass
