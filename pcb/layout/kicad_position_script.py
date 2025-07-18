#!/usr/bin/env python3
"""
KiCad PCB Layout Script for Keyboard Positions

This script calculates keyboard positions using the layout.py module and positions footprints
in your KiCad PCB file accordingly.

Usage:
1. Open your PCB in KiCad's PCB Editor (Pcbnew)
2. Go to Tools -> Scripting Console
3. Run: exec(open('/path/to/this/script.py').read())

Or save this as an action plugin in your KiCad plugins directory.
"""

import os
import sys

# Add the layout module to the path
script_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, script_dir)

from layout import KeyboardLayoutConfig, KeyboardLayoutCalculator

try:
    import pcbnew
except ImportError:
    print("Warning: pcbnew module not available. This script must be run within KiCad.")
    pcbnew = None


def position_keyboard_footprints_from_positions(positions):
    """
    Position keyboard footprints based on calculated positions.
    
    Args:
        positions: Dictionary from KeyboardLayoutCalculator.generate_all_positions()
    """
    if pcbnew is None:
        print("Error: pcbnew module not available. This script must be run within KiCad.")
        return
        
    # Get the current board
    board = pcbnew.GetBoard()
    
    if not board:
        print("Error: No PCB board loaded!")
        return
    
    # Convert positions to flat dictionary format
    position_dict = {}
    for half_name, half_data in positions.items():
        for component_type, components in half_data.items():
            for ref, x_mm, y_mm, rotation in components:
                position_dict[ref] = (x_mm, y_mm, rotation)
    
    print(f"Loaded {len(position_dict)} positions from calculator")
    
    # Position footprints
    positioned_count = 0
    missing_footprints = []
    
    for ref, (x_mm, y_mm, rotation) in position_dict.items():
        # Find the footprint by reference
        footprint = board.FindFootprintByReference(ref)
        
        if footprint:
            # Convert mm to KiCad internal units (nanometers)
            x_nm = pcbnew.FromMM(x_mm)
            y_nm = pcbnew.FromMM(y_mm)
            
            # Set position (KiCad uses VECTOR2I for position)
            footprint.SetPosition(pcbnew.VECTOR2I(int(x_nm), int(y_nm)))
            
            # Set rotation (KiCad uses tenths of degrees)
            # Convert degrees to tenths of degrees and create EDA_ANGLE
            rotation_tenths = int(rotation * 10)
            footprint.SetOrientationDegrees(rotation)
            
            positioned_count += 1
            print(f"Positioned {ref} at ({x_mm:.3f}, {y_mm:.3f}) mm, {rotation:.1f}°")
        else:
            missing_footprints.append(ref)
    
    print(f"\nSummary:")
    print(f"- Successfully positioned: {positioned_count} footprints")
    print(f"- Missing footprints: {len(missing_footprints)}")
    
    if missing_footprints:
        print(f"Missing footprints: {', '.join(missing_footprints)}")
        print("Make sure your footprints have the correct reference designators.")
    
    # Refresh the display
    pcbnew.Refresh()
    print("Layout complete! The display has been refreshed.")


def position_keyboard_footprints_direct(config=None):
    """
    Position keyboard footprints by calculating positions directly.
    
    Args:
        config: KeyboardLayoutConfig instance. If None, uses default configuration.
    """
    # Use default configuration if none provided
    if config is None:
        column_stagger = {
            0: 0.0,      # Column 0 (pinky)
            1: -14.45,   # Column 1 (ring)
            2: -4.25,    # Column 2 (middle)
            3: 4.25,     # Column 3 (index)
            4: 2.55,     # Column 4 (inner index)
        }
        config = KeyboardLayoutConfig(
            origin_x=14, origin_y=28.95, column_stagger=column_stagger, 
            num_rows=3, num_thumb_keys=3, thumb_arc_col_start=3
        )
    
    # Calculate positions
    positions = KeyboardLayoutCalculator.generate_all_positions(config)
    
    # Position the footprints
    position_keyboard_footprints_from_positions(positions)


# Main execution
if __name__ == "__main__":
    print("Calculating positions directly from layout configuration...")
    position_keyboard_footprints_direct()

# For direct console execution, you can also just call:
# position_keyboard_footprints_direct()  # Calculate positions directly
