#!/usr/bin/env python3
"""
Main demonstration script for the keyboard layout calculator.

This script demonstrates how to use the keyboard layout calculator
to generate positions for a split column staggered keyboard.
"""

from layout import KeyboardLayoutCalculator, get_charma_config
from output import (
    print_positions,
    export_csv,
    export_svg,
    export_svg_for_footprints,
    export_svg_switch_plate,
    export_svg_mounting_holes,
    export_svg_hotswap_profile,
)


def main():
    """Main function to demonstrate the keyboard layout calculator."""
    print("Split Column Staggered Keyboard Layout Calculator")
    print("================================================")

    # Create configuration using the Charma factory method
    config = get_charma_config()

    # Print layout information
    print("\nLayout Specifications:")
    print(
        f"- Switch footprint size: {config.footprint_width}mm x {config.footprint_height}mm"
    )
    print(f"- Diode footprint size: {config.diode_width}mm x {config.diode_height}mm")
    print(
        f"- Diode offset from switch: ({config.diode_offset_x}mm, {config.diode_offset_y}mm)"
    )
    print(f"- Key spacing: {config.key_spacing}mm")
    print(f"- X pitch: {config.x_pitch}mm")
    print(f"- Y pitch: {config.y_pitch}mm")
    print(f"- Rows: {config.num_rows}")
    print(f"- Columns per half: {config.num_cols}")
    print(f"- Thumb keys per half: {config.num_thumb_keys}")
    print(f"- Thumb arc starts under column: {config.thumb_arc_col_start}")
    print(
        f"- Thumb arc: {config.thumb_arc_config.start_angle}° to {config.thumb_arc_config.end_angle}° (radius: {config.thumb_arc_config.radius}mm)"
    )
    print(
        f"- Thumb offset: ({config.thumb_arc_config.offset_x}mm, {config.thumb_arc_config.offset_y}mm)"
    )
    print(f"- Specific positions: {len(config.specific_positions)} components")

    # Generate positions
    positions = KeyboardLayoutCalculator.generate_all_positions(config)

    # Display all positions
    print_positions(config, positions)

    # Export files
    export_csv(positions)
    export_svg(config, positions, "keyboard_layout.svg")
    export_svg_for_footprints(config, positions, "keyboard_switches_cad.svg")
    export_svg_switch_plate(config, positions, "keyboard_switch_plate.svg")
    export_svg_mounting_holes(config, positions, "keyboard_mounting_holes.svg")
    export_svg_hotswap_profile(config, positions, "keyboard_hotswap_profile.svg")

    print("\nFiles generated:")
    print("- keyboard_positions.csv (CSV format)")
    print("- keyboard_layout.svg (SVG visualization)")
    print("- keyboard_switches_cad.svg (CAD-ready switch outlines)")
    print("- keyboard_switch_plate.svg (Switch plate holes and recesses)")
    print("- keyboard_mounting_holes.svg (Mounting holes for assembly)")
    print("- keyboard_hotswap_profile.svg (Hotswap socket profiles for CAD)")


if __name__ == "__main__":
    main()
