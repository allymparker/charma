#!/usr/bin/env python3
"""
KiCad Footprint Position Calculator for Split Column Staggered Keyboard

Calculates positions for switch footprints in a split keyboard layout.
Specifications:
- 3 rows, 5 columns per half
- Footprint size: 17.5mm x 16.5mm
- Spacing: 0.5mm between keys
- Column staggered layout
"""

import math
from typing import List, Tuple, Dict


class KeyboardLayoutCalculator:
    def __init__(self, origin_x: float = 0.0, origin_y: float = 0.0):
        """
        Initialize the keyboard layout calculator.
        
        Args:
            origin_x: X coordinate of the origin in mm
            origin_y: Y coordinate of the origin in mm
        """
        self.origin_x = origin_x
        self.origin_y = origin_y
        
        # Footprint dimensions in mm
        self.footprint_width = 17.5
        self.footprint_height = 16.5
        
        # Spacing between keys in mm
        self.key_spacing = 0.5
        
        # Total spacing between key centers
        self.x_pitch = self.footprint_width + self.key_spacing
        self.y_pitch = self.footprint_height + self.key_spacing
        
        # Column stagger offsets (in mm) - adjust these for desired stagger
        self.column_stagger = {
            0: 0.0,      # Column 0 (pinky)
            1: -14.45,     # Column 1 (ring)
            2: -4.25,     # Column 2 (middle)
            3: 4.25,     # Column 3 (index)
            4: 2.55,      # Column 4 (inner index)
        }
        
        # Thumb key configuration
        self.thumb_offset_y = 7.3  # mm below the reference key
        self.thumb_spacing_x = 18.0  # mm spacing between thumb keys
        self.thumb_drop_y = 3.0  # mm additional drop for keys 2 and 3
        self.thumb_rotation = 21.0  # degrees rotation for keys 2 and 3
        
    def calculate_position(self, row: int, col: int, is_right_half: bool = False) -> Tuple[float, float]:
        """
        Calculate the position of a key at given row and column.
        
        Args:
            row: Row number (0-2)
            col: Column number (0-4)
            is_right_half: True for right half, False for left half
            
        Returns:
            Tuple of (x, y) coordinates in mm
        """
        # Base position calculation
        x = self.origin_x + (col * self.x_pitch)
        y = self.origin_y + (row * self.y_pitch)
        
        # Apply column stagger by summing the stagger offsets up to this column
        for c in range(col + 1):
            y += self.column_stagger[c]
        
        # For right half, mirror the layout
        if is_right_half:
            # Mirror across Y axis and add separation between halves
            separation = 30.0  # mm separation between halves (increased)
            # Calculate the rightmost position of left half
            left_half_width = 4 * self.x_pitch + self.footprint_width
            x = left_half_width + separation + ((4 - col) * self.x_pitch)
        
        return (x, y)
    
    def calculate_thumb_positions(self, is_right_half: bool = False) -> List[Tuple[str, float, float, float]]:
        """
        Calculate positions for the three thumb keys.
        
        Args:
            is_right_half: True for right half, False for left half
            
        Returns:
            List of (key_name, x, y, rotation) tuples
        """
        thumb_positions = []
        
        # Get the reference key position (col 4, row 2 - bottom row of col 4)
        ref_x, ref_y = self.calculate_position(2, 4, is_right_half)
        
        # First thumb key: directly below the reference key
        thumb1_x = ref_x
        thumb1_y = ref_y + self.footprint_height + self.thumb_offset_y
        thumb1_rotation = 0.0
        
        if is_right_half:
            thumb_positions.append(("RT0", thumb1_x, thumb1_y, thumb1_rotation))
            
            # For right half, thumb keys go to the left and are rotated counter-clockwise
            # Add extra half key offset for rotated keys
            extra_offset_x = self.footprint_width / 2
            extra_offset_y = self.footprint_height / 2
            
            thumb2_x = thumb1_x - self.thumb_spacing_x - extra_offset_x
            thumb2_y = thumb1_y + self.thumb_drop_y + extra_offset_y
            thumb2_rotation = -self.thumb_rotation
            
            thumb3_x = thumb2_x - self.thumb_spacing_x - extra_offset_x
            thumb3_y = thumb2_y + self.thumb_drop_y + extra_offset_y
            thumb3_rotation = -self.thumb_rotation * 2  # Double rotation for last key
            
            thumb_positions.append(("RT1", thumb2_x, thumb2_y, thumb2_rotation))
            thumb_positions.append(("RT2", thumb3_x, thumb3_y, thumb3_rotation))
        else:
            thumb_positions.append(("LT0", thumb1_x, thumb1_y, thumb1_rotation))
            
            # For left half, thumb keys go to the right and are rotated clockwise
            # Add extra half key offset for rotated keys
            extra_offset_x = self.footprint_width / 2
            extra_offset_y = self.footprint_height / 2
            
            thumb2_x = thumb1_x + self.thumb_spacing_x + extra_offset_x
            thumb2_y = thumb1_y + self.thumb_drop_y + extra_offset_y
            thumb2_rotation = self.thumb_rotation
            
            thumb3_x = thumb2_x + self.thumb_spacing_x + extra_offset_x
            thumb3_y = thumb2_y + self.thumb_drop_y + extra_offset_y
            thumb3_rotation = self.thumb_rotation * 2  # Double rotation for last key
            
            thumb_positions.append(("LT1", thumb2_x, thumb2_y, thumb2_rotation))
            thumb_positions.append(("LT2", thumb3_x, thumb3_y, thumb3_rotation))
        
        return thumb_positions
    
    def generate_all_positions(self) -> Dict[str, List[Tuple[str, float, float]]]:
        """
        Generate all key positions for both halves of the keyboard.
        
        Returns:
            Dictionary with 'left' and 'right' keys containing lists of
            (key_name, x, y) tuples
        """
        positions = {'left': [], 'right': []}
        
        # Generate positions for left half
        for row in range(3):
            for col in range(5):
                x, y = self.calculate_position(row, col, is_right_half=False)
                key_name = f"L{row}{col}"
                positions['left'].append((key_name, x, y))
        
        # Add left thumb keys (ignore rotation for basic positioning)
        left_thumbs = self.calculate_thumb_positions(is_right_half=False)
        for key_name, x, y, rotation in left_thumbs:
            positions['left'].append((key_name, x, y))
        
        # Generate positions for right half
        for row in range(3):
            for col in range(5):
                x, y = self.calculate_position(row, col, is_right_half=True)
                key_name = f"R{row}{col}"
                positions['right'].append((key_name, x, y))
        
        # Add right thumb keys (ignore rotation for basic positioning)
        right_thumbs = self.calculate_thumb_positions(is_right_half=True)
        for key_name, x, y, rotation in right_thumbs:
            positions['right'].append((key_name, x, y))
        
        return positions
    
    def generate_all_positions_with_rotation(self) -> Dict[str, List[Tuple[str, float, float, float]]]:
        """
        Generate all key positions including rotation data.
        
        Returns:
            Dictionary with 'left' and 'right' keys containing lists of
            (key_name, x, y, rotation) tuples
        """
        positions = {'left': [], 'right': []}
        
        # Generate positions for left half (no rotation for main keys)
        for row in range(3):
            for col in range(5):
                x, y = self.calculate_position(row, col, is_right_half=False)
                key_name = f"L{row}{col}"
                positions['left'].append((key_name, x, y, 0.0))
        
        # Add left thumb keys with rotation
        left_thumbs = self.calculate_thumb_positions(is_right_half=False)
        positions['left'].extend(left_thumbs)
        
        # Generate positions for right half (no rotation for main keys)
        for row in range(3):
            for col in range(5):
                x, y = self.calculate_position(row, col, is_right_half=True)
                key_name = f"R{row}{col}"
                positions['right'].append((key_name, x, y, 0.0))
        
        # Add right thumb keys with rotation
        right_thumbs = self.calculate_thumb_positions(is_right_half=True)
        positions['right'].extend(right_thumbs)
        
        return positions
    
    def print_positions(self):
        """Print all key positions in a readable format."""
        positions = self.generate_all_positions()
        
        print("Keyboard Layout Positions (in mm)")
        print("=" * 50)
        
        print("\nLeft Half:")
        print("-" * 30)
        for key_name, x, y in positions['left']:
            print(f"{key_name}: ({x:6.2f}, {y:6.2f})")
        
        print("\nRight Half:")
        print("-" * 30)
        for key_name, x, y in positions['right']:
            print(f"{key_name}: ({x:6.2f}, {y:6.2f})")
    
    def export_kicad_format(self, filename: str = "keyboard_positions.txt"):
        """
        Export positions in a format suitable for KiCad scripting.
        
        Args:
            filename: Output filename
        """
        positions = self.generate_all_positions_with_rotation()
        
        with open(filename, 'w') as f:
            f.write("# KiCad Keyboard Layout Positions\n")
            f.write("# Format: Reference X(mm) Y(mm) Rotation(degrees)\n")
            f.write("# Generated by layout.py\n\n")
            
            f.write("# Left Half\n")
            for key_name, x, y, rotation in positions['left']:
                f.write(f"{key_name} {x:.3f} {y:.3f} {rotation:.1f}\n")
            
            f.write("\n# Right Half\n")
            for key_name, x, y, rotation in positions['right']:
                f.write(f"{key_name} {x:.3f} {y:.3f} {rotation:.1f}\n")
        
        print(f"Positions exported to {filename}")
    
    def export_csv(self, filename: str = "keyboard_positions.csv"):
        """
        Export positions in CSV format.
        
        Args:
            filename: Output CSV filename
        """
        positions = self.generate_all_positions_with_rotation()
        
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
        positions_with_rotation = self.generate_all_positions_with_rotation()
        
        # Calculate SVG dimensions
        all_positions = positions['left'] + positions['right']
        min_x = min(x for _, x, y in all_positions) - 10
        max_x = max(x for _, x, y in all_positions) + self.footprint_width + 10
        min_y = min(y for _, x, y in all_positions) - 25  # More space at top
        max_y = max(y for _, x, y in all_positions) + self.footprint_height + 35  # More space at bottom
        
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
        for key_name, x, y, rotation in positions_with_rotation['left']:
            center_x = x + self.footprint_width/2
            center_y = y + self.footprint_height/2
            
            if rotation != 0:
                # Rotated key (thumb keys)
                svg_content += f'''  <!-- {key_name} (rotated) -->
  <g transform="rotate({rotation:.1f} {center_x:.1f} {center_y:.1f})">
    <rect x="{x:.1f}" y="{y:.1f}" 
          width="{self.footprint_width:.1f}" height="{self.footprint_height:.1f}"
          fill="#fff3e0" stroke="#f57c00" stroke-width="0.1"/>
    <text x="{center_x:.1f}" y="{center_y + 1:.1f}" 
          text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
          fill="#f57c00" font-weight="bold">{key_name}</text>
  </g>
'''
            else:
                # Regular key
                svg_content += f'''  <!-- {key_name} -->
  <rect x="{x:.1f}" y="{y:.1f}" 
        width="{self.footprint_width:.1f}" height="{self.footprint_height:.1f}"
        fill="#e3f2fd" stroke="#1976d2" stroke-width="0.1"/>
  <text x="{center_x:.1f}" y="{center_y + 1:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
        fill="#1976d2" font-weight="bold">{key_name}</text>
'''
        
        # Add key rectangles and labels for right half
        for key_name, x, y, rotation in positions_with_rotation['right']:
            center_x = x + self.footprint_width/2
            center_y = y + self.footprint_height/2
            
            if rotation != 0:
                # Rotated key (thumb keys)
                svg_content += f'''  <!-- {key_name} (rotated) -->
  <g transform="rotate({rotation:.1f} {center_x:.1f} {center_y:.1f})">
    <rect x="{x:.1f}" y="{y:.1f}" 
          width="{self.footprint_width:.1f}" height="{self.footprint_height:.1f}"
          fill="#fff3e0" stroke="#f57c00" stroke-width="0.1"/>
    <text x="{center_x:.1f}" y="{center_y + 1:.1f}" 
          text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
          fill="#f57c00" font-weight="bold">{key_name}</text>
  </g>
'''
            else:
                # Regular key
                svg_content += f'''  <!-- {key_name} -->
  <rect x="{x:.1f}" y="{y:.1f}" 
        width="{self.footprint_width:.1f}" height="{self.footprint_height:.1f}"
        fill="#f3e5f5" stroke="#7b1fa2" stroke-width="0.1"/>
  <text x="{center_x:.1f}" y="{center_y + 1:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
        fill="#7b1fa2" font-weight="bold">{key_name}</text>
'''
        
        # Add legend
        legend_x = min_x + 5
        legend_y = max_y - 30  # Moved further down for larger legend
        svg_content += f'''
  <!-- Legend -->
  <rect x="{legend_x:.1f}" y="{legend_y:.1f}" width="40" height="15" 
        fill="white" stroke="#dee2e6" stroke-width="0.5" rx="1"/>
  
  <text x="{legend_x + 20:.1f}" y="{legend_y + 3:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
        fill="#212529" font-weight="bold">Legend</text>
  
  <rect x="{legend_x + 2:.1f}" y="{legend_y + 5:.1f}" width="4" height="3" 
        fill="#e3f2fd" stroke="#1976d2" stroke-width="0.1"/>
  <text x="{legend_x + 7:.1f}" y="{legend_y + 7:.1f}" 
        font-family="Arial, sans-serif" font-size="1.8" fill="#212529">Left Keys</text>
  
  <rect x="{legend_x + 15:.1f}" y="{legend_y + 5:.1f}" width="4" height="3" 
        fill="#f3e5f5" stroke="#7b1fa2" stroke-width="0.1"/>
  <text x="{legend_x + 20:.1f}" y="{legend_y + 7:.1f}" 
        font-family="Arial, sans-serif" font-size="1.8" fill="#212529">Right Keys</text>
  
  <rect x="{legend_x + 29:.1f}" y="{legend_y + 5:.1f}" width="4" height="3" 
        fill="#fff3e0" stroke="#f57c00" stroke-width="0.1"/>
  <text x="{legend_x + 34:.1f}" y="{legend_y + 7:.1f}" 
        font-family="Arial, sans-serif" font-size="1.8" fill="#212529">Thumb Keys</text>
  
  <!-- Dimensions -->
  <text x="{legend_x + 20:.1f}" y="{legend_y + 11:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="1.8" 
        fill="#6c757d">Footprint: {self.footprint_width}×{self.footprint_height}mm | Spacing: {self.key_spacing}mm</text>
  
  <text x="{legend_x + 20:.1f}" y="{legend_y + 13:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="1.8" 
        fill="#6c757d">Thumb rotation: {self.thumb_rotation}° | 3 rows + 3 thumbs per half</text>

</svg>'''
        
        with open(filename, 'w') as f:
            f.write(svg_content)
        
        print(f"SVG visualization exported to {filename}")
        

def main():
    """Main function to demonstrate the keyboard layout calculator."""
    print("Split Column Staggered Keyboard Layout Calculator")
    print("================================================")
    
    # Create calculator with origin at (0, 0)
    calc = KeyboardLayoutCalculator(origin_x=0.0, origin_y=0.0)
    
    # Print layout information
    print(f"\nLayout Specifications:")
    print(f"- Footprint size: {calc.footprint_width}mm x {calc.footprint_height}mm")
    print(f"- Key spacing: {calc.key_spacing}mm")
    print(f"- X pitch: {calc.x_pitch}mm")
    print(f"- Y pitch: {calc.y_pitch}mm")
    print(f"- Rows: 3")
    print(f"- Columns per half: 5")
    print(f"- Thumb keys per half: 3")
    print(f"- Thumb key rotation: {calc.thumb_rotation}°")
    
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