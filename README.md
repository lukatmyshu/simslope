# E6 TruGolf Grass Slope Detection System

A Python application that captures the E6 TruGolf golf simulator screen, detects the grass/playing surface, and calculates the slope angle to help with shot planning.

## Features

- Real-time grass detection and slope analysis
- Multiple slope detection methods for improved accuracy
- Visual feedback with slope direction indicators
- Confidence scoring for detection reliability
- Minimal impact on E6 simulator performance

## Requirements

- Python 3.7 or higher
- E6 TruGolf simulator running in windowed mode
- Required Python packages (see requirements.txt)

## Installation

1. Clone this repository:
```bash
git clone <repository-url>
cd e6-slope-detection
```

2. Create a virtual environment (recommended):
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install required packages:
```bash
pip install -r requirements.txt
```

## Usage

1. Start the E6 TruGolf simulator and ensure it's running in windowed mode.

2. Run the slope detection system:
```bash
python main.py
```

3. The system will:
   - Automatically detect the E6 window
   - Begin capturing and analyzing the golf course view
   - Display real-time slope information in a separate window

4. Controls:
   - Press 'q' to quit the application
   - The display window can be resized as needed

## Configuration

You can adjust various parameters in `config.py`:
- Color ranges for grass detection
- Detection sensitivity
- Performance settings
- Display options

## Troubleshooting

1. If the E6 window is not detected:
   - Ensure E6 is running in windowed mode
   - Check that the window title matches the pattern in config.py

2. If grass detection is unreliable:
   - Adjust the HSV color ranges in config.py
   - Ensure good lighting conditions
   - Try different courses if available

3. If performance is slow:
   - Reduce the capture resolution in config.py
   - Adjust the processing downscale factor
   - Close other resource-intensive applications

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 
