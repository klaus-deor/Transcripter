"""PyInstaller hook for Transcripter."""

from PyInstaller.utils.hooks import collect_submodules, collect_data_files

# Collect all transcripter submodules
hiddenimports = collect_submodules('transcripter')

# Also collect provider submodules explicitly
hiddenimports += collect_submodules('transcripter.providers')
hiddenimports += collect_submodules('transcripter.gui_cross')

# Collect sounddevice data files (needed for PortAudio binaries)
try:
    datas = collect_data_files('sounddevice')
except Exception:
    datas = []

# Collect soundfile data files
try:
    datas += collect_data_files('soundfile')
except Exception:
    pass
