#!/usr/bin/env python3
"""
Build script for Transcripter executables.

Usage:
    python scripts/build.py [--clean] [--debug]

Options:
    --clean     Clean build directories before building
    --debug     Build with debug mode (console window)
"""

import subprocess
import sys
import shutil
import argparse
from pathlib import Path


# Project paths
SCRIPT_DIR = Path(__file__).parent
PROJECT_ROOT = SCRIPT_DIR.parent
DIST_DIR = PROJECT_ROOT / "dist"
BUILD_DIR = PROJECT_ROOT / "build"
SPEC_FILE = PROJECT_ROOT / "packaging" / "pyinstaller" / "transcripter.spec"


def check_dependencies():
    """Check if required dependencies are installed."""
    missing = []

    # Check PyInstaller
    try:
        import PyInstaller
        print(f"✓ PyInstaller {PyInstaller.__version__} found")
    except ImportError:
        missing.append("pyinstaller")

    # Check Pillow
    try:
        import PIL
        print(f"✓ Pillow {PIL.__version__} found")
    except ImportError:
        missing.append("pillow")

    if missing:
        print(f"\n✗ Missing dependencies: {', '.join(missing)}")
        print(f"  Install with: pip install {' '.join(missing)}")
        return False

    return True


def clean_build():
    """Clean build directories."""
    print("\nCleaning build directories...")

    for dir_path in [DIST_DIR, BUILD_DIR]:
        if dir_path.exists():
            shutil.rmtree(dir_path)
            print(f"  Removed: {dir_path}")

    # Clean PyInstaller cache
    cache_dir = PROJECT_ROOT / "__pycache__"
    if cache_dir.exists():
        shutil.rmtree(cache_dir)


def ensure_icons():
    """Ensure icons are generated."""
    icons_script = SCRIPT_DIR / "generate_icons.py"
    assets_dir = PROJECT_ROOT / "packaging" / "assets"
    main_icon = assets_dir / "transcripter.png"

    if not main_icon.exists():
        print("\nGenerating icons...")
        subprocess.run([sys.executable, str(icons_script)], check=True)
    else:
        print(f"✓ Icons found at {assets_dir}")


def build(debug: bool = False):
    """Build the executable."""
    print(f"\nBuilding Transcripter for {sys.platform}...")

    # Base PyInstaller command
    cmd = [
        sys.executable, "-m", "PyInstaller",
        str(SPEC_FILE),
        "--distpath", str(DIST_DIR),
        "--workpath", str(BUILD_DIR),
        "--clean",
        "--noconfirm",
    ]

    # Add log level
    if debug:
        cmd.extend(["--log-level", "DEBUG"])
    else:
        cmd.extend(["--log-level", "INFO"])

    print(f"Running: {' '.join(cmd)}")
    print()

    result = subprocess.run(cmd, cwd=str(PROJECT_ROOT))

    if result.returncode != 0:
        print(f"\n✗ Build failed with exit code {result.returncode}")
        sys.exit(result.returncode)


def get_output_path() -> Path:
    """Get the path to the built executable."""
    if sys.platform == "darwin":
        return DIST_DIR / "Transcripter.app"
    elif sys.platform == "win32":
        return DIST_DIR / "Transcripter.exe"
    else:
        return DIST_DIR / "Transcripter"


def print_summary():
    """Print build summary."""
    output = get_output_path()

    print("\n" + "=" * 60)
    print("BUILD COMPLETE")
    print("=" * 60)

    if output.exists():
        if output.is_dir():
            # macOS .app bundle
            size = sum(f.stat().st_size for f in output.rglob("*") if f.is_file())
        else:
            size = output.stat().st_size

        size_mb = size / (1024 * 1024)
        print(f"\n✓ Output: {output}")
        print(f"✓ Size: {size_mb:.1f} MB")

        print("\nTo run:")
        if sys.platform == "darwin":
            print(f"  open {output}")
        elif sys.platform == "win32":
            print(f"  {output}")
        else:
            print(f"  {output}")
            print("\nTo create AppImage (Linux):")
            print("  ./packaging/linux/build_appimage.sh")
    else:
        print(f"\n✗ Output not found: {output}")


def main():
    parser = argparse.ArgumentParser(description="Build Transcripter executable")
    parser.add_argument("--clean", action="store_true", help="Clean build directories")
    parser.add_argument("--debug", action="store_true", help="Build with debug mode")
    args = parser.parse_args()

    print("=" * 60)
    print("TRANSCRIPTER BUILD SCRIPT")
    print("=" * 60)
    print(f"\nPlatform: {sys.platform}")
    print(f"Python: {sys.version}")

    # Check dependencies
    if not check_dependencies():
        sys.exit(1)

    # Clean if requested
    if args.clean:
        clean_build()

    # Ensure icons exist
    ensure_icons()

    # Build
    build(debug=args.debug)

    # Summary
    print_summary()


if __name__ == "__main__":
    main()
