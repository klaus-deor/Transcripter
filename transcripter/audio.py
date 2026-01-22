"""Audio recording module for Transcripter."""

import sounddevice as sd
import numpy as np
import wave
import threading
import time
from pathlib import Path
from typing import Optional, Callable, List, Dict
from dataclasses import dataclass


@dataclass
class AudioDevice:
    """Represents an audio input device."""
    index: int
    name: str
    channels: int
    sample_rate: float


class AudioRecorder:
    """Handles audio recording from microphone."""

    def __init__(
        self,
        sample_rate: int = 16000,
        channels: int = 1,
        device_name: Optional[str] = None
    ):
        """
        Initialize the audio recorder.

        Args:
            sample_rate: Sample rate in Hz (default: 16000)
            channels: Number of audio channels (default: 1 for mono)
            device_name: Name of the audio device to use (None for default)
        """
        self.sample_rate = sample_rate
        self.channels = channels
        self.device_name = device_name
        self.device_index = self._get_device_index(device_name)

        self.is_recording = False
        self.recording_thread: Optional[threading.Thread] = None
        self.audio_data: List[np.ndarray] = []
        self.start_time: Optional[float] = None
        self.max_duration: Optional[int] = None

        # Callbacks
        self.on_recording_started: Optional[Callable] = None
        self.on_recording_stopped: Optional[Callable] = None
        self.on_error: Optional[Callable[[Exception], None]] = None

    @staticmethod
    def list_devices() -> List[AudioDevice]:
        """
        List all available audio input devices.

        Returns:
            List of AudioDevice objects
        """
        devices = []
        device_list = sd.query_devices()

        for idx, device in enumerate(device_list):
            # Only include input devices
            if device['max_input_channels'] > 0:
                devices.append(AudioDevice(
                    index=idx,
                    name=device['name'],
                    channels=device['max_input_channels'],
                    sample_rate=device['default_samplerate']
                ))

        return devices

    def _get_device_index(self, device_name: Optional[str]) -> Optional[int]:
        """
        Get device index by name.

        Args:
            device_name: Name of the device

        Returns:
            Device index or None for default device
        """
        if not device_name:
            return None

        devices = self.list_devices()
        for device in devices:
            if device_name.lower() in device.name.lower():
                return device.index

        print(f"Warning: Device '{device_name}' not found. Using default device.")
        return None

    def _audio_callback(self, indata, frames, time_info, status):
        """
        Callback function for audio stream.

        Args:
            indata: Input audio data
            frames: Number of frames
            time_info: Time information
            status: Status flags
        """
        if status:
            print(f"Audio callback status: {status}")

        if self.is_recording:
            # Store audio data
            self.audio_data.append(indata.copy())

            # Check max duration
            if self.max_duration:
                elapsed = time.time() - self.start_time
                if elapsed >= self.max_duration:
                    self.stop_recording()

    def start_recording(self, max_duration: Optional[int] = None) -> bool:
        """
        Start recording audio.

        Args:
            max_duration: Maximum recording duration in seconds (None for unlimited)

        Returns:
            True if recording started successfully, False otherwise
        """
        if self.is_recording:
            print("Already recording")
            return False

        try:
            self.audio_data = []
            self.is_recording = True
            self.start_time = time.time()
            self.max_duration = max_duration

            # Start audio stream in a separate thread
            self.recording_thread = threading.Thread(target=self._record_audio)
            self.recording_thread.daemon = True
            self.recording_thread.start()

            if self.on_recording_started:
                self.on_recording_started()

            return True

        except Exception as e:
            print(f"Error starting recording: {e}")
            self.is_recording = False
            if self.on_error:
                self.on_error(e)
            return False

    def _record_audio(self):
        """Internal method to handle audio recording stream."""
        try:
            with sd.InputStream(
                device=self.device_index,
                channels=self.channels,
                samplerate=self.sample_rate,
                callback=self._audio_callback
            ):
                while self.is_recording:
                    time.sleep(0.1)

        except Exception as e:
            print(f"Error in recording thread: {e}")
            self.is_recording = False
            if self.on_error:
                self.on_error(e)

    def stop_recording(self) -> Optional[np.ndarray]:
        """
        Stop recording audio.

        Returns:
            Numpy array containing the recorded audio data, or None if no data
        """
        if not self.is_recording:
            print("Not currently recording")
            return None

        self.is_recording = False

        # Wait for recording thread to finish
        if self.recording_thread:
            self.recording_thread.join(timeout=2.0)

        if self.on_recording_stopped:
            self.on_recording_stopped()

        # Concatenate all audio chunks
        if self.audio_data:
            audio = np.concatenate(self.audio_data, axis=0)
            return audio
        else:
            print("No audio data recorded")
            return None

    def save_to_file(self, audio_data: np.ndarray, file_path: str) -> bool:
        """
        Save recorded audio to a WAV file.

        Args:
            audio_data: Numpy array containing audio data
            file_path: Path to save the audio file

        Returns:
            True if saved successfully, False otherwise
        """
        try:
            # Ensure directory exists
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            # Normalize audio data to 16-bit PCM
            audio_int16 = np.int16(audio_data * 32767)

            # Write WAV file
            with wave.open(file_path, 'w') as wf:
                wf.setnchannels(self.channels)
                wf.setsampwidth(2)  # 16-bit
                wf.setframerate(self.sample_rate)
                wf.writeframes(audio_int16.tobytes())

            return True

        except Exception as e:
            print(f"Error saving audio file: {e}")
            if self.on_error:
                self.on_error(e)
            return False

    def get_recording_duration(self) -> float:
        """
        Get current recording duration in seconds.

        Returns:
            Duration in seconds, or 0 if not recording
        """
        if self.is_recording and self.start_time:
            return time.time() - self.start_time
        return 0.0

    def set_device(self, device_name: str) -> bool:
        """
        Set the audio input device.

        Args:
            device_name: Name of the device to use

        Returns:
            True if device was found and set, False otherwise
        """
        if self.is_recording:
            print("Cannot change device while recording")
            return False

        device_index = self._get_device_index(device_name)
        if device_index is not None:
            self.device_index = device_index
            self.device_name = device_name
            return True

        return False


def get_default_device() -> Optional[AudioDevice]:
    """
    Get the default audio input device.

    Returns:
        AudioDevice object or None if no device found
    """
    try:
        default_device = sd.query_devices(kind='input')
        if default_device:
            return AudioDevice(
                index=sd.default.device[0] if isinstance(sd.default.device, tuple) else sd.default.device,
                name=default_device['name'],
                channels=default_device['max_input_channels'],
                sample_rate=default_device['default_samplerate']
            )
    except Exception as e:
        print(f"Error getting default device: {e}")

    return None
