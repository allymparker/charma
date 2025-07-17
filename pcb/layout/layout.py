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
                 num_rows: int = 3, column_stagger: Dict[int, float] = None):
        """
        Initialize the keyboard layout calculator.
        
        Args:
            origin_x: X coordinate of the origin in mm
            origin_y: Y coordinate of the origin in mm
            num_rows: Number of rows in the keyboard layout
            column_stagger: Dictionary mapping column index to stagger offset in mm
                          If None, uses default column stagger values
        """
        self.origin_x = origin_x
        self.origin_y = origin_y
        
        # Layout dimensions
        self.num_rows = num_rows
        
        # Column stagger offsets (in mm) - adjust these for desired stagger
        self.column_stagger = column_stagger.copy()
        
        self.num_cols = len(self.column_stagger)
        
        # Footprint dimensions in mm
        self.footprint_width = 17.5
        self.footprint_height = 16.5
        
        # Spacing between keys in mm
        self.key_spacing = 0.5
        
        # Total spacing between key centers
        self.x_pitch = self.footprint_width + self.key_spacing
        self.y_pitch = self.footprint_height + self.key_spacing
        
    def calculate_left_position(self, row: int, col: int) -> Tuple[float, float]:
        """
        Calculate the position of a key at given row and column for the left half.
        
        Args:
            row: Row number (0 to num_rows-1)
            col: Column number (0 to num_cols-1)
            
        Returns:
            Tuple of (x, y) coordinates in mm
        """
        # Base position calculation
        x = self.origin_x + (col * self.x_pitch)
        y = self.origin_y + (row * self.y_pitch)
        
        # Apply column stagger by summing the stagger offsets up to this column
        for c in range(col + 1):
            y += self.column_stagger[c]
        
        return (x, y)
    
    def mirror_position(self, left_x: float, left_y: float) -> Tuple[float, float]:
        """
        Mirror a left half position to create the corresponding right half position.
        
        Args:
            left_x: X coordinate from left half
            left_y: Y coordinate from left half (same for both halves)
            
        Returns:
            Tuple of (x, y) coordinates for the mirrored position
        """
        # Calculate the rightmost position of left half
        left_half_width = (self.num_cols - 1) * self.x_pitch + self.footprint_width
        separation = 30.0  # mm separation between halves
        
        # Mirror the x coordinate
        right_x = left_half_width + separation + (left_half_width - left_x - self.footprint_width)
        
        return (right_x, left_y)
    
    def generate_all_positions(self) -> Dict[str, List[Tuple[str, float, float]]]:
        """
        Generate all key positions for both halves of the keyboard.
        Both halves numbered top-left to bottom-right (row by row, left to right).
        
        Returns:
            Dictionary with 'left' and 'right' keys containing lists of
            (key_name, x, y) tuples
        """
        positions = {'left': [], 'right': []}
        
        # Generate left half positions (numbered row by row, left to right)
        switch_num = 1
        for row in range(self.num_rows):
            for col in range(self.num_cols):
                x, y = self.calculate_left_position(row, col)
                key_name = f"SWL{switch_num}"
                positions['left'].append((key_name, x, y))
                switch_num += 1
        
        # Generate right half by mirroring left positions
        # Numbered row by row, left to right from the right half perspective
        switch_num = 1
        for row in range(self.num_rows):
            for col in range(self.num_cols - 1, -1, -1):  # Reverse column order
                # Find the corresponding left position
                left_x, left_y = self.calculate_left_position(row, col)
                # Mirror it to get right position
                right_x, right_y = self.mirror_position(left_x, left_y)
                key_name = f"SWR{switch_num}"
                positions['right'].append((key_name, right_x, right_y))
                switch_num += 1
        
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
        positions = self.generate_all_positions()
        
        with open(filename, 'w') as f:
            f.write("# KiCad Keyboard Layout Positions\n")
            f.write("# Format: Reference X(mm) Y(mm)\n")
            f.write("# Generated by layout.py\n\n")
            
            f.write("# Left Half\n")
            for key_name, x, y in positions['left']:
                f.write(f"{key_name} {x:.3f} {y:.3f}\n")
            
            f.write("\n# Right Half\n")
            for key_name, x, y in positions['right']:
                f.write(f"{key_name} {x:.3f} {y:.3f}\n")
        
        print(f"Positions exported to {filename}")
    
    def export_csv(self, filename: str = "keyboard_positions.csv"):
        """
        Export positions in CSV format.
        
        Args:
            filename: Output CSV filename
        """
        positions = self.generate_all_positions()
        
        with open(filename, 'w') as f:
            f.write("Reference,X(mm),Y(mm),Half\n")
            
            for key_name, x, y in positions['left']:
                f.write(f"{key_name},{x:.3f},{y:.3f},Left\n")
            
            for key_name, x, y in positions['right']:
                f.write(f"{key_name},{x:.3f},{y:.3f},Right\n")
        
        print(f"Positions exported to {filename}")
    
    def export_svg(self, filename: str = "keyboard_layout.svg"):
        """
        Export positions as an SVG visualization.
        
        Args:
            filename: Output SVG filename
        """
        positions = self.generate_all_positions()
        
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
        for key_name, x, y in positions['left']:
            svg_content += f'''  <!-- {key_name} -->
  <rect x="{x:.1f}" y="{y:.1f}" 
        width="{self.footprint_width:.1f}" height="{self.footprint_height:.1f}"
        fill="#e3f2fd" stroke="#1976d2" stroke-width="0.1"/>
  <text x="{x + self.footprint_width/2:.1f}" y="{y + self.footprint_height/2 + 1:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
        fill="#1976d2" font-weight="bold">{key_name}</text>
'''
        
        # Add key rectangles and labels for right half
        for key_name, x, y in positions['right']:
            svg_content += f'''  <!-- {key_name} -->
  <rect x="{x:.1f}" y="{y:.1f}" 
        width="{self.footprint_width:.1f}" height="{self.footprint_height:.1f}"
        fill="#f3e5f5" stroke="#7b1fa2" stroke-width="0.1"/>
  <text x="{x + self.footprint_width/2:.1f}" y="{y + self.footprint_height/2 + 1:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
        fill="#7b1fa2" font-weight="bold">{key_name}</text>
'''
        
        # Add legend
        legend_x = min_x + 5
        legend_y = max_y - 25  # Moved further down
        svg_content += f'''
  <!-- Legend -->
  <rect x="{legend_x:.1f}" y="{legend_y:.1f}" width="30" height="12" 
        fill="white" stroke="#dee2e6" stroke-width="0.5" rx="1"/>
  
  <text x="{legend_x + 15:.1f}" y="{legend_y + 3:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
        fill="#212529" font-weight="bold">Legend</text>
  
  <rect x="{legend_x + 2:.1f}" y="{legend_y + 5:.1f}" width="4" height="3" 
        fill="#e3f2fd" stroke="#1976d2" stroke-width="0.1"/>
  <text x="{legend_x + 7:.1f}" y="{legend_y + 7:.1f}" 
        font-family="Arial, sans-serif" font-size="2" fill="#212529">Left Half</text>
  
  <rect x="{legend_x + 16:.1f}" y="{legend_y + 5:.1f}" width="4" height="3" 
        fill="#f3e5f5" stroke="#7b1fa2" stroke-width="0.1"/>
  <text x="{legend_x + 21:.1f}" y="{legend_y + 7:.1f}" 
        font-family="Arial, sans-serif" font-size="2" fill="#212529">Right Half</text>
  
  <!-- Dimensions -->
  <text x="{legend_x + 15:.1f}" y="{legend_y + 11:.1f}" 
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
    # Create calculator with default parameters
    calc = KeyboardLayoutCalculator(origin_x=0.0, origin_y=0.0, column_stagger=column_stagger, num_rows=3)
    
    # Print layout information
    print(f"\nLayout Specifications:")
    print(f"- Footprint size: {calc.footprint_width}mm x {calc.footprint_height}mm")
    print(f"- Key spacing: {calc.key_spacing}mm")
    print(f"- X pitch: {calc.x_pitch}mm")
    print(f"- Y pitch: {calc.y_pitch}mm")
    print(f"- Rows: {calc.num_rows}")
    print(f"- Columns per half: {calc.num_cols}")
    
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