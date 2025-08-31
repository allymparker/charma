#!/usr/bin/env python3
"""
KiCad PCB Layout Script for Keyboard Positions

This script calculates keyboard positions using the layout.py module and positions footprints
in your KiCad PCB file accordingly.

Usage:
1. Open your PCB in KiCad's PCB Editor (Pcbnew)
2. Go to Tools -> Scripting Console
3. Navigate to the directory containing this script (if needed):
   os.chdir('/workspaces/charma/pcb/layout')
4. Run: exec(open('kicad_position_script.py').read())

Alternative usage from any directory:
exec(open('../layout/kicad_position_script.py').read())

Or save this as an action plugin in your KiCad plugins directory.
"""

import os
import sys

# Add the layout module to the path
# Handle case where __file__ is not defined (e.g., when executed via exec())
try:
    script_dir = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # Fallback: assume we're in the layout directory or use current working directory
    script_dir = os.getcwd()
    # If we're not in the layout directory, try to find it
    if not os.path.exists(os.path.join(script_dir, "layout.py")):
        # Try common locations
        possible_dirs = [os.path.join(script_dir, "layout"), os.path.join(script_dir, "..", "layout"), "/workspaces/charma/pcb/layout"]
        for dir_path in possible_dirs:
            if os.path.exists(os.path.join(dir_path, "layout.py")):
                script_dir = dir_path
                break
        else:
            print(f"Warning: Could not find layout.py. Current directory: {script_dir}")
            print("Make sure you're running this from the correct directory or adjust the path.")

sys.path.insert(0, script_dir)

# Import modules with reloading support
import importlib
import layout

# Reload modules to pick up any changes made since last run
importlib.reload(layout)

from layout import KeyboardLayoutCalculator, get_charma_config, print_positions

try:
    import pcbnew
except ImportError:
    print("Warning: pcbnew module not available. This script must be run within KiCad.")
    pcbnew = None


def position_keyboard_footprints_from_positions(positions, x_origin=0, y_origin=0):
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
            x_nm = pcbnew.FromMM(x_mm + x_origin)
            y_nm = pcbnew.FromMM(y_mm + y_origin)

            # Set position (KiCad uses VECTOR2I for position)
            footprint.SetPosition(pcbnew.VECTOR2I(int(x_nm), int(y_nm)))

            # Set rotation (KiCad uses degrees)
            footprint.SetOrientationDegrees(-rotation)

            positioned_count += 1
        else:
            missing_footprints.append(ref)

    print(f"\nSummary:")
    print(f"- Successfully positioned: {positioned_count} footprints")
    print(f"- Missing footprints: {len(missing_footprints)}")

    if missing_footprints:
        # Group missing footprints by type
        switches = [r for r in missing_footprints if r.startswith("SW")]
        diodes_left = [r for r in missing_footprints if r.startswith("DL")]
        diodes_right = [r for r in missing_footprints if r.startswith("DR")]
        other = [r for r in missing_footprints if not r.startswith("SW") and not r.startswith("D")]

        if switches:
            print(f"Missing switches: {', '.join(switches)}")
        if diodes_left:
            print(f"Missing left diodes: {', '.join(diodes_left)}")
        if diodes_right:
            print(f"Missing right diodes: {', '.join(diodes_right)}")
        if other:
            print(f"Missing other components: {', '.join(other)}")
        print("Make sure your footprints have the correct reference designators.")

    # Refresh the display
    pcbnew.Refresh()
    print("Layout complete! The display has been refreshed.")


def position_keyboard_footprints_direct(config=None):
    """
    Position keyboard footprints by calculating positions directly.

    Args:
        config: KeyboardLayoutConfig instance. If None, uses Charma default configuration.
    """
    # Use Charma configuration if none provided
    if config is None:
        config = get_charma_config()

    # Calculate positions
    positions = KeyboardLayoutCalculator.generate_all_positions(config)

    print_positions(positions)

    # Position the footprints
    position_keyboard_footprints_from_positions(positions, 30, 30)


# Main execution
if __name__ == "__main__":
    print("Calculating positions directly from layout configuration...")
    position_keyboard_footprints_direct()

# For direct console execution, you can also just call:
# position_keyboard_footprints_direct()  # Calculate positions directly
