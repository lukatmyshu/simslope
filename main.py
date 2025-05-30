"""
Main application for E6 TruGolf and GSPro Grass Slope Detection System.
Integrates all components and handles the main processing loop.
"""

import cv2
import numpy as np
import time
import sys
import platform
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
        self.frame_count = 0
        self.last_fps_time = time.time()
        self.fps = 0

    def calculate_fps(self):
        """Calculate and display FPS."""
        self.frame_count += 1
        current_time = time.time()
        if current_time - self.last_fps_time >= 1.0:
            self.fps = self.frame_count
            self.frame_count = 0
            self.last_fps_time = current_time

    def handle_windows_specific(self):
        """Handle Windows-specific initialization."""
        if platform.system() == "Windows":
            # Set process priority to high
            try:
                import psutil
                process = psutil.Process()
                process.nice(psutil.HIGH_PRIORITY_CLASS)
            except:
                pass

            # Configure OpenCV for Windows
            cv2.setUseOptimized(True)
            cv2.ocl.setUseOpenCL(True)

    def run(self):
        """Main application loop."""
        self.running = True
        print("Starting Golf Slope Detection System...")
        print("Press 'q' to quit")
        print("Waiting for E6 TruGolf or GSPro window...")

        # Handle Windows-specific setup
        self.handle_windows_specific()

        # Initialize window
        cv2.namedWindow(self.display.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.display.window_name, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)

        while self.running:
            try:
                # Capture screen
                frame = self.screen_capture.capture_golf_view()
                if frame is None:
                    time.sleep(0.1)
                    continue

                # Get current simulator type
                simulator = self.screen_capture.get_current_simulator()
                if simulator and self.frame_count == 0:  # Only print on first frame
                    print(f"Detected simulator: {simulator}")

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

                # Calculate FPS
                self.calculate_fps()

                # Create and show overlay
                overlay = self.display.create_overlay(
                    frame,
                    grass_mask,
                    slope_angle,
                    side_slope,
                    confidence,
                    simulator
                )

                # Add FPS to display
                cv2.putText(
                    overlay,
                    f"FPS: {self.fps}",
                    (10, overlay.shape[0] - 20),
                    cv2.FONT_HERSHEY_SIMPLEX,
                    0.7,
                    (255, 255, 255),
                    2
                )

                # Show frame
                self.display.show_frame(overlay)

                # Check for quit command
                key = cv2.waitKey(1) & 0xFF
                if key == ord('q'):
                    self.running = False
                elif key == ord('r'):  # Reset window position
                    cv2.moveWindow(self.display.window_name, 0, 0)

            except Exception as e:
                print(f"Error in main loop: {e}")
                time.sleep(0.1)  # Prevent CPU spinning on error
                continue

    def cleanup(self):
        """Clean up resources."""
        try:
            self.screen_capture.cleanup()
            self.display.cleanup()
        except Exception as e:
            print(f"Error during cleanup: {e}")

def main():
    app = SlopeDetectionApp()
    try:
        app.run()
    except KeyboardInterrupt:
        print("\nShutting down...")
    except Exception as e:
        print(f"\nUnexpected error: {e}")
    finally:
        app.cleanup()

if __name__ == "__main__":
    main() 