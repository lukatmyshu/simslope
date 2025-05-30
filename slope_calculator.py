"""
Slope calculator module for E6 TruGolf Grass Slope Detection System.
Implements multiple methods for slope detection.
"""

import cv2
import numpy as np
from typing import Tuple, List, Optional
import config

class SlopeCalculator:
    def __init__(self):
        self.method_weights = {
            'horizon': 0.4,
            'texture': 0.3,
            'perspective': 0.3
        }

    def detect_horizon_line(self, grass_mask: np.ndarray, frame: np.ndarray) -> Tuple[float, float]:
        """
        Find horizon using edge detection and Hough transform.
        Returns (slope_angle, confidence).
        """
        # Apply Canny edge detection
        edges = cv2.Canny(grass_mask, *config.EDGE_THRESHOLD)
        
        # Find lines using Hough transform
        lines = cv2.HoughLinesP(
            edges,
            rho=1,
            theta=np.pi/180,
            threshold=config.HOUGH_THRESHOLD,
            minLineLength=100,
            maxLineGap=10
        )
        
        if lines is None:
            return 0.0, 0.0
            
        # Calculate angles for all lines
        angles = []
        for line in lines:
            x1, y1, x2, y2 = line[0]
            if x2 - x1 != 0:  # Avoid division by zero
                angle = np.arctan((y2 - y1) / (x2 - x1)) * 180 / np.pi
                angles.append(angle)
        
        if not angles:
            return 0.0, 0.0
            
        # Calculate median angle and confidence
        median_angle = np.median(angles)
        confidence = min(1.0, len(angles) / 10)  # More lines = higher confidence
        
        return median_angle, confidence

    def calculate_texture_gradient(self, grass_region: np.ndarray) -> Tuple[float, float]:
        """
        Analyze grass texture for slope information.
        Returns (slope_angle, confidence).
        """
        # Calculate gradients using Sobel operators
        sobelx = cv2.Sobel(grass_region, cv2.CV_64F, 1, 0, ksize=3)
        sobely = cv2.Sobel(grass_region, cv2.CV_64F, 0, 1, ksize=3)
        
        # Calculate gradient magnitude and direction
        magnitude = np.sqrt(sobelx**2 + sobely**2)
        direction = np.arctan2(sobely, sobelx) * 180 / np.pi
        
        # Calculate weighted average direction
        valid_mask = magnitude > np.mean(magnitude)
        if not np.any(valid_mask):
            return 0.0, 0.0
            
        weighted_direction = np.average(
            direction[valid_mask],
            weights=magnitude[valid_mask]
        )
        
        # Calculate confidence based on gradient strength
        confidence = min(1.0, np.mean(magnitude[valid_mask]) / 255)
        
        return weighted_direction, confidence

    def compute_perspective_slope(self, grass_mask: np.ndarray) -> Tuple[float, float]:
        """
        Analyze perspective for slope information.
        Returns (slope_angle, confidence).
        """
        # Find contours of grass regions
        contours, _ = cv2.findContours(
            grass_mask,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        if not contours:
            return 0.0, 0.0
            
        # Find the largest contour
        largest_contour = max(contours, key=cv2.contourArea)
        
        # Fit a rectangle to the contour
        rect = cv2.minAreaRect(largest_contour)
        angle = rect[2]
        
        # Calculate confidence based on contour area and shape
        area = cv2.contourArea(largest_contour)
        confidence = min(1.0, area / (grass_mask.shape[0] * grass_mask.shape[1] * 0.1))
        
        return angle, confidence

    def compute_slope_angle(self, grass_mask: np.ndarray, frame: np.ndarray) -> Tuple[float, float, float]:
        """
        Combine multiple methods to calculate final slope angle.
        Returns (slope_angle, side_slope, confidence).
        """
        # Get results from all methods
        horizon_angle, horizon_conf = self.detect_horizon_line(grass_mask, frame)
        texture_angle, texture_conf = self.calculate_texture_gradient(grass_mask)
        perspective_angle, perspective_conf = self.compute_perspective_slope(grass_mask)
        
        # Weight the results
        weighted_angle = (
            horizon_angle * self.method_weights['horizon'] * horizon_conf +
            texture_angle * self.method_weights['texture'] * texture_conf +
            perspective_angle * self.method_weights['perspective'] * perspective_conf
        )
        
        # Calculate overall confidence
        total_confidence = (
            horizon_conf * self.method_weights['horizon'] +
            texture_conf * self.method_weights['texture'] +
            perspective_conf * self.method_weights['perspective']
        )
        
        # Calculate side slope (left/right tilt)
        side_slope = np.arctan2(
            np.sin(weighted_angle * np.pi / 180),
            np.cos(weighted_angle * np.pi / 180)
        ) * 180 / np.pi
        
        # Clamp angles to expected ranges
        weighted_angle = np.clip(weighted_angle, -config.MAX_SLOPE_ANGLE, config.MAX_SLOPE_ANGLE)
        side_slope = np.clip(side_slope, -config.MAX_SIDE_SLOPE, config.MAX_SIDE_SLOPE)
        
        return weighted_angle, side_slope, total_confidence 