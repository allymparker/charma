#!/usr/bin/env python3
"""
Example usage of the refactored KeyboardLayoutCalculator

This demonstrates how to use the new functional API to calculate positions
without creating an instance of the calculator class.
"""

from layout import KeyboardLayoutConfig, KeyboardLayoutCalculator, print_positions, export_csv, export_svg


def main():
    print("Example: Custom Keyboard Layout")
    print("==============================")
    
    # Define custom column stagger
    custom_stagger = {
        0: 0.0,      # Column 0 (pinky) - no offset
        1: -12.0,    # Column 1 (ring) - moved up 12mm  
        2: -2.0,     # Column 2 (middle) - moved up 2mm
        3: 6.0,      # Column 3 (index) - moved down 6mm
        4: 4.0,      # Column 4 (inner index) - moved down 4mm
    }
    
    # Create a configuration
    config = KeyboardLayoutConfig(
        origin_x=10,
        origin_y=25,
        num_rows=4,  # 4 rows instead of 3
        column_stagger=custom_stagger,
        num_thumb_keys=2,  # Only 2 thumb keys
        thumb_arc_col_start=2  # Thumb arc starts under middle finger
    )
    
    print(f"Configuration:")
    print(f"- Origin: ({config.origin_x}, {config.origin_y})")
    print(f"- Rows: {config.num_rows}")
    print(f"- Columns: {config.num_cols}")
    print(f"- Thumb keys: {config.num_thumb_keys}")
    print(f"- Thumb arc starts under column: {config.thumb_arc_col_start}")
    
    # Calculate positions using the static method
    positions = KeyboardLayoutCalculator.generate_all_positions(config)
    
    # Print positions to console
    print_positions(config, positions)
    
    # Export files with custom names
    export_csv(positions, "custom_keyboard_positions.csv")
    export_svg(config, positions, "custom_keyboard_layout.svg")
    
    print(f"\nFiles generated:")
    print(f"- custom_keyboard_positions.csv (CSV format)")
    print(f"- custom_keyboard_layout.svg (SVG visualization)")
    
    # Example: Calculate just one position
    print(f"\nExample: Calculate single position")
    print(f"Left half, row 0, col 2 position: {KeyboardLayoutCalculator.calculate_left_position(config, 0, 2)}")
    
    # Example: Calculate thumb position
    thumb_pos = KeyboardLayoutCalculator.calculate_thumb_position(config, 0)
    print(f"First thumb key position: {thumb_pos}")


if __name__ == "__main__":
    main()
