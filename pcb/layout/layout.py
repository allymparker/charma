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


class KeyboardLayoutCalculator:
    def __init__(self, origin_x: float = 0.0, origin_y: float = 0.0, 
                 num_rows: int = 3, column_stagger: Dict[int, float] = None,
                 num_thumb_keys: int = 3, thumb_arc_col_start: int = 3):
        """
        Initialize the keyboard layout calculator.
        
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
        self.split_separation = 60.0  # mm - separation between left and right halves
        
        # Layout dimensions
        self.num_rows = num_rows
        
        # Column stagger offsets (in mm) - adjust these for desired stagger
        self.column_stagger = column_stagger.copy()
        
        self.num_cols = len(self.column_stagger)
        
        # Thumb key configuration
        self.num_thumb_keys = num_thumb_keys
        self.thumb_arc_col_start = thumb_arc_col_start
        
        # Footprint dimensions in mm
        self.footprint_width = 17.5
        self.footprint_height = 16.5
        
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


        
    def calculate_left_position(self, row: int, col: int) -> Tuple[float, float]:
        """
        Calculate the center position of a key at given row and column for the left half.
        
        Args:
            row: Row number (0 to num_rows-1)
            col: Column number (0 to num_cols-1)
            
        Returns:
            Tuple of (x, y) coordinates in mm (center of footprint)
        """
        # Base position calculation (top-left corner)
        x = self.origin_x + (col * self.x_pitch)
        y = self.origin_y + (row * self.y_pitch)
        
        # Apply column stagger by summing the stagger offsets up to this column
        for c in range(col + 1):
            y += self.column_stagger[c]
        
        # Convert to center coordinates
        x_center = x + (self.footprint_width / 2)
        y_center = y + (self.footprint_height / 2)
        
        return (x_center, y_center)
    
    def calculate_thumb_position(self, thumb_index: int, is_left: bool = True) -> Tuple[float, float, float]:
        """
        Calculate the position and rotation of a thumb key in an arc.
        
        Args:
            thumb_index: Index of the thumb key (0 to num_thumb_keys-1)
            is_left: True for left half, False for right half
            
        Returns:
            Tuple of (x, y, rotation) coordinates in mm and degrees
            rotation is in degrees (positive is counterclockwise)
        """
        # Calculate angle for this thumb key in the arc
        if self.num_thumb_keys == 1:
            angle = 0.0
        else:
            angle_range = self.thumb_arc_end_angle - self.thumb_arc_start_angle
            angle = self.thumb_arc_start_angle + (thumb_index * angle_range / (self.num_thumb_keys - 1))
        
        # Convert angle to radians for calculation
        angle_rad = math.radians(angle)
        
        # Calculate position on the arc
        arc_x = self.thumb_arc_radius * math.cos(angle_rad)
        arc_y = self.thumb_arc_radius * math.sin(angle_rad)
        
        # Find the reference point (center of bottom key in thumb_arc_col_start column)
        ref_x, ref_y = self.calculate_left_position(self.num_rows - 1, self.thumb_arc_col_start)
        
        # Calculate arc origin: X stays at reference, Y is reference plus arc radius (below the reference)
        arc_origin_x = ref_x + self.thumb_offset_x
        arc_origin_y = ref_y + self.thumb_offset_y + self.thumb_arc_radius
        
        # Apply arc position relative to arc origin
        thumb_x = arc_origin_x + arc_x
        thumb_y = arc_origin_y + arc_y
        
        # Key rotation follows the arc tangent (perpendicular to radius)
        # Add 90 degrees to make keys tangent to the arc
        rotation = angle + 90.0
        
        # For right half, we'll mirror this in the mirror_thumb_position method
        
        return (thumb_x, thumb_y, rotation)
    
    def mirror_thumb_position(self, left_x: float, left_y: float, left_rotation: float) -> Tuple[float, float, float]:
        """
        Mirror a left thumb position to create the corresponding right thumb position.
        
        Args:
            left_x: X coordinate from left half (center of footprint)
            left_y: Y coordinate from left half (center of footprint)
            left_rotation: Rotation from left half in degrees
            
        Returns:
            Tuple of (x, y, rotation) coordinates for the mirrored position
        """
        # Use the same mirroring logic as main keys for X coordinate
        left_half_width = (self.num_cols - 1) * self.x_pitch + self.footprint_width
        separation = self.split_separation
        
        # Mirror the x coordinate
        right_x = left_half_width + separation + (left_half_width - left_x)
        
        # Y coordinate stays the same
        right_y = left_y
        
        # Mirror the rotation (negate the angle)
        right_rotation = -left_rotation
        
        return (right_x, right_y, right_rotation)
    
    def mirror_position(self, left_x: float, left_y: float) -> Tuple[float, float]:
        """
        Mirror a left half position to create the corresponding right half position.
        
        Args:
            left_x: X coordinate from left half (center of footprint)
            left_y: Y coordinate from left half (center of footprint)
            
        Returns:
            Tuple of (x, y) coordinates for the mirrored position (center of footprint)
        """
        # Calculate the rightmost position of left half (center-based)
        left_half_width = (self.num_cols - 1) * self.x_pitch + self.footprint_width
        separation = self.split_separation # mm separation between halves
        
        # Mirror the x coordinate (accounting for center positioning)
        right_x = left_half_width + separation + (left_half_width - left_x)
        
        return (right_x, left_y)
    
    def generate_all_positions(self) -> Dict[str, List[Tuple[str, float, float, float]]]:
        """
        Generate all key positions for both halves of the keyboard.
        Both halves numbered top-left to bottom-right (row by row, left to right).
        Includes main keys and thumb keys.
        
        Returns:
            Dictionary with 'left' and 'right' keys containing lists of
            (key_name, x, y, rotation) tuples
        """
        positions = {'left': [], 'right': []}
        
        # Generate left half main key positions (numbered row by row, left to right)
        switch_num = 1
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                x, y = self.calculate_left_position(row, col)
                key_name = f"SWL{switch_num}"
                positions['left'].append((key_name, x, y, 0.0))  # Main keys have 0 rotation
                switch_num += 1
        
        # Generate left half thumb key positions
        for thumb_idx in range(self.num_thumb_keys):
            x, y, rotation = self.calculate_thumb_position(thumb_idx, is_left=True)
            key_name = f"SWL{switch_num + thumb_idx}"
            positions['left'].append((key_name, x, y, rotation))
        
        # Generate right half main key positions by mirroring left positions
        # Numbered row by row, left to right from the right half perspective
        switch_num = 1
        for row in range(self.num_rows):
            for col in range(self.num_cols - 1, -1, -1):  # Reverse column order
                # Find the corresponding left position
                left_x, left_y = self.calculate_left_position(row, col)
                # Mirror it to get right position
                right_x, right_y = self.mirror_position(left_x, left_y)
                key_name = f"SWR{switch_num}"
                positions['right'].append((key_name, right_x, right_y, 0.0))  # Main keys have 0 rotation
                switch_num += 1
        
        # Generate right half thumb key positions by mirroring left thumb positions
        for thumb_idx in range(self.num_thumb_keys):
            left_x, left_y, left_rotation = self.calculate_thumb_position(thumb_idx, is_left=True)
            right_x, right_y, right_rotation = self.mirror_thumb_position(left_x, left_y, left_rotation)
            key_name = f"SWR{switch_num + thumb_idx}"
            positions['right'].append((key_name, right_x, right_y, right_rotation))
        
        return positions
    
    def print_positions(self):
        """Print all key positions in a readable format."""
        positions = self.generate_all_positions()
        
        print("Keyboard Layout Positions (center coordinates in mm)")
        print("=" * 70)
        
        print("\nLeft Half:")
        print("-" * 45)
        for key_name, x, y, rotation in positions['left']:
            print(f"{key_name}: ({x:6.2f}, {y:6.2f}, {rotation:6.1f}°)")
        
        print("\nRight Half:")
        print("-" * 45)
        for key_name, x, y, rotation in positions['right']:
            print(f"{key_name}: ({x:6.2f}, {y:6.2f}, {rotation:6.1f}°)")
    
    def export_kicad_format(self, filename: str = "keyboard_positions.txt"):
        """
        Export positions in a format suitable for KiCad scripting.
        
        Args:
            filename: Output filename
        """
        positions = self.generate_all_positions()
        
        with open(filename, 'w') as f:
            f.write("# KiCad Keyboard Layout Positions\n")
            f.write("# Format: Reference X(mm) Y(mm) Rotation(degrees)\n")
            f.write("# Coordinates are center of footprint\n")
            f.write("# Rotation is in degrees (positive is counterclockwise)\n")
            f.write("# Generated by layout.py\n\n")
            
            f.write("# Left Half\n")
            for key_name, x, y, rotation in positions['left']:
                f.write(f"{key_name} {x:.3f} {y:.3f} {-rotation:.1f}\n")
            
            f.write("\n# Right Half\n")
            for key_name, x, y, rotation in positions['right']:
                f.write(f"{key_name} {x:.3f} {y:.3f} {-rotation:.1f}\n")
        
        print(f"Positions exported to {filename}")
    
    def export_csv(self, filename: str = "keyboard_positions.csv"):
        """
        Export positions in CSV format.
        
        Args:
            filename: Output CSV filename
        """
        positions = self.generate_all_positions()
        
        with open(filename, 'w') as f:
            f.write("Reference,X(mm),Y(mm),Rotation(degrees),Half\n")
            
            for key_name, x, y, rotation in positions['left']:
                f.write(f"{key_name},{x:.3f},{y:.3f},{rotation:.1f},Left\n")
            
            for key_name, x, y, rotation in positions['right']:
                f.write(f"{key_name},{x:.3f},{y:.3f},{rotation:.1f},Right\n")
        
        print(f"Positions exported to {filename}")
    
    def export_svg(self, filename: str = "keyboard_layout.svg"):
        """
        Export positions as an SVG visualization.
        
        Args:
            filename: Output SVG filename
        """
        positions = self.generate_all_positions()
        
        # Calculate SVG dimensions (accounting for center coordinates and rotation)
        all_positions = positions['left'] + positions['right']
        min_x = min(x - self.footprint_width/2 for _, x, y, r in all_positions) - 10
        max_x = max(x + self.footprint_width/2 for _, x, y, r in all_positions) + 10
        min_y = min(y - self.footprint_height/2 for _, x, y, r in all_positions) - 25  # More space at top
        max_y = max(y + self.footprint_height/2 for _, x, y, r in all_positions) + 35  # More space at bottom
        
        width = max_x - min_x
        height = max_y - min_y
        
        # Create SVG content
        svg_content = f'''<?xml version="1.0" encoding="UTF-8"?>
<svg width="{width:.1f}mm" height="{height:.1f}mm" 
     viewBox="{min_x:.1f} {min_y:.1f} {width:.1f} {height:.1f}"
     xmlns="http://www.w3.org/2000/svg">
  
  <!-- Background -->
  <rect x="{min_x:.1f}" y="{min_y:.1f}" width="{width:.1f}" height="{height:.1f}" 
        fill="#f8f9fa" stroke="none"/>
  
  <!-- Grid lines (optional) -->
  <defs>
    <pattern id="grid" width="10" height="10" patternUnits="userSpaceOnUse">
      <path d="M 10 0 L 0 0 0 10" fill="none" stroke="#e9ecef" stroke-width="0.5"/>
    </pattern>
  </defs>
  <rect x="{min_x:.1f}" y="{min_y:.1f}" width="{width:.1f}" height="{height:.1f}" 
        fill="url(#grid)"/>
  
  <!-- Title -->
  <text x="{(min_x + max_x) / 2:.1f}" y="{min_y + 8:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="4" 
        fill="#212529" font-weight="bold">
    Split Column Staggered Keyboard Layout
  </text>
  
  <!-- Left Half Label -->
  <text x="{36:.1f}" y="{min_y + 18:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="3" 
        fill="#6c757d">Left Half</text>
  
  <!-- Right Half Label -->
  <text x="{155:.1f}" y="{min_y + 18:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="3" 
        fill="#6c757d">Right Half</text>
'''
        
        # Add key rectangles and labels for left half
        for key_name, x, y, rotation in positions['left']:
            # Determine if this is a thumb key for styling
            is_thumb = key_name.startswith("SWTL")
            fill_color = "#fff3e0" if is_thumb else "#e3f2fd"
            stroke_color = "#f57c00" if is_thumb else "#1976d2"
            text_color = "#f57c00" if is_thumb else "#1976d2"
            
            if abs(rotation) < 0.1:  # No rotation for main keys
                # Convert center coordinates to top-left for rectangle drawing
                rect_x = x - self.footprint_width/2
                rect_y = y - self.footprint_height/2
                svg_content += f'''  <!-- {key_name} -->
  <rect x="{rect_x:.1f}" y="{rect_y:.1f}" 
        width="{self.footprint_width:.1f}" height="{self.footprint_height:.1f}"
        fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.1"/>
  <text x="{x:.1f}" y="{y + 1:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
        fill="{text_color}" font-weight="bold">{key_name}</text>
'''
            else:  # Rotated thumb keys
                # Convert center coordinates to top-left for rectangle drawing
                rect_x = -self.footprint_width/2
                rect_y = -self.footprint_height/2
                svg_content += f'''  <!-- {key_name} -->
  <g transform="translate({x:.1f},{y:.1f}) rotate({rotation:.1f})">
    <rect x="{rect_x:.1f}" y="{rect_y:.1f}" 
          width="{self.footprint_width:.1f}" height="{self.footprint_height:.1f}"
          fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.1"/>
    <text x="0" y="1" 
          text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
          fill="{text_color}" font-weight="bold">{key_name}</text>
  </g>
'''
        
        # Add key rectangles and labels for right half
        for key_name, x, y, rotation in positions['right']:
            # Determine if this is a thumb key for styling
            is_thumb = key_name.startswith("SWTR")
            fill_color = "#fff8e1" if is_thumb else "#f3e5f5"
            stroke_color = "#ff9800" if is_thumb else "#7b1fa2"
            text_color = "#ff9800" if is_thumb else "#7b1fa2"
            
            if abs(rotation) < 0.1:  # No rotation for main keys
                # Convert center coordinates to top-left for rectangle drawing
                rect_x = x - self.footprint_width/2
                rect_y = y - self.footprint_height/2
                svg_content += f'''  <!-- {key_name} -->
  <rect x="{rect_x:.1f}" y="{rect_y:.1f}" 
        width="{self.footprint_width:.1f}" height="{self.footprint_height:.1f}"
        fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.1"/>
  <text x="{x:.1f}" y="{y + 1:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
        fill="{text_color}" font-weight="bold">{key_name}</text>
'''
            else:  # Rotated thumb keys
                # Convert center coordinates to top-left for rectangle drawing
                rect_x = -self.footprint_width/2
                rect_y = -self.footprint_height/2
                svg_content += f'''  <!-- {key_name} -->
  <g transform="translate({x:.1f},{y:.1f}) rotate({rotation:.1f})">
    <rect x="{rect_x:.1f}" y="{rect_y:.1f}" 
          width="{self.footprint_width:.1f}" height="{self.footprint_height:.1f}"
          fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.1"/>
    <text x="0" y="1" 
          text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
          fill="{text_color}" font-weight="bold">{key_name}</text>
  </g>
'''
        
        # Add thumb arc origins
        # Calculate left thumb arc origin
        ref_x, ref_y = self.calculate_left_position(self.num_rows - 1, self.thumb_arc_col_start)
        left_origin_x = ref_x + self.thumb_offset_x
        left_origin_y = ref_y + self.thumb_offset_y + self.thumb_arc_radius
        
        # Calculate right thumb arc origin by mirroring the left origin
        right_origin_x, right_origin_y = self.mirror_position(left_origin_x, left_origin_y)
        
        # Add left thumb arc origin marker
        svg_content += f'''  <!-- Left Thumb Arc Origin -->
  <circle cx="{left_origin_x:.1f}" cy="{left_origin_y:.1f}" r="1" 
          fill="#d32f2f" stroke="#b71c1c" stroke-width="0.2"/>
  <circle cx="{left_origin_x:.1f}" cy="{left_origin_y:.1f}" r="3" 
          fill="none" stroke="#d32f2f" stroke-width="0.1" stroke-dasharray="0.5,0.5"/>
  <text x="{left_origin_x:.1f}" y="{left_origin_y - 4:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="1.5" 
        fill="#d32f2f" font-weight="bold">L-ARC</text>
'''
        
        # Add right thumb arc origin marker
        svg_content += f'''  <!-- Right Thumb Arc Origin -->
  <circle cx="{right_origin_x:.1f}" cy="{right_origin_y:.1f}" r="1" 
          fill="#d32f2f" stroke="#b71c1c" stroke-width="0.2"/>
  <circle cx="{right_origin_x:.1f}" cy="{right_origin_y:.1f}" r="3" 
          fill="none" stroke="#d32f2f" stroke-width="0.1" stroke-dasharray="0.5,0.5"/>
  <text x="{right_origin_x:.1f}" y="{right_origin_y - 4:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="1.5" 
        fill="#d32f2f" font-weight="bold">R-ARC</text>
'''
        
        # Add legend
        legend_x = min_x + 5
        legend_y = max_y - 40  # More space for expanded legend with arc origins
        svg_content += f'''
  <!-- Legend -->
  <rect x="{legend_x:.1f}" y="{legend_y:.1f}" width="55" height="27" 
        fill="white" stroke="#dee2e6" stroke-width="0.5" rx="1"/>
  
  <text x="{legend_x + 27.5:.1f}" y="{legend_y + 3:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
        fill="#212529" font-weight="bold">Legend</text>
  
  <!-- Main Keys -->
  <rect x="{legend_x + 2:.1f}" y="{legend_y + 5:.1f}" width="4" height="3" 
        fill="#e3f2fd" stroke="#1976d2" stroke-width="0.1"/>
  <text x="{legend_x + 7:.1f}" y="{legend_y + 7:.1f}" 
        font-family="Arial, sans-serif" font-size="1.8" fill="#212529">Left Main</text>
  
  <rect x="{legend_x + 18:.1f}" y="{legend_y + 5:.1f}" width="4" height="3" 
        fill="#f3e5f5" stroke="#7b1fa2" stroke-width="0.1"/>
  <text x="{legend_x + 23:.1f}" y="{legend_y + 7:.1f}" 
        font-family="Arial, sans-serif" font-size="1.8" fill="#212529">Right Main</text>
  
  <!-- Thumb Keys -->
  <rect x="{legend_x + 2:.1f}" y="{legend_y + 10:.1f}" width="4" height="3" 
        fill="#fff3e0" stroke="#f57c00" stroke-width="0.1"/>
  <text x="{legend_x + 7:.1f}" y="{legend_y + 12:.1f}" 
        font-family="Arial, sans-serif" font-size="1.8" fill="#212529">Left Thumb</text>
  
  <rect x="{legend_x + 18:.1f}" y="{legend_y + 10:.1f}" width="4" height="3" 
        fill="#fff8e1" stroke="#ff9800" stroke-width="0.1"/>
  <text x="{legend_x + 23:.1f}" y="{legend_y + 12:.1f}" 
        font-family="Arial, sans-serif" font-size="1.8" fill="#212529">Right Thumb</text>
  
  <!-- Thumb Arc Origins -->
  <circle cx="{legend_x + 4:.1f}" cy="{legend_y + 16:.1f}" r="1" 
          fill="#d32f2f" stroke="#b71c1c" stroke-width="0.2"/>
  <text x="{legend_x + 7:.1f}" y="{legend_y + 17:.1f}" 
        font-family="Arial, sans-serif" font-size="1.8" fill="#212529">Arc Origins</text>
  
  <!-- Dimensions -->
  <text x="{legend_x + 27.5:.1f}" y="{legend_y + 22:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="1.8" 
        fill="#6c757d">Footprint: {self.footprint_width}×{self.footprint_height}mm | Spacing: {self.key_spacing}mm</text>

</svg>'''
        
        with open(filename, 'w') as f:
            f.write(svg_content)
        
        print(f"SVG visualization exported to {filename}")
        

def main():
    """Main function to demonstrate the keyboard layout calculator."""
    print("Split Column Staggered Keyboard Layout Calculator")
    print("================================================")
    column_stagger = {
                0: 0.0,      # Column 0 (pinky)
                1: -14.45,   # Column 1 (ring)
                2: -4.25,    # Column 2 (middle)
                3: 4.25,     # Column 3 (index)
                4: 2.55,     # Column 4 (inner index)
            }
    # Create calculator with default parameters (including 3 thumb keys)
    calc = KeyboardLayoutCalculator(origin_x=0.0, origin_y=0.0, column_stagger=column_stagger, 
                                   num_rows=3, num_thumb_keys=3, thumb_arc_col_start=3)
    
    # Print layout information
    print(f"\nLayout Specifications:")
    print(f"- Footprint size: {calc.footprint_width}mm x {calc.footprint_height}mm")
    print(f"- Key spacing: {calc.key_spacing}mm")
    print(f"- X pitch: {calc.x_pitch}mm")
    print(f"- Y pitch: {calc.y_pitch}mm")
    print(f"- Rows: {calc.num_rows}")
    print(f"- Columns per half: {calc.num_cols}")
    print(f"- Thumb keys per half: {calc.num_thumb_keys}")
    print(f"- Thumb arc starts under column: {calc.thumb_arc_col_start}")
    print(f"- Thumb arc: {calc.thumb_arc_start_angle}° to {calc.thumb_arc_end_angle}° (radius: {calc.thumb_arc_radius}mm)")
    print(f"- Thumb offset: ({calc.thumb_offset_x}mm, {calc.thumb_offset_y}mm)")
    
    # Display all positions
    calc.print_positions()
    
    # Export files
    calc.export_kicad_format()
    calc.export_csv()
    calc.export_svg()
    
    print(f"\nFiles generated:")
    print(f"- keyboard_positions.txt (KiCad format)")
    print(f"- keyboard_positions.csv (CSV format)")
    print(f"- keyboard_layout.svg (SVG visualization)")


if __name__ == "__main__":
    main()