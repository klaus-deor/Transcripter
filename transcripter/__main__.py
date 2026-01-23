"""Main entry point for Transcripter package."""

import sys

def main():
    """Main entry point that selects the right version for the platform."""
    if sys.platform.startswith('linux'):
        # Use native GTK version on Linux (works better with GNOME)
        try:
            from transcripter.main import main as gtk_main
            gtk_main()
        except ImportError:
            # Fallback to cross-platform if GTK not available
            from transcripter.main_cross import main as cross_main
            cross_main()
    else:
        # Use cross-platform version on Windows/macOS
        from transcripter.main_cross import main as cross_main
        cross_main()

if __name__ == "__main__":
    main()
