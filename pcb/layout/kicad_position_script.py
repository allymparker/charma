v#!/usr/bin/env python3
"""
KiCad PCB Layout Script for Keyboard Positions

This script reads the keyboard_positions.txt file and positions footprints
in your KiCad PCB file accordingly.

Usage:
1. Open your PCB in KiCad's PCB Editor (Pcbnew)
2. Go to Tools -> Scripting Console
3. Run: exec(open('/path/to/this/script.py').read())

Or save this as an action plugin in your KiCad plugins directory.
"""

import pcbnew
import os

def position_keyboard_footprints(positions_file="./layout/keyboard_positions.txt"):
    """
    Position keyboard footprints based on the positions file.
    
    Args:
        positions_file: Path to the keyboard positions file
    """
    # Get the current board
    board = pcbnew.GetBoard()
    
    if not board:
        print("Error: No PCB board loaded!")
        return
    
    # Check if positions file exists
    if not os.path.exists(positions_file):
        print(f"Error: Positions file '{positions_file}' not found!")
        print(f"Current directory: {os.getcwd()}")
        return
    
    # Read positions from file
    positions = {}
    with open(positions_file, 'r') as f:
        for line in f:
            line = line.strip()
            # Skip comments and empty lines
            if line.startswith('#') or not line:
                continue
            
            # Parse: Reference X(mm) Y(mm) Rotation(degrees)
            parts = line.split()
            if len(parts) >= 4:
                ref = parts[0]
                x_mm = float(parts[1])
                y_mm = float(parts[2])
                rotation = float(parts[3])
                positions[ref] = (x_mm, y_mm, rotation)
    
    print(f"Loaded {len(positions)} positions from {positions_file}")
    
    # Position footprints
    positioned_count = 0
    missing_footprints = []
    
    for ref, (x_mm, y_mm, rotation) in positions.items():
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

# Main execution
if __name__ == "__main__":
    # Try to find the positions file in common locations
    try:
        # First try current working directory
        positions_file = "keyboard_positions.txt"
        if not os.path.exists(positions_file):
            # Try relative to script location if __file__ is available
            try:
                script_dir = os.path.dirname(os.path.abspath(__file__))
                positions_file = os.path.join(script_dir, "keyboard_positions.txt")
            except NameError:
                # __file__ not available (running in console), use current directory
                positions_file = "./layout/keyboard_positions.txt"
        
        position_keyboard_footprints(positions_file)
    except Exception as e:
        print(f"Error: {e}")
        print("You can also call the function directly:")
        print("position_keyboard_footprints('/full/path/to/keyboard_positions.txt')")

# For direct console execution, you can also just call:
# position_keyboard_footprints("keyboard_positions.txt")
