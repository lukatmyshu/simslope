"""
Configuration settings for the E6 TruGolf Grass Slope Detection System.
"""

# Color ranges for grass detection (HSV)
GRASS_HSV_LOWER = (40, 30, 30)
GRASS_HSV_UPPER = (80, 255, 255)

# Detection sensitivity
EDGE_THRESHOLD = (50, 150)  # Canny edge detection
HOUGH_THRESHOLD = 100       # Line detection threshold
MIN_GRASS_PIXELS = 5000     # Minimum grass area needed

# Performance settings
CAPTURE_FPS = 12
PROCESSING_DOWNSCALE = 0.5  # Scale factor for faster processing

# Window detection settings
WINDOW_TITLE_PATTERN = "E6 TruGolf"  # Pattern to match E6 window title
UI_MARGIN_TOP = 50    # Pixels to skip from top of window
UI_MARGIN_BOTTOM = 50 # Pixels to skip from bottom of window

# Slope detection parameters
MAX_SLOPE_ANGLE = 15  # Maximum expected slope angle in degrees
MAX_SIDE_SLOPE = 10   # Maximum expected side slope in degrees
MIN_CONFIDENCE = 0.5  # Minimum confidence threshold (0-1)

# Processing settings
BLUR_KERNEL_SIZE = (5, 5)  # Gaussian blur kernel size
MORPH_KERNEL_SIZE = (5, 5) # Morphological operation kernel size

# Display settings
DISPLAY_WIDTH = 800   # Width of the display window
DISPLAY_HEIGHT = 600  # Height of the display window
OVERLAY_ALPHA = 0.5   # Transparency of the overlay (0-1) 