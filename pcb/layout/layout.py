#!/usr/bin/env python3
"""
KiCad Footprint Position Calculator for Split Column Staggered Keyboard

Calculates positions for switch footprints in a split keyboard layout.
Default specifications:
- 3 rows, 5 columns per half (configurable)
- Footprint size: 17.5mm x 16.5mm
- Spacing: 0.5mm between keys
- Column staggered layout (configurable)
"""

import math
from typing import List, Tuple, Dict


class KeyboardLayoutConfig:
    """Configuration for keyboard layout calculations."""
    def __init__(self, origin_x: float = 0.0, origin_y: float = 0.0, 
                 num_rows: int = 3, column_stagger: Dict[int, float] = None,
                 num_thumb_keys: int = 3, thumb_arc_col_start: int = 3):
        """
        Initialize the keyboard layout configuration.
        
        Args:
            origin_x: X coordinate of the origin in mm
            origin_y: Y coordinate of the origin in mm
            num_rows: Number of rows in the keyboard layout
            column_stagger: Dictionary mapping column index to stagger offset in mm
                          If None, uses default column stagger values
            num_thumb_keys: Number of thumb keys per half (default: 3)
            thumb_arc_col_start: Column number under which the thumb arc starts (default: 2)
        """
        self.origin_x = origin_x
        self.origin_y = origin_y
        self.split_separation = 90.0  # mm - separation between left and right halves
        
        # Layout dimensions
        self.num_rows = num_rows
        
        # Column stagger offsets (in mm) - adjust these for desired stagger
        self.column_stagger = column_stagger.copy() if column_stagger else {}
        
        self.num_cols = len(self.column_stagger)
        
        # Thumb key configuration
        self.num_thumb_keys = num_thumb_keys
        self.thumb_arc_col_start = thumb_arc_col_start
        
        # Footprint dimensions in mm
        self.footprint_width = 17.5
        self.footprint_height = 16.5
        
        # Diode dimensions in mm
        self.diode_width = 1.5
        self.diode_height = 5.2
        
        # Diode offset from switch center in mm
        self.diode_offset_x = -6.5
        self.diode_offset_y = -5.2
        
        # Spacing between keys in mm
        self.key_spacing = 0.5
        
        # Total spacing between key centers
        self.x_pitch = self.footprint_width + self.key_spacing
        self.y_pitch = self.footprint_height + self.key_spacing
        
        # Thumb arc configuration
        self.thumb_arc_radius = 56.65  # mm - radius of the thumb arc
        self.thumb_arc_start_angle = -90  # degrees - starting angle for thumb arc
        self.thumb_arc_end_angle = -48.0  # degrees - ending angle for thumb arc
        self.thumb_offset_x = 0  # mm - horizontal offset from center of bottom key in thumb_arc_col_start
        self.thumb_offset_y = 7.05+self.y_pitch # mm - vertical offset from center of bottom key in thumb_arc_col_start


