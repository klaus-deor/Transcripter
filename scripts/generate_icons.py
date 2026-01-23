#!/usr/bin/env python3
"""Generate icons for Transcripter in various sizes and formats."""

import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw
except ImportError:
    print("Pillow required. Install with: pip install pillow")
    sys.exit(1)


def create_microphone_icon(size: int, recording: bool = False) -> Image.Image:
    """
    Create a minimalist microphone icon.

    Args:
        size: Icon size in pixels (square)
        recording: If True, create recording state icon (red dot)

    Returns:
        PIL Image object
    """
    image = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(image)

    # Scale factors
    center_x = size // 2
    center_y = size // 2
    line_width = max(2, size // 12)

    # Color - white for normal, red for recording
    color = '#FF4444' if recording else '#FFFFFF'

    # Microphone dimensions
    mic_width = size // 3
    mic_height = size // 2
    mic_left = center_x - mic_width // 2
    mic_right = mic_left + mic_width
    mic_top = size // 8
    mic_bottom = mic_top + mic_height

    # Draw microphone head (rounded rectangle / pill shape)
    # Top arc
    draw.arc(
        [mic_left, mic_top, mic_right, mic_top + mic_width],
        start=180,
        end=0,
        fill=color,
        width=line_width
    )
    # Left side
    draw.line(
        [(mic_left, mic_top + mic_width // 2), (mic_left, mic_bottom - mic_width // 4)],
        fill=color,
        width=line_width
    )
    # Right side
    draw.line(
        [(mic_right, mic_top + mic_width // 2), (mic_right, mic_bottom - mic_width // 4)],
        fill=color,
        width=line_width
    )
    # Bottom arc of mic head
    draw.arc(
        [mic_left, mic_bottom - mic_width // 2, mic_right, mic_bottom],
        start=0,
        end=180,
        fill=color,
        width=line_width
    )

    # Holder arc (U shape around microphone)
    holder_padding = size // 6
    holder_top = mic_bottom - mic_width // 3
    holder_bottom = mic_bottom + size // 6
    draw.arc(
        [holder_padding, holder_top, size - holder_padding, holder_bottom + size // 8],
        start=0,
        end=180,
        fill=color,
        width=line_width
    )

    # Stand (vertical line from holder to base)
    stand_top = holder_bottom
    stand_bottom = size - size // 6
    draw.line(
        [(center_x, stand_top), (center_x, stand_bottom)],
        fill=color,
        width=line_width
    )

    # Base (horizontal line)
    base_width = size // 3
    draw.line(
        [(center_x - base_width // 2, stand_bottom), (center_x + base_width // 2, stand_bottom)],
        fill=color,
        width=line_width
    )

    # If recording, add a small red dot indicator in corner
    if recording:
        dot_size = max(4, size // 8)
        dot_x = size - dot_size - 2
        dot_y = 2
        draw.ellipse(
            [dot_x, dot_y, dot_x + dot_size, dot_y + dot_size],
            fill='#FF0000'
        )

    return image


def generate_all_icons(output_dir: Path) -> None:
    """
    Generate all required icons.

    Args:
        output_dir: Directory to save icons
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Main icon sizes
    sizes = {
        'transcripter.png': 512,
        'transcripter_256.png': 256,
        'transcripter_128.png': 128,
        'transcripter_64.png': 64,
        'transcripter_48.png': 48,
        'transcripter_32.png': 32,
        'transcripter_16.png': 16,
    }

    # Recording icon sizes
    recording_sizes = {
        'recording.png': 64,
        'recording_32.png': 32,
    }

    # Generate main icons
    for filename, size in sizes.items():
        icon = create_microphone_icon(size, recording=False)
        icon.save(output_dir / filename, 'PNG')
        print(f"Created: {filename} ({size}x{size})")

    # Generate recording icons
    for filename, size in recording_sizes.items():
        icon = create_microphone_icon(size, recording=True)
        icon.save(output_dir / filename, 'PNG')
        print(f"Created: {filename} ({size}x{size})")


def create_ico_file(output_dir: Path) -> None:
    """Create Windows .ico file with multiple sizes."""
    ico_path = output_dir.parent / 'windows' / 'transcripter.ico'
    ico_path.parent.mkdir(parents=True, exist_ok=True)

    # Create icons at different sizes for ICO
    sizes = [16, 32, 48, 64, 128, 256]
    images = [create_microphone_icon(s, recording=False) for s in sizes]

    # Save as ICO
    images[0].save(
        ico_path,
        format='ICO',
        sizes=[(s, s) for s in sizes],
        append_images=images[1:]
    )
    print(f"Created: {ico_path}")


def create_icns_file(output_dir: Path) -> None:
    """Create macOS .icns file."""
    try:
        import subprocess
    except ImportError:
        print("Skipping .icns creation (requires iconutil on macOS)")
        return

    icns_dir = output_dir.parent / 'macos'
    icns_dir.mkdir(parents=True, exist_ok=True)

    # Create iconset directory
    iconset_dir = icns_dir / 'transcripter.iconset'
    iconset_dir.mkdir(exist_ok=True)

    # macOS icon sizes (name pattern: icon_WxH.png and icon_WxH@2x.png)
    sizes = [
        (16, 'icon_16x16.png'),
        (32, 'icon_16x16@2x.png'),
        (32, 'icon_32x32.png'),
        (64, 'icon_32x32@2x.png'),
        (128, 'icon_128x128.png'),
        (256, 'icon_128x128@2x.png'),
        (256, 'icon_256x256.png'),
        (512, 'icon_256x256@2x.png'),
        (512, 'icon_512x512.png'),
        (1024, 'icon_512x512@2x.png'),
    ]

    for size, filename in sizes:
        icon = create_microphone_icon(size, recording=False)
        icon.save(iconset_dir / filename, 'PNG')

    print(f"Created iconset at: {iconset_dir}")
    print("To create .icns on macOS, run: iconutil -c icns transcripter.iconset")


def main():
    """Main entry point."""
    # Determine output directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent
    assets_dir = project_root / 'packaging' / 'assets'

    print("Generating Transcripter icons...")
    print(f"Output directory: {assets_dir}")
    print()

    generate_all_icons(assets_dir)
    print()

    create_ico_file(assets_dir)
    print()

    create_icns_file(assets_dir)
    print()

    # Also copy main icons to the gui/icons directory for development
    gui_icons_dir = project_root / 'transcripter' / 'gui' / 'icons'
    gui_icons_dir.mkdir(parents=True, exist_ok=True)

    for name in ['transcripter.png', 'recording.png']:
        src = assets_dir / name
        dst = gui_icons_dir / name
        if src.exists():
            import shutil
            shutil.copy(src, dst)
            print(f"Copied to development: {dst}")

    print()
    print("Done!")


if __name__ == "__main__":
    main()
