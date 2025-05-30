"""
UI display module for E6 TruGolf and GSPro Grass Slope Detection System.
Handles real-time display and visualization.
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import config

class DisplayUI:
    def __init__(self):
        self.window_name = "Golf Slope Detection"
        cv2.namedWindow(self.window_name, cv2.WINDOW_NORMAL)
        cv2.resizeWindow(self.window_name, config.DISPLAY_WIDTH, config.DISPLAY_HEIGHT)

    def create_overlay(self, frame: np.ndarray, grass_mask: np.ndarray,
                      slope_angle: float, side_slope: float,
                      confidence: float, simulator: Optional[str] = None) -> np.ndarray:
        """Create visualization overlay with slope information."""
        # Create a copy of the frame for drawing
        overlay = frame.copy()
        
        # Create colored mask for grass regions
        grass_overlay = np.zeros_like(frame)
        grass_overlay[grass_mask > 0] = [0, 255, 0]  # Green for grass
        
        # Blend the grass overlay with the original frame
        cv2.addWeighted(
            grass_overlay,
            config.OVERLAY_ALPHA,
            overlay,
            1 - config.OVERLAY_ALPHA,
            0,
            overlay
        )
        
        # Draw slope direction indicator
        self._draw_slope_indicator(overlay, slope_angle, side_slope)
        
        # Add text information
        self._add_text_info(overlay, slope_angle, side_slope, confidence, simulator)
        
        return overlay

    def _draw_slope_indicator(self, overlay: np.ndarray,
                            slope_angle: float, side_slope: float):
        """Draw visual indicator for slope direction."""
        height, width = overlay.shape[:2]
        center = (width // 2, height // 2)
        
        # Calculate arrow length based on slope angle
        arrow_length = min(width, height) * 0.3
        
        # Calculate arrow direction
        angle_rad = np.radians(slope_angle)
        dx = arrow_length * np.sin(angle_rad)
        dy = arrow_length * np.cos(angle_rad)
        
        # Draw main slope arrow
        end_point = (
            int(center[0] + dx),
            int(center[1] + dy)
        )
        cv2.arrowedLine(
            overlay,
            center,
            end_point,
            (0, 0, 255),  # Red color
            3,
            tipLength=0.2
        )
        
        # Draw side slope indicator if significant
        if abs(side_slope) > 1.0:
            side_angle_rad = np.radians(side_slope)
            side_dx = arrow_length * 0.5 * np.sin(side_angle_rad)
            side_dy = arrow_length * 0.5 * np.cos(side_angle_rad)
            
            side_end = (
                int(center[0] + side_dx),
                int(center[1] + side_dy)
            )
            cv2.arrowedLine(
                overlay,
                center,
                side_end,
                (255, 0, 0),  # Blue color
                2,
                tipLength=0.2
            )

    def _add_text_info(self, overlay: np.ndarray, slope_angle: float,
                      side_slope: float, confidence: float,
                      simulator: Optional[str] = None):
        """Add text information to the overlay."""
        # Format text information
        simulator_text = f"Simulator: {simulator if simulator else 'Not Detected'}"
        slope_text = f"Slope: {slope_angle:.1f}°"
        side_text = f"Side Slope: {side_slope:.1f}°"
        conf_text = f"Confidence: {confidence*100:.0f}%"
        
        # Add text to overlay
        y_offset = 30
        cv2.putText(
            overlay,
            simulator_text,
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )
        
        y_offset += 40
        cv2.putText(
            overlay,
            slope_text,
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )
        
        y_offset += 40
        cv2.putText(
            overlay,
            side_text,
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )
        
        y_offset += 40
        cv2.putText(
            overlay,
            conf_text,
            (10, y_offset),
            cv2.FONT_HERSHEY_SIMPLEX,
            1,
            (255, 255, 255),
            2
        )

    def show_frame(self, frame: np.ndarray):
        """Display the frame in the window."""
        cv2.imshow(self.window_name, frame)

    def cleanup(self):
        """Clean up resources."""
        cv2.destroyAllWindows() 