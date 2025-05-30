"""
Grass detection module for E6 TruGolf Grass Slope Detection System.
Handles grass segmentation and validation.
"""

import cv2
import numpy as np
from typing import Tuple, Optional
import config

class GrassDetector:
    def __init__(self):
        self.kernel = np.ones(config.MORPH_KERNEL_SIZE, np.uint8)
        # GSPro-specific: Additional color ranges for different grass types
        self.grass_ranges = [
            (config.GRASS_HSV_LOWER, config.GRASS_HSV_UPPER),  # Standard green
            ((35, 30, 30), (45, 255, 255)),  # Light green
            ((50, 30, 30), (70, 255, 255)),  # Dark green
        ]

    def segment_grass(self, frame: np.ndarray) -> Tuple[np.ndarray, float]:
        """
        Extract grass regions using color and texture analysis.
        Returns the grass mask and confidence score.
        """
        # Convert to HSV color space
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        # Create combined mask for all grass color ranges
        combined_mask = np.zeros(frame.shape[:2], dtype=np.uint8)
        for lower, upper in self.grass_ranges:
            mask = cv2.inRange(hsv, lower, upper)
            combined_mask = cv2.bitwise_or(combined_mask, mask)
        
        # Clean up the mask
        mask = self.clean_grass_mask(combined_mask)
        
        # Calculate confidence based on grass coverage
        confidence = self.validate_grass_region(mask)
        
        return mask, confidence

    def clean_grass_mask(self, mask: np.ndarray) -> np.ndarray:
        """Remove noise and improve grass region quality."""
        # Apply Gaussian blur to reduce noise
        mask = cv2.GaussianBlur(mask, config.BLUR_KERNEL_SIZE, 0)
        
        # Apply morphological operations
        mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, self.kernel)
        mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, self.kernel)
        
        # Threshold to get binary mask
        _, mask = cv2.threshold(mask, 127, 255, cv2.THRESH_BINARY)
        
        return mask

    def validate_grass_region(self, mask: np.ndarray) -> float:
        """
        Ensure we have enough grass pixels for reliable detection.
        Returns confidence score between 0 and 1.
        """
        # Count grass pixels
        grass_pixels = np.count_nonzero(mask)
        total_pixels = mask.shape[0] * mask.shape[1]
        
        # Calculate grass coverage ratio
        coverage = grass_pixels / total_pixels
        
        # Calculate confidence based on coverage
        if grass_pixels < config.MIN_GRASS_PIXELS:
            return 0.0
        
        # Higher confidence for moderate coverage (not too sparse, not too dense)
        if 0.2 <= coverage <= 0.8:
            return 1.0
        else:
            # Lower confidence for extreme coverage values
            return 0.5

    def get_grass_contours(self, mask: np.ndarray) -> list:
        """Get the contours of grass regions."""
        contours, _ = cv2.findContours(
            mask, 
            cv2.RETR_EXTERNAL, 
            cv2.CHAIN_APPROX_SIMPLE
        )
        return contours

    def get_largest_grass_region(self, mask: np.ndarray) -> Optional[np.ndarray]:
        """Get the mask of the largest continuous grass region."""
        contours = self.get_grass_contours(mask)
        if not contours:
            return None
            
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Create a mask for the largest region
        largest_mask = np.zeros_like(mask)
        cv2.drawContours(largest_mask, [largest_contour], -1, 255, -1)
        
        return largest_mask 