"""
TurtleBot Soccer Robot Package

This package contains all modules for the soccer-playing TurtleBot robot.

Modules:
- hsv_filter: Handles color filtering in HSV space
- imagepip_processor: Processes camera images
- motor_driver: Controls robot movements
- path_info: Stores path planning information
- scene_info: Contains scene analysis results
- search_engine: Determines robot state
- visualizer: Provides visualization tools
"""

__all__ = [
    'hsv_filter',
    'image_processor',
    'motor_driver',
    'path_info',
    'scene_info',
    'search_engine',
    'visualizer'
]

__version__ = '1.0.0'
