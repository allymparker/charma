#!/usr/bin/env python3
"""
Main demonstration script for the keyboard layout calculator.

This script demonstrates how to use the keyboard layout calculator
to generate positions for a split column staggered keyboard.
"""

from layout import KeyboardLayoutConfig, KeyboardLayoutCalculator
from output import print_positions, export_csv, export_svg


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
    # Create configuration with default parameters (including 3 thumb keys)
    config = KeyboardLayoutConfig(origin_x=14, origin_y=28.95, column_stagger=column_stagger, 
                                 num_rows=3, num_thumb_keys=3, thumb_arc_col_start=3)
    
    # Print layout information
    print(f"\nLayout Specifications:")
    print(f"- Switch footprint size: {config.footprint_width}mm x {config.footprint_height}mm")
    print(f"- Diode footprint size: {config.diode_width}mm x {config.diode_height}mm")
    print(f"- Diode offset from switch: ({config.diode_offset_x}mm, {config.diode_offset_y}mm)")
    print(f"- Key spacing: {config.key_spacing}mm")
    print(f"- X pitch: {config.x_pitch}mm")
    print(f"- Y pitch: {config.y_pitch}mm")
    print(f"- Rows: {config.num_rows}")
    print(f"- Columns per half: {config.num_cols}")
    print(f"- Thumb keys per half: {config.num_thumb_keys}")
    print(f"- Thumb arc starts under column: {config.thumb_arc_col_start}")
    print(f"- Thumb arc: {config.thumb_arc_start_angle}° to {config.thumb_arc_end_angle}° (radius: {config.thumb_arc_radius}mm)")
    print(f"- Thumb offset: ({config.thumb_offset_x}mm, {config.thumb_offset_y}mm)")
    
    # Generate positions
    positions = KeyboardLayoutCalculator.generate_all_positions(config)
    
    # Display all positions
    print_positions(config, positions)
    
    # Export files
    export_csv(positions)
    export_svg(config, positions, "keyboard_layout.svg")
    
    print(f"\nFiles generated:")
    print(f"- keyboard_positions.csv (CSV format)")
    print(f"- keyboard_layout.svg (SVG visualization)")


if __name__ == "__main__":
    main()
