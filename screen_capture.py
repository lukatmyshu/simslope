"""
Screen capture module for E6 TruGolf Grass Slope Detection System.
Handles window detection and screen capture functionality.
"""

import pygetwindow as gw
import numpy as np
import mss
import mss.tools
from PIL import Image
import cv2
import time
from typing import Tuple, Optional
import config

class ScreenCapture:
    def __init__(self):
        self.sct = mss.mss()
        self.window = None
        self.capture_region = None
        self.last_capture_time = 0
        self.frame_interval = 1.0 / config.CAPTURE_FPS

    def find_e6_window(self) -> Optional[gw.Window]:
        """Find and return E6 TruGolf window coordinates."""
        try:
            windows = gw.getWindowsWithTitle(config.WINDOW_TITLE_PATTERN)
            if windows:
                self.window = windows[0]
                return self.window
            return None
        except Exception as e:
            print(f"Error finding E6 window: {e}")
            return None

    def get_optimal_capture_region(self) -> Optional[dict]:
        """Determine best screen region for grass detection."""
        if not self.window:
            return None

        # Get window position and size
        left = self.window.left
        top = self.window.top + config.UI_MARGIN_TOP
        width = self.window.width
        height = self.window.height - (config.UI_MARGIN_TOP + config.UI_MARGIN_BOTTOM)

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
            self.window = self.find_e6_window()
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

    def cleanup(self):
        """Clean up resources."""
        self.sct.close() 