class KeyboardLayoutCalculator:
    """Static methods for calculating keyboard layout positions."""
    
    @staticmethod
    def calculate_left_position(config: KeyboardLayoutConfig, row: int, col: int) -> Tuple[float, float]:
        """
        Calculate the center position of a key at given row and column for the left half.
        
        Args:
            config: KeyboardLayoutConfig instance with layout parameters
            row: Row number (0 to num_rows-1)
            col: Column number (0 to num_cols-1)
            
        Returns:
            Tuple of (x, y) coordinates in mm (center of footprint)
        """
        # Base position calculation (top-left corner)
        x = config.origin_x + (col * config.x_pitch)
        y = config.origin_y + (row * config.y_pitch)
        
        # Apply column stagger by summing the stagger offsets up to this column
        for c in range(col + 1):
            y += config.column_stagger[c]
        
        # Convert to center coordinates
        x_center = x + (config.footprint_width / 2)
        y_center = y + (config.footprint_height / 2)
        
        return (x_center, y_center)
    
    @staticmethod
    def calculate_thumb_position(config: KeyboardLayoutConfig, thumb_index: int, is_left: bool = True) -> Tuple[float, float, float]:
        """
        Calculate the position and rotation of a thumb key in an arc.
        
        Args:
            config: KeyboardLayoutConfig instance with layout parameters
            thumb_index: Index of the thumb key (0 to num_thumb_keys-1)
            is_left: True for left half, False for right half
            
        Returns:
            Tuple of (x, y, rotation) coordinates in mm and degrees
            rotation is in degrees (positive is counterclockwise)
        """
        # Calculate angle for this thumb key in the arc
        if config.num_thumb_keys == 1:
            angle = 0.0
        else:
            angle_range = config.thumb_arc_end_angle - config.thumb_arc_start_angle
            angle = config.thumb_arc_start_angle + (thumb_index * angle_range / (config.num_thumb_keys - 1))
        
        # Convert angle to radians for calculation
        angle_rad = math.radians(angle)
        
        # Calculate position on the arc
        arc_x = config.thumb_arc_radius * math.cos(angle_rad)
        arc_y = config.thumb_arc_radius * math.sin(angle_rad)
        
        # Find the reference point (center of bottom key in thumb_arc_col_start column)
        ref_x, ref_y = KeyboardLayoutCalculator.calculate_left_position(config, config.num_rows - 1, config.thumb_arc_col_start)
        
        # Calculate arc origin: X stays at reference, Y is reference plus arc radius (below the reference)
        arc_origin_x = ref_x + config.thumb_offset_x
        arc_origin_y = ref_y + config.thumb_offset_y + config.thumb_arc_radius
        
        # Apply arc position relative to arc origin
        thumb_x = arc_origin_x + arc_x
        thumb_y = arc_origin_y + arc_y
        
        # Key rotation follows the arc tangent (perpendicular to radius)
        # Add 90 degrees to make keys tangent to the arc
        rotation = angle + 90.0
        
        # For right half, we'll mirror this in the mirror_thumb_position method
        
        return (thumb_x, thumb_y, rotation)
    
    @staticmethod
    def mirror_thumb_position(config: KeyboardLayoutConfig, left_x: float, left_y: float, left_rotation: float) -> Tuple[float, float, float]:
        """
        Mirror a left thumb position to create the corresponding right thumb position.
        
        Args:
            config: KeyboardLayoutConfig instance with layout parameters
            left_x: X coordinate from left half (center of footprint)
            left_y: Y coordinate from left half (center of footprint)
            left_rotation: Rotation from left half in degrees
            
        Returns:
            Tuple of (x, y, rotation) coordinates for the mirrored position
        """
        # Use the same mirroring logic as main keys for X coordinate
        left_half_width = (config.num_cols - 1) * config.x_pitch + config.footprint_width
        separation = config.split_separation
        
        # Mirror the x coordinate
        right_x = left_half_width + separation + (left_half_width - left_x)
        
        # Y coordinate stays the same
        right_y = left_y
        
        # Mirror the rotation (negate the angle)
        right_rotation = -left_rotation
        
        return (right_x, right_y, right_rotation)
    
    @staticmethod
    def mirror_position(config: KeyboardLayoutConfig, left_x: float, left_y: float) -> Tuple[float, float]:
        """
        Mirror a left half position to create the corresponding right half position.
        
        Args:
            config: KeyboardLayoutConfig instance with layout parameters
            left_x: X coordinate from left half (center of footprint)
            left_y: Y coordinate from left half (center of footprint)
            
        Returns:
            Tuple of (x, y) coordinates for the mirrored position (center of footprint)
        """
        # Calculate the rightmost position of left half (center-based)
        left_half_width = (config.num_cols - 1) * config.x_pitch + config.footprint_width
        separation = config.split_separation # mm separation between halves
        
        # Mirror the x coordinate (accounting for center positioning)
        right_x = left_half_width + separation + (left_half_width - left_x)
        
        return (right_x, left_y)
    
    @staticmethod
    def calculate_diode_position(config: KeyboardLayoutConfig, switch_x: float, switch_y: float, switch_rotation: float = 0.0) -> Tuple[float, float, float]:
        """
        Calculate the diode position relative to a switch position.
        
        Args:
            config: KeyboardLayoutConfig instance with layout parameters
            switch_x: X coordinate of the switch center
            switch_y: Y coordinate of the switch center
            switch_rotation: Rotation of the switch in degrees (for thumb keys)
            
        Returns:
            Tuple of (x, y, rotation) coordinates for the diode center
        """
        if abs(switch_rotation) < 0.1:  # No rotation for main keys
            diode_x = switch_x + config.diode_offset_x
            diode_y = switch_y + config.diode_offset_y
            diode_rotation = 0.0
        else:  # Rotated thumb keys - apply rotation to offset
            # Convert rotation to radians
            rot_rad = math.radians(switch_rotation)
            
            # Apply rotation to the offset vector
            rotated_offset_x = (config.diode_offset_x * math.cos(rot_rad) - 
                               config.diode_offset_y * math.sin(rot_rad))
            rotated_offset_y = (config.diode_offset_x * math.sin(rot_rad) + 
                               config.diode_offset_y * math.cos(rot_rad))
            
            diode_x = switch_x + rotated_offset_x
            diode_y = switch_y + rotated_offset_y
            diode_rotation = switch_rotation
        
        return (diode_x, diode_y, diode_rotation)
    
    @staticmethod
    def generate_all_positions(config: KeyboardLayoutConfig) -> Dict[str, Dict[str, List[Tuple[str, float, float, float]]]]:
        """
        Generate all key and diode positions for both halves of the keyboard.
        Both halves numbered top-left to bottom-right (row by row, left to right).
        Includes main keys, thumb keys, and their corresponding diodes.
        
        Args:
            config: KeyboardLayoutConfig instance with layout parameters
        
        Returns:
            Dictionary with 'left' and 'right' keys, each containing 'switches' and 'diodes'
            with lists of (component_name, x, y, rotation) tuples
        """
        positions = {
            'left': {'switches': [], 'diodes': []}, 
            'right': {'switches': [], 'diodes': []}
        }
        
        # Generate left half main key positions (numbered row by row, left to right)
        switch_num = 1
        for row in range(config.num_rows):
            for col in range(config.num_cols):
                x, y = KeyboardLayoutCalculator.calculate_left_position(config, row, col)
                key_name = f"SWL{switch_num}"
                diode_name = f"DL{switch_num}"
                
                # Add switch position
                positions['left']['switches'].append((key_name, x, y, 0.0))  # Main keys have 0 rotation
                
                # Calculate and add diode position
                diode_x, diode_y, diode_rotation = KeyboardLayoutCalculator.calculate_diode_position(config, x, y, 0.0)
                positions['left']['diodes'].append((diode_name, diode_x, diode_y, diode_rotation))
                
                switch_num += 1
        
        # Generate left half thumb key positions
        for thumb_idx in range(config.num_thumb_keys):
            x, y, rotation = KeyboardLayoutCalculator.calculate_thumb_position(config, thumb_idx, is_left=True)
            key_name = f"SWL{switch_num + thumb_idx}"
            diode_name = f"DL{switch_num + thumb_idx}"
            
            # Add switch position
            positions['left']['switches'].append((key_name, x, y, rotation))
            
            # Calculate and add diode position
            diode_x, diode_y, diode_rotation = KeyboardLayoutCalculator.calculate_diode_position(config, x, y, rotation)
            positions['left']['diodes'].append((diode_name, diode_x, diode_y, diode_rotation))
        
        # Generate right half main key positions by mirroring left positions
        # Numbered row by row, left to right from the right half perspective
        switch_num = 1
        for row in range(config.num_rows):
            for col in range(config.num_cols - 1, -1, -1):  # Reverse column order
                # Find the corresponding left position
                left_x, left_y = KeyboardLayoutCalculator.calculate_left_position(config, row, col)
                # Mirror it to get right position
                right_x, right_y = KeyboardLayoutCalculator.mirror_position(config, left_x, left_y)
                key_name = f"SWR{switch_num}"
                diode_name = f"DR{switch_num}"
                
                # Add switch position
                positions['right']['switches'].append((key_name, right_x, right_y, 0.0))  # Main keys have 0 rotation
                
                # Calculate and add diode position
                diode_x, diode_y, diode_rotation = KeyboardLayoutCalculator.calculate_diode_position(config, right_x, right_y, 0.0)
                positions['right']['diodes'].append((diode_name, diode_x, diode_y, diode_rotation))
                
                switch_num += 1
        
        # Generate right half thumb key positions by mirroring left thumb positions
        for thumb_idx in range(config.num_thumb_keys):
            left_x, left_y, left_rotation = KeyboardLayoutCalculator.calculate_thumb_position(config, thumb_idx, is_left=True)
            right_x, right_y, right_rotation = KeyboardLayoutCalculator.mirror_thumb_position(config, left_x, left_y, left_rotation)
            key_name = f"SWR{switch_num + thumb_idx}"
            diode_name = f"DR{switch_num + thumb_idx}"
            
            # Add switch position
            positions['right']['switches'].append((key_name, right_x, right_y, right_rotation))
            
            # Calculate and add diode position
            diode_x, diode_y, diode_rotation = KeyboardLayoutCalculator.calculate_diode_position(config, right_x, right_y, right_rotation)
            positions['right']['diodes'].append((diode_name, diode_x, diode_y, diode_rotation))
        
        return positions