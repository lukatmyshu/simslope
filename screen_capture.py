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
        self.is_fullscreen = False
        self.last_window_check = 0
        self.window_check_interval = 5.0  # Check window every 5 seconds

    def find_simulator_window(self) -> Optional[Tuple[gw.Window, str]]:
        """Find and return simulator window coordinates and type."""
        try:
            current_time = time.time()
            # Only check window title periodically to reduce overhead
            if current_time - self.last_window_check < self.window_check_interval:
                return self.window, self.current_simulator

            self.last_window_check = current_time

            # First try to find by window title
            for simulator, settings in config.SIMULATOR_WINDOWS.items():
                windows = gw.getWindowsWithTitle(settings["title_pattern"])
                if windows:
                    window = windows[0]
                    self.is_fullscreen = (window.width >= 1920 and window.height >= 1080)
                    return window, simulator

            # If no window found by title, try to find fullscreen windows
            if not self.window:  # Only if we don't already have a window
                all_windows = gw.getAllWindows()
                fullscreen_windows = [w for w in all_windows if w.width >= 1920 and w.height >= 1080]
                
                if fullscreen_windows:
                    # If we have a previous window, try to match by position
                    if self.window:
                        for window in fullscreen_windows:
                            if (abs(window.left - self.window.left) < 10 and 
                                abs(window.top - self.window.top) < 10):
                                self.is_fullscreen = True
                                return window, self.current_simulator
                    
                    # If no match found, use the largest window
                    largest_window = max(fullscreen_windows, key=lambda w: w.width * w.height)
                    self.is_fullscreen = True
                    # Try to determine simulator type based on window size/position
                    if largest_window.width == 1920 and largest_window.height == 1080:
                        return largest_window, "E6"  # Default to E6 for 1080p
                    else:
                        return largest_window, "GSPro"  # Default to GSPro for other resolutions

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

        if self.is_fullscreen:
            # For fullscreen, capture the entire screen
            monitors = self.sct.monitors
            if len(monitors) > 1:
                # If multiple monitors, try to find the one with the simulator
                for monitor in monitors[1:]:  # Skip the primary monitor
                    if (self.window.left >= monitor["left"] and 
                        self.window.top >= monitor["top"] and
                        self.window.left + self.window.width <= monitor["left"] + monitor["width"] and
                        self.window.top + self.window.height <= monitor["top"] + monitor["height"]):
                        return monitor
            # If not found or only one monitor, use the primary monitor
            return monitors[0]
        else:
            # For windowed mode, use window coordinates
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
            
            # For fullscreen, try to detect and crop to the actual game area
            if self.is_fullscreen:
                frame = self._crop_fullscreen_frame(frame)
            
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

    def _crop_fullscreen_frame(self, frame: np.ndarray) -> np.ndarray:
        """Attempt to crop fullscreen frame to the actual game area."""
        try:
            # Convert to grayscale for processing
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            
            # Apply threshold to find dark areas (usually UI elements)
            _, thresh = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
            
            # Find contours
            contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if contours:
                # Find the largest contour that's not the entire frame
                max_area = frame.shape[0] * frame.shape[1] * 0.95  # 95% of frame
                valid_contours = [c for c in contours if cv2.contourArea(c) < max_area]
                
                if valid_contours:
                    largest = max(valid_contours, key=cv2.contourArea)
                    x, y, w, h = cv2.boundingRect(largest)
                    
                    # Add some padding
                    padding = 10
                    x = max(0, x - padding)
                    y = max(0, y - padding)
                    w = min(frame.shape[1] - x, w + 2 * padding)
                    h = min(frame.shape[0] - y, h + 2 * padding)
                    
                    return frame[y:y+h, x:x+w]
            
            return frame
        except Exception as e:
            print(f"Error cropping fullscreen frame: {e}")
            return frame

    def get_current_simulator(self) -> Optional[str]:
        """Return the currently detected simulator type."""
        return self.current_simulator

    def is_simulator_fullscreen(self) -> bool:
        """Return whether the simulator is running in fullscreen mode."""
        return self.is_fullscreen

    def cleanup(self):
        """Clean up resources."""
        self.sct.close() 