"""
Screen capture module for E6 TruGolf and GSPro Grass Slope Detection System.
Handles window detection and screen capture functionality.
"""

import pygetwindow as gw
import numpy as np
import mss
import mss.tools
from PIL import Image
import cv2
import time
from typing import Tuple, Optional, Dict
import config

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()
        self.window = None
        self.capture_region = None
        self.last_capture_time = 0
        self.frame_interval = 1.0 / config.CAPTURE_FPS
        self.current_simulator = None

    def find_simulator_window(self) -> Optional[Tuple[gw.Window, str]]:
        """Find and return simulator window coordinates and type."""
        try:
            for simulator, settings in config.SIMULATOR_WINDOWS.items():
                windows = gw.getWindowsWithTitle(settings["title_pattern"])
                if windows:
                    return windows[0], simulator
            return None, None
        except Exception as e:
            print(f"Error finding simulator window: {e}")
            return None, None

    def get_optimal_capture_region(self) -> Optional[dict]:
        """Determine best screen region for grass detection."""
        if not self.window or not self.current_simulator:
            return None

        # Get simulator-specific settings
        settings = config.SIMULATOR_WINDOWS[self.current_simulator]

        # Get window position and size
        left = self.window.left
        top = self.window.top + settings["ui_margin_top"]
        width = self.window.width
        height = self.window.height - (settings["ui_margin_top"] + settings["ui_margin_bottom"])

        return {
            "left": left,
            "top": top,
            "width": width,
            "height": height
        }

    def capture_golf_view(self) -> Optional[np.ndarray]:
        """Capture the main golf course view, avoiding UI."""
        current_time = time.time()
        if current_time - self.last_capture_time < self.frame_interval:
            return None

        if not self.window:
            self.window, self.current_simulator = self.find_simulator_window()
            if not self.window:
                return None

        if not self.capture_region:
            self.capture_region = self.get_optimal_capture_region()
            if not self.capture_region:
                return None

        try:
            # Capture the screen region
            screenshot = self.sct.grab(self.capture_region)
            
            # Convert to numpy array
            frame = np.array(screenshot)
            
            # Convert from BGRA to BGR
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)
            
            # Resize for processing if needed
            if config.PROCESSING_DOWNSCALE != 1.0:
                new_size = (
                    int(frame.shape[1] * config.PROCESSING_DOWNSCALE),
                    int(frame.shape[0] * config.PROCESSING_DOWNSCALE)
                )
                frame = cv2.resize(frame, new_size)

            self.last_capture_time = current_time
            return frame

        except Exception as e:
            print(f"Error capturing screen: {e}")
            return None

    def get_current_simulator(self) -> Optional[str]:
        """Return the currently detected simulator type."""
        return self.current_simulator

    def cleanup(self):
        """Clean up resources."""
        self.sct.close() 