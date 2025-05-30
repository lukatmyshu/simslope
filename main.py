"""
Main application for E6 TruGolf Grass Slope Detection System.
Integrates all components and handles the main processing loop.
"""

import cv2
import numpy as np
import time
from screen_capture import ScreenCapture
from grass_detector import GrassDetector
from slope_calculator import SlopeCalculator
from ui_display import DisplayUI
import config

class SlopeDetectionApp:
    def __init__(self):
        self.screen_capture = ScreenCapture()
        self.grass_detector = GrassDetector()
        self.slope_calculator = SlopeCalculator()
        self.display = DisplayUI()
        self.running = False

    def run(self):
        """Main application loop."""
        self.running = True
        print("Starting E6 Slope Detection System...")
        print("Press 'q' to quit")

        while self.running:
            # Capture screen
            frame = self.screen_capture.capture_golf_view()
            if frame is None:
                time.sleep(0.1)
                continue

            # Detect grass
            grass_mask, grass_confidence = self.grass_detector.segment_grass(frame)
            
            if grass_confidence < config.MIN_CONFIDENCE:
                # Show original frame with low confidence message
                self.display.show_frame(frame)
                continue

            # Calculate slope
            slope_angle, side_slope, confidence = self.slope_calculator.compute_slope_angle(
                grass_mask, frame
            )

            # Create and show overlay
            overlay = self.display.create_overlay(
                frame,
                grass_mask,
                slope_angle,
                side_slope,
                confidence
            )
            self.display.show_frame(overlay)

            # Check for quit command
            if cv2.waitKey(1) & 0xFF == ord('q'):
                self.running = False

    def cleanup(self):
        """Clean up resources."""
        self.screen_capture.cleanup()
        self.display.cleanup()

def main():
    app = SlopeDetectionApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        app.cleanup()

if __name__ == "__main__":
    main() 