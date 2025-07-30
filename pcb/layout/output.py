#!/usr/bin/env python3
"""
Output utilities for keyboard layout calculator.

Contains functions for displaying and exporting keyboard layout positions.
"""

from typing import Dict, List, Tuple, Optional, NamedTuple
import svgwrite
from layout import KeyboardLayoutConfig, KeyboardLayoutCalculator


class CadSvgDimensions(NamedTuple):
    """Dimensions for CAD SVG export."""
    min_x_px: float
    min_y_px: float
    width_px: float
    height_px: float

# Constants for CAD export
# Conversion factor for Fusion 360: 1mm = 96/25.4 pixels (96 DPI)
FUSION_360_MM_TO_PX = 96.0 / 25.4
CAD_MARGIN = 20  # mm


def _calculate_cad_svg_dimensions(positions: Dict[str, Dict[str, List[Tuple[str, float, float, float]]]], config: KeyboardLayoutConfig) -> CadSvgDimensions:
    """
    Calculate SVG dimensions for CAD export using efficient approximation based on key switch positions.
    Uses the rightmost switch (SWR<num_cols>) x position + footprint width * 0.5 for width calculation,
    and the last right switch position + footprint height for height calculation.
    Top-left position is (0,0) before adding margin.

    Args:
        positions: Positions dictionary from generate_all_positions
        config: KeyboardLayoutConfig instance with layout parameters

    Returns:
        CadSvgDimensions with pixel coordinates for SVG creation
    """
    # Find the rightmost switch (SWR<num_cols>) position for width calculation
    # This is always at index (config.num_cols - 1) in the right switches list
    all_right_switches = positions["right"]["switches"]
    # Index num_cols-1 is the rightmost column
    rightmost_switch_position = all_right_switches[config.num_cols - 1]
    rightmost_switch_x = rightmost_switch_position[1]  # x coordinate

    # Find the last (bottommost) right switch for height calculation
    last_right_switch_y = max(y for _, x, y, r in all_right_switches)

    # Calculate bounds using efficient approximation method
    # Width: rightmost switch x position + footprint width * 0.5 gives us the approximate right edge
    switch_max_x = rightmost_switch_x + config.footprint_width * 0.5

    # Height: last right switch position + footprint height
    switch_max_y = last_right_switch_y + config.footprint_height

    # Top-left is (0,0) - the origin position
    switch_min_x = 0.0
    switch_min_y = 0.0

    # Add margin for clean viewing (in mm)
    min_x_mm = switch_min_x - CAD_MARGIN
    max_x_mm = switch_max_x + CAD_MARGIN
    min_y_mm = switch_min_y - CAD_MARGIN
    max_y_mm = switch_max_y + CAD_MARGIN

    width_mm = max_x_mm - min_x_mm
    height_mm = max_y_mm - min_y_mm

    # Convert to pixels for Fusion 360 compatibility
    min_x_px = min_x_mm * FUSION_360_MM_TO_PX
    min_y_px = min_y_mm * FUSION_360_MM_TO_PX
    width_px = width_mm * FUSION_360_MM_TO_PX
    height_px = height_mm * FUSION_360_MM_TO_PX

    return CadSvgDimensions(
        min_x_px=min_x_px,
        min_y_px=min_y_px,
        width_px=width_px,
        height_px=height_px
    )


def _create_cad_svg_drawing(filename: str, dimensions: CadSvgDimensions) -> svgwrite.Drawing:
    """
    Create SVG drawing with pixel units for Fusion 360 compatibility.

    Args:
        filename: Output SVG filename
        dimensions: CadSvgDimensions from _calculate_cad_svg_dimensions

    Returns:
        svgwrite.Drawing instance
    """
    return svgwrite.Drawing(filename, size=(f"{dimensions.width_px:.3f}px", f"{dimensions.height_px:.3f}px"), viewBox=f"{dimensions.min_x_px:.3f} {dimensions.min_y_px:.3f} {dimensions.width_px:.3f} {dimensions.height_px:.3f}")


def _add_coordinate_origin_marker(dwg: svgwrite.Drawing):
    """
    Add coordinate origin marker to SVG drawing.

    Args:
        dwg: svgwrite.Drawing instance
        stroke_color: Color for the origin marker
        stroke_width: Width of the origin marker strokes
    """
    stroke_color: str = "#000000"
    stroke_width: str = "0.1"
    origin_group = dwg.g()
    origin_group.add(dwg.circle(center=(0, 0), r=3.78, fill="none", stroke=stroke_color, stroke_width=stroke_width))
    origin_group.add(dwg.line(start=(-18.9, 0), end=(18.9, 0), stroke=stroke_color, stroke_width=stroke_width))
    origin_group.add(dwg.line(start=(0, -18.9), end=(0, 18.9), stroke=stroke_color, stroke_width=stroke_width))
    dwg.add(origin_group)


def _add_midpoint_separation_line(dwg: svgwrite.Drawing, positions: Dict[str, Dict[str, List[Tuple[str, float, float, float]]]], config: KeyboardLayoutConfig, dimensions: CadSvgDimensions):
    """
    Add midpoint separation line between left and right halves.

    Args:
        dwg: svgwrite.Drawing instance
        positions: Positions dictionary from generate_all_positions
        config: KeyboardLayoutConfig instance
        dimensions: CadSvgDimensions from _calculate_cad_svg_dimensions
    """
    left_switches = positions["left"]["switches"]
    right_switches = positions["right"]["switches"]

    # Find the rightmost x coordinate of left switches (in mm)
    left_max_x_mm = max(x + config.footprint_width / 2 for _, x, y, r in left_switches)

    # Find the leftmost x coordinate of right switches (in mm)
    right_min_x_mm = min(x - config.footprint_width / 2 for _, x, y, r in right_switches)

    # Calculate the midpoint (in mm, then convert to pixels)
    midpoint_x_mm = (left_max_x_mm + right_min_x_mm) / 2
    midpoint_x_px = midpoint_x_mm * FUSION_360_MM_TO_PX

    # Add midpoint separation line
    dwg.add(dwg.line(start=(midpoint_x_px, dimensions.min_y_px), end=(midpoint_x_px, dimensions.min_y_px + dimensions.height_px), stroke="#0066cc", stroke_width="0.57", stroke_dasharray="7.56,3.78"))


def print_positions(config: KeyboardLayoutConfig, positions: Dict[str, Dict[str, List[Tuple[str, float, float, float]]]]):
    """Print all key and diode positions in a readable format."""
    print("Keyboard Layout Positions (center coordinates in mm)")
    print("=" * 70)

    print("\nLeft Half:")
    print("-" * 45)
    for component_type, components in positions["left"].items():
        print(f"{component_type.capitalize()}:")
        for component_name, x, y, rotation in components:
            print(f"  {component_name}: ({x:6.2f}, {y:6.2f}, {rotation:6.1f}°)")

    print("\nRight Half:")
    print("-" * 45)
    for component_type, components in positions["right"].items():
        print(f"{component_type.capitalize()}:")
        for component_name, x, y, rotation in components:
            print(f"  {component_name}: ({x:6.2f}, {y:6.2f}, {rotation:6.1f}°)")


def export_csv(positions: Dict[str, Dict[str, List[Tuple[str, float, float, float]]]], filename: str = "keyboard_positions.csv"):
    """
    Export positions in CSV format.

    Args:
        positions: Positions dictionary from generate_all_positions
        filename: Output CSV filename
    """
    with open(filename, "w") as f:
        f.write("Reference,X(mm),Y(mm),Rotation(degrees),Half,Type\n")

        for key_name, x, y, rotation in positions["left"]["switches"]:
            f.write(f"{key_name},{x:.3f},{y:.3f},{rotation:.1f},Left,Switch\n")

        for diode_name, x, y, rotation in positions["left"]["diodes"]:
            f.write(f"{diode_name},{x:.3f},{y:.3f},{rotation:.1f},Left,Diode\n")

        # Add specific components for left half
        for component_type, components in positions["left"].items():
            if component_type not in ["switches", "diodes"]:
                for component_name, x, y, rotation in components:
                    f.write(f"{component_name},{x:.3f},{y:.3f},{rotation:.1f},Left,{component_type}\n")

        for key_name, x, y, rotation in positions["right"]["switches"]:
            f.write(f"{key_name},{x:.3f},{y:.3f},{rotation:.1f},Right,Switch\n")

        for diode_name, x, y, rotation in positions["right"]["diodes"]:
            f.write(f"{diode_name},{x:.3f},{y:.3f},{rotation:.1f},Right,Diode\n")

        # Add specific components for right half
        for component_type, components in positions["right"].items():
            if component_type not in ["switches", "diodes"]:
                for component_name, x, y, rotation in components:
                    f.write(f"{component_name},{x:.3f},{y:.3f},{rotation:.1f},Right,{component_type}\n")

    print(f"Positions exported to {filename}")


def export_svg(config: KeyboardLayoutConfig, positions: Dict[str, Dict[str, List[Tuple[str, float, float, float]]]], filename: str = "keyboard_layout.svg"):
    """
    Export positions as an SVG visualization.

    Args:
        config: KeyboardLayoutConfig instance with layout parameters
        positions: Positions dictionary from generate_all_positions
        filename: Output SVG filename
    """
    # Calculate SVG dimensions using efficient approximation (similar to CAD export but with different margins)
    # Find the rightmost switch (SWR<num_cols>) position for width calculation
    # This is always at index (config.num_cols - 1) in the right switches list
    all_right_switches = positions["right"]["switches"]
    rightmost_switch_position = all_right_switches[config.num_cols - 1]  # Index num_cols-1 is the rightmost column
    rightmost_switch_x = rightmost_switch_position[1]  # x coordinate
    
    # Find the last (bottommost) right switch for height calculation
    last_right_switch_y = max(y for _, x, y, r in all_right_switches)
    
    # Calculate base bounds using efficient approximation
    switch_max_x = rightmost_switch_x + config.footprint_width * 0.5
    switch_min_x = config.origin_x - config.footprint_width / 2
    switch_max_y = last_right_switch_y + config.footprint_height
    switch_min_y = config.origin_y - config.footprint_height / 2

    # Check if we need to extend bounds for diodes (quick check)
    all_diode_positions = positions["left"]["diodes"] + positions["right"]["diodes"]
    if all_diode_positions:
        # Just check a few key diodes instead of all of them
        sample_diode_x = all_diode_positions[0][1]  # First diode x position
        if sample_diode_x - config.diode_width / 2 < switch_min_x:
            switch_min_x = sample_diode_x - config.diode_width / 2
        if sample_diode_x + config.diode_width / 2 > switch_max_x:
            switch_max_x = sample_diode_x + config.diode_width / 2

    # Check for specific components that might extend bounds
    for half in ["left", "right"]:
        for component_type, components in positions[half].items():
            if component_type not in ["switches", "diodes"] and components:
                # Just check first component of each type as representative
                x, y = components[0][1], components[0][2]
                component_margin = 2  # 2mm margin for components
                switch_min_x = min(switch_min_x, x - component_margin)
                switch_max_x = max(switch_max_x, x + component_margin)
                switch_min_y = min(switch_min_y, y - component_margin)
                switch_max_y = max(switch_max_y, y + component_margin)

    # Add visualization margins (different from CAD margins)
    min_x = switch_min_x - 10
    max_x = switch_max_x + 10
    min_y = switch_min_y - 25  # More space at top for title
    max_y = switch_max_y + 10  # Less space at bottom

    width = max_x - min_x
    height = max_y - min_y

    # Create SVG drawing (using mm units for visualization)
    dwg = svgwrite.Drawing(filename, size=(f"{width:.1f}mm", f"{height:.1f}mm"), viewBox=f"{min_x:.1f} {min_y:.1f} {width:.1f} {height:.1f}")

    # Add background
    dwg.add(dwg.rect(insert=(min_x, min_y), size=(width, height), fill="#f8f9fa", stroke="none"))

    # Add grid pattern
    grid_pattern = dwg.defs.add(dwg.pattern(id="grid", patternUnits="userSpaceOnUse", size=(10, 10)))
    grid_pattern.add(dwg.path(d="M 10 0 L 0 0 0 10", fill="none", stroke="#e9ecef", stroke_width=0.5))

    # Apply grid to background
    dwg.add(dwg.rect(insert=(min_x, min_y), size=(width, height), fill="url(#grid)"))

    # Add title
    dwg.add(dwg.text("Split Column Staggered Keyboard Layout", insert=((min_x + max_x) / 2, min_y + 8), text_anchor="middle", font_family="Arial, sans-serif", font_size="4", fill="#212529", font_weight="bold"))

    # Add half labels
    dwg.add(dwg.text("Left Half", insert=(36, min_y + 18), text_anchor="middle", font_family="Arial, sans-serif", font_size="3", fill="#6c757d"))

    dwg.add(dwg.text("Right Half", insert=(155, min_y + 18), text_anchor="middle", font_family="Arial, sans-serif", font_size="3", fill="#6c757d"))

    # Add key rectangles and labels for left half
    for key_name, x, y, rotation in positions["left"]["switches"]:
        # Use same color for all left switches
        fill_color = "#e3f2fd"
        stroke_color = "#1976d2"
        text_color = "#1976d2"

        if abs(rotation) < 0.1:  # No rotation for main keys
            # Add switch rectangle
            dwg.add(dwg.rect(insert=(x - config.footprint_width / 2, y - config.footprint_height / 2), size=(config.footprint_width, config.footprint_height), fill=fill_color, stroke=stroke_color, stroke_width=0.01))
            # Add label
            dwg.add(dwg.text(key_name, insert=(x, y + 1), text_anchor="middle", font_family="Arial, sans-serif", font_size="2.5", fill=text_color, font_weight="bold"))
        else:  # Rotated thumb keys
            group = dwg.g(transform=f"translate({x:.1f},{y:.1f}) rotate({rotation:.1f})")
            group.add(dwg.rect(insert=(-config.footprint_width / 2, -config.footprint_height / 2), size=(config.footprint_width, config.footprint_height), fill=fill_color, stroke=stroke_color, stroke_width=0.01))
            group.add(dwg.text(key_name, insert=(0, 1), text_anchor="middle", font_family="Arial, sans-serif", font_size="2.5", fill=text_color, font_weight="bold"))
            dwg.add(group)

    # Add diode rectangles and labels for left half
    for diode_name, x, y, rotation in positions["left"]["diodes"]:
        # Use same color for all left diodes
        fill_color = "#a8dadc"
        stroke_color = "#457b9d"
        text_color = "#1d3557"

        if abs(rotation) < 0.1:  # No rotation for main keys
            # Add diode rectangle
            dwg.add(dwg.rect(insert=(x - config.diode_width / 2, y - config.diode_height / 2), size=(config.diode_width, config.diode_height), fill=fill_color, stroke=stroke_color, stroke_width=0.1))
            # Add label
            dwg.add(dwg.text(diode_name, insert=(x, y + 0.5), text_anchor="middle", font_family="Arial, sans-serif", font_size="1.5", fill=text_color, font_weight="bold"))
        else:  # Rotated thumb diodes
            group = dwg.g(transform=f"translate({x:.1f},{y:.1f}) rotate({rotation:.1f})")
            group.add(dwg.rect(insert=(-config.diode_width / 2, -config.diode_height / 2), size=(config.diode_width, config.diode_height), fill=fill_color, stroke=stroke_color, stroke_width=0.1))
            group.add(dwg.text(diode_name, insert=(0, 0.5), text_anchor="middle", font_family="Arial, sans-serif", font_size="1.5", fill=text_color, font_weight="bold"))
            dwg.add(group)

    # Add key rectangles and labels for right half
    for key_name, x, y, rotation in positions["right"]["switches"]:
        # Use same color for all right switches
        fill_color = "#f3e5f5"
        stroke_color = "#7b1fa2"
        text_color = "#7b1fa2"

        if abs(rotation) < 0.1:  # No rotation for main keys
            # Add switch rectangle
            dwg.add(dwg.rect(insert=(x - config.footprint_width / 2, y - config.footprint_height / 2), size=(config.footprint_width, config.footprint_height), fill=fill_color, stroke=stroke_color, stroke_width=0.01))
            # Add label
            dwg.add(dwg.text(key_name, insert=(x, y + 1), text_anchor="middle", font_family="Arial, sans-serif", font_size="2.5", fill=text_color, font_weight="bold"))
        else:  # Rotated thumb keys
            group = dwg.g(transform=f"translate({x:.1f},{y:.1f}) rotate({rotation:.1f})")
            group.add(dwg.rect(insert=(-config.footprint_width / 2, -config.footprint_height / 2), size=(config.footprint_width, config.footprint_height), fill=fill_color, stroke=stroke_color, stroke_width=0.01))
            group.add(dwg.text(key_name, insert=(0, 1), text_anchor="middle", font_family="Arial, sans-serif", font_size="2.5", fill=text_color, font_weight="bold"))
            dwg.add(group)

    # Add diode rectangles and labels for right half
    for diode_name, x, y, rotation in positions["right"]["diodes"]:
        # Use same color for all right diodes
        fill_color = "#dda0dd"
        stroke_color = "#9a031e"
        text_color = "#5f0a87"

        if abs(rotation) < 0.1:  # No rotation for main keys
            # Add diode rectangle
            dwg.add(dwg.rect(insert=(x - config.diode_width / 2, y - config.diode_height / 2), size=(config.diode_width, config.diode_height), fill=fill_color, stroke=stroke_color, stroke_width=0.1))
            # Add label
            dwg.add(dwg.text(diode_name, insert=(x, y + 0.5), text_anchor="middle", font_family="Arial, sans-serif", font_size="1.5", fill=text_color, font_weight="bold"))
        else:  # Rotated thumb diodes
            group = dwg.g(transform=f"translate({x:.1f},{y:.1f}) rotate({rotation:.1f})")
            group.add(dwg.rect(insert=(-config.diode_width / 2, -config.diode_height / 2), size=(config.diode_width, config.diode_height), fill=fill_color, stroke=stroke_color, stroke_width=0.1))
            group.add(dwg.text(diode_name, insert=(0, 0.5), text_anchor="middle", font_family="Arial, sans-serif", font_size="1.5", fill=text_color, font_weight="bold"))
            dwg.add(group)

    # Add specific components for both halves
    for half in ["left", "right"]:
        for component_type, components in positions[half].items():
            if component_type not in ["switches", "diodes"]:
                # Choose color based on component type
                if component_type == "MCU":
                    fill_color = "#ff6b35"
                    stroke_color = "#d63031"
                    text_color = "#2d3436"
                elif component_type == "HOLE":
                    fill_color = "#636e72"
                    stroke_color = "#2d3436"
                    text_color = "#2d3436"
                elif component_type == "BAT":
                    fill_color = "#00b894"
                    stroke_color = "#00a085"
                    text_color = "#2d3436"
                elif component_type == "RSW":
                    fill_color = "#e17055"
                    stroke_color = "#d63031"
                    text_color = "#2d3436"
                else:
                    fill_color = "#74b9ff"
                    stroke_color = "#0984e3"
                    text_color = "#2d3436"

                for component_name, x, y, rotation in components:
                    if component_type == "HOLE":
                        # Make holes 3mm circles (radius = 1.5mm)
                        dwg.add(dwg.circle(center=(x, y), r=1.5, fill=fill_color, stroke=stroke_color, stroke_width=0.1))
                        dwg.add(dwg.text(component_name, insert=(x, y - 3), text_anchor="middle", font_family="Arial, sans-serif", font_size="2", fill=text_color, font_weight="bold"))
                    else:
                        # Make all other components small dots (radius = 0.5mm)
                        dwg.add(dwg.circle(center=(x, y), r=0.5, fill=fill_color, stroke=stroke_color, stroke_width=0.1))
                        dwg.add(dwg.text(component_name, insert=(x, y - 2), text_anchor="middle", font_family="Arial, sans-serif", font_size="1.5", fill=text_color, font_weight="bold"))

    # Add thumb arc origins
    # Calculate left thumb arc origin
    ref_x, ref_y = KeyboardLayoutCalculator.calculate_left_position(config, config.num_rows - 1, config.thumb_arc_col_start)
    left_origin_x = ref_x + config.thumb_arc_config.offset_x
    left_origin_y = ref_y + config.thumb_arc_config.offset_y + config.thumb_arc_config.radius

    # Calculate right thumb arc origin by mirroring the left origin
    right_origin_x, right_origin_y = KeyboardLayoutCalculator.mirror_position(config, left_origin_x, left_origin_y)

    # Add left thumb arc origin marker
    dwg.add(dwg.circle(center=(left_origin_x, left_origin_y), r=0.5, fill="#d32f2f", stroke="#b71c1c", stroke_width=0.1))
    dwg.add(dwg.circle(center=(left_origin_x, left_origin_y), r=3, fill="none", stroke="#d32f2f", stroke_width=0.05, stroke_dasharray="0.5,0.5"))
    dwg.add(dwg.text("L-ARC", insert=(left_origin_x, left_origin_y - 4), text_anchor="middle", font_family="Arial, sans-serif", font_size="1.5", fill="#d32f2f", font_weight="bold"))

    # Add right thumb arc origin marker
    dwg.add(dwg.circle(center=(right_origin_x, right_origin_y), r=0.5, fill="#d32f2f", stroke="#b71c1c", stroke_width=0.1))
    dwg.add(dwg.circle(center=(right_origin_x, right_origin_y), r=3, fill="none", stroke="#d32f2f", stroke_width=0.05, stroke_dasharray="0.5,0.5"))
    dwg.add(dwg.text("R-ARC", insert=(right_origin_x, right_origin_y - 4), text_anchor="middle", font_family="Arial, sans-serif", font_size="1.5", fill="#d32f2f", font_weight="bold"))

    # Add coordinate origin (0,0)
    origin_group = dwg.g()
    origin_group.add(dwg.circle(center=(0, 0), r=0.5, fill="#ff4444", stroke="#cc0000", stroke_width=0.1))
    origin_group.add(dwg.circle(center=(0, 0), r=5, fill="none", stroke="#ff4444", stroke_width=0.05, stroke_dasharray="1,1"))
    origin_group.add(dwg.line(start=(-10, 0), end=(10, 0), stroke="#ff4444", stroke_width=0.1))
    origin_group.add(dwg.line(start=(0, -10), end=(0, 10), stroke="#ff4444", stroke_width=0.1))
    origin_group.add(dwg.text("ORIGIN", insert=(0, -7), text_anchor="middle", font_family="Arial, sans-serif", font_size="2", fill="#ff4444", font_weight="bold"))
    origin_group.add(dwg.text("(0.0, 0.0)", insert=(0, 10), text_anchor="middle", font_family="Arial, sans-serif", font_size="1.5", fill="#666666"))
    dwg.add(origin_group)

    # Save the SVG
    dwg.save()
    print(f"SVG visualization exported to {filename}")


def export_svg_for_footprints(config: KeyboardLayoutConfig, positions: Dict[str, Dict[str, List[Tuple[str, float, float, float]]]], filename: str = "keyboard_switches_cad.svg"):
    """
    Export switch outlines and origin as a clean SVG for CAD import (e.g., Fusion 360).

    Args:
        config: KeyboardLayoutConfig instance with layout parameters
        positions: Positions dictionary from generate_all_positions
        filename: Output SVG filename
    """
    # Calculate SVG dimensions
    dimensions = _calculate_cad_svg_dimensions(positions, config)

    # Create SVG drawing
    dwg = _create_cad_svg_drawing(filename, dimensions)

    # Add switch rectangles for both halves
    for half in ["left", "right"]:
        for key_name, x, y, rotation in positions[half]["switches"]:
            # Convert mm coordinates to pixels
            x_px = x * FUSION_360_MM_TO_PX
            y_px = y * FUSION_360_MM_TO_PX
            width_px_rect = config.footprint_width * FUSION_360_MM_TO_PX
            height_px_rect = config.footprint_height * FUSION_360_MM_TO_PX

            if abs(rotation) < 0.1:  # No rotation for main keys
                # Add switch outline rectangle
                dwg.add(dwg.rect(insert=(x_px - width_px_rect / 2, y_px - height_px_rect / 2), size=(width_px_rect, height_px_rect), fill="none", stroke="#000000", stroke_width="0.38"))
            else:  # Rotated thumb keys
                # Create group for rotation
                group = dwg.g(transform=f"translate({x_px:.3f},{y_px:.3f}) rotate({rotation:.3f})")
                group.add(dwg.rect(insert=(-width_px_rect / 2, -height_px_rect / 2), size=(width_px_rect, height_px_rect), fill="none", stroke="#000000", stroke_width="0.38"))
                dwg.add(group)

    # Add midpoint separation line
    _add_midpoint_separation_line(dwg, positions, config, dimensions)

    # Add coordinate origin marker
    _add_coordinate_origin_marker(dwg)

    # Save the SVG
    dwg.save()
    print(f"CAD-ready SVG exported to {filename}")


def export_svg_switch_plate(config: KeyboardLayoutConfig, positions: Dict[str, Dict[str, List[Tuple[str, float, float, float]]]], filename: str = "keyboard_switch_plate.svg"):
    """
    Export switch plate hole and recess positions for CAD import (e.g., Fusion 360).
    Creates 14mm (hole) and 16mm (recess) squares centered on each switch position.
    Minimal SVG with black hairline strokes for clean CAD import.

    Args:
        config: KeyboardLayoutConfig instance with layout parameters
        positions: Positions dictionary from generate_all_positions
        filename: Output SVG filename
    """
    # Calculate SVG dimensions
    dimensions = _calculate_cad_svg_dimensions(positions, config)

    # Create SVG drawing
    dwg = _create_cad_svg_drawing(filename, dimensions)

    # Add switch plate holes and recesses for both halves
    for half in ["left", "right"]:
        for key_name, x, y, rotation in positions[half]["switches"]:
            # Convert mm coordinates to pixels
            x_px = x * FUSION_360_MM_TO_PX
            y_px = y * FUSION_360_MM_TO_PX

            # Hole and recess dimensions in pixels
            hole_14_px = 14.0 * FUSION_360_MM_TO_PX
            recess_16_px = 16.0 * FUSION_360_MM_TO_PX

            if abs(rotation) < 0.1:  # No rotation for main keys
                # 16mm recess (outer rectangle)
                dwg.add(dwg.rect(insert=(x_px - recess_16_px / 2, y_px - recess_16_px / 2), size=(recess_16_px, recess_16_px), fill="none", stroke="#000000", stroke_width="0.1"))

                # 14mm hole (inner rectangle)
                dwg.add(dwg.rect(insert=(x_px - hole_14_px / 2, y_px - hole_14_px / 2), size=(hole_14_px, hole_14_px), fill="none", stroke="#000000", stroke_width="0.1"))
            else:  # Rotated thumb keys
                # Create group for rotation
                group = dwg.g(transform=f"translate({x_px:.3f},{y_px:.3f}) rotate({rotation:.3f})")

                # 16mm recess (outer rectangle)
                group.add(dwg.rect(insert=(-recess_16_px / 2, -recess_16_px / 2), size=(recess_16_px, recess_16_px), fill="none", stroke="#000000", stroke_width="0.1"))

                # 14mm hole (inner rectangle)
                group.add(dwg.rect(insert=(-hole_14_px / 2, -hole_14_px / 2), size=(hole_14_px, hole_14_px), fill="none", stroke="#000000", stroke_width="0.1"))

                dwg.add(group)

    # Add coordinate origin marker
    _add_coordinate_origin_marker(dwg)

    # Save the SVG
    dwg.save()
    print(f"Switch plate SVG exported to {filename}")


def export_svg_bottom_plate_recesses(config: KeyboardLayoutConfig, positions: Dict[str, Dict[str, List[Tuple[str, float, float, float]]]], filename: str = "keyboard_hotswap_profile.svg"):
    """
    Export hotswap socket profiles and mounting holes positioned relative to switch centers for CAD import (e.g., Fusion 360).
    Includes hotswap profiles, 3mm center mounting holes, and 2.2mm right-side mounting holes (x+ 5.22mm offset).

    Args:
        config: KeyboardLayoutConfig instance with layout parameters
        positions: Positions dictionary from generate_all_positions
        filename: Output SVG filename
    """
    # Hotswap profile offset from switch center (in mm)
    hotswap_offset_x = -1.413  # x - 1.413 mm
    hotswap_offset_y = 3.625  # y + 3.625 mm

    # Hotswap profile dimensions (from original SVG)
    hotswap_width = 13.4  # mm
    hotswap_height = 9.45  # mm

    # Mounting hole dimensions
    offset_distance = 5.22  # mm
    center_radius = 1.5  # mm (3mm diameter / 2)
    side_radius = 1.1  # mm (2.2mm diameter / 2)
    total_reach = offset_distance + side_radius

    # Calculate SVG dimensions
    dimensions = _calculate_cad_svg_dimensions(positions, config)

    # Create SVG drawing
    dwg = _create_cad_svg_drawing(filename, dimensions)

    # Define the hotswap profile paths (converted from the original SVG)
    # These paths are relative to the center of the hotswap profile
    def add_hotswap_profile(dwg, center_x_px, center_y_px, rotation=0):
        """Add a hotswap profile centered at the given pixel coordinates."""

        # Create group for rotation and positioning
        if abs(rotation) < 0.1:
            # No rotation
            group = dwg.g(transform=f"translate({center_x_px:.3f},{center_y_px:.3f})")
        else:
            # With rotation
            group = dwg.g(transform=f"translate({center_x_px:.3f},{center_y_px:.3f}) rotate({rotation:.3f})")

        # Main hotswap socket body path (scaled to pixels and centered)
        path1_d = f"""m {(6.000002 - 6.7) * FUSION_360_MM_TO_PX:.3f},{(2.0998362 - 4.725) * FUSION_360_MM_TO_PX:.3f} 
                     a {1.251812 * FUSION_360_MM_TO_PX:.3f},{1.251812 * FUSION_360_MM_TO_PX:.3f} 0 0 1 {1.1936531 * FUSION_360_MM_TO_PX:.3f},{0.87468 * FUSION_360_MM_TO_PX:.3f} 
                     {1.859393 * FUSION_360_MM_TO_PX:.3f},{1.859393 * FUSION_360_MM_TO_PX:.3f} 0 0 0 {1.4758169 * FUSION_360_MM_TO_PX:.3f},{1.275316 * FUSION_360_MM_TO_PX:.3f} 
                     h {1.856266 * FUSION_360_MM_TO_PX:.3f} 
                     a {0.55 * FUSION_360_MM_TO_PX:.3f},{0.55 * FUSION_360_MM_TO_PX:.3f} 0 0 1 {0.38891 * FUSION_360_MM_TO_PX:.3f},{0.16109 * FUSION_360_MM_TO_PX:.3f} 
                     l {0.67426 * FUSION_360_MM_TO_PX:.3f},{0.67426 * FUSION_360_MM_TO_PX:.3f} 
                     a {0.55 * FUSION_360_MM_TO_PX:.3f},{0.55 * FUSION_360_MM_TO_PX:.3f} 0 0 1 {0.16109 * FUSION_360_MM_TO_PX:.3f},{0.38891 * FUSION_360_MM_TO_PX:.3f} 
                     v {0.27574 * FUSION_360_MM_TO_PX:.3f} 
                     h {1.65 * FUSION_360_MM_TO_PX:.3f} 
                     v {2.2 * FUSION_360_MM_TO_PX:.3f} 
                     h {-1.65 * FUSION_360_MM_TO_PX:.3f} 
                     v {0.27574 * FUSION_360_MM_TO_PX:.3f} 
                     a {0.55 * FUSION_360_MM_TO_PX:.3f},{0.55 * FUSION_360_MM_TO_PX:.3f} 0 0 1 {-0.16109 * FUSION_360_MM_TO_PX:.3f},{0.38891 * FUSION_360_MM_TO_PX:.3f} 
                     l {-0.67426 * FUSION_360_MM_TO_PX:.3f},{0.67426 * FUSION_360_MM_TO_PX:.3f} 
                     a {0.55 * FUSION_360_MM_TO_PX:.3f},{0.55 * FUSION_360_MM_TO_PX:.3f} 0 0 1 {-0.38891 * FUSION_360_MM_TO_PX:.3f},{0.16109 * FUSION_360_MM_TO_PX:.3f} 
                     H {(7.7742661 - 6.7) * FUSION_360_MM_TO_PX:.3f} 
                     a {0.55 * FUSION_360_MM_TO_PX:.3f},{0.55 * FUSION_360_MM_TO_PX:.3f} 0 0 1 {-0.38891 * FUSION_360_MM_TO_PX:.3f},{-0.16109 * FUSION_360_MM_TO_PX:.3f} 
                     l {-0.67426 * FUSION_360_MM_TO_PX:.3f},{-0.67426 * FUSION_360_MM_TO_PX:.3f} 
                     a {0.55 * FUSION_360_MM_TO_PX:.3f},{0.55 * FUSION_360_MM_TO_PX:.3f} 0 0 1 {-0.16109 * FUSION_360_MM_TO_PX:.3f},{-0.38891 * FUSION_360_MM_TO_PX:.3f} 
                     v {-0.16423 * FUSION_360_MM_TO_PX:.3f} 
                     A {0.954545 * FUSION_360_MM_TO_PX:.3f},{0.954545 * FUSION_360_MM_TO_PX:.3f} 0 0 0 {(5.600006 - 6.7) * FUSION_360_MM_TO_PX:.3f},{(7.1998422 - 4.725) * FUSION_360_MM_TO_PX:.3f} 
                     H {(2.7000061 - 6.7) * FUSION_360_MM_TO_PX:.3f} 
                     a {1.05 * FUSION_360_MM_TO_PX:.3f},{1.05 * FUSION_360_MM_TO_PX:.3f} 0 0 1 {-1.05 * FUSION_360_MM_TO_PX:.3f},{-1.05 * FUSION_360_MM_TO_PX:.3f} 
                     v {-0.4 * FUSION_360_MM_TO_PX:.3f} 
                     H {(3.1e-6 - 6.7) * FUSION_360_MM_TO_PX:.3f} 
                     v {-2.2 * FUSION_360_MM_TO_PX:.3f} 
                     h {1.649999 * FUSION_360_MM_TO_PX:.3f} 
                     v {-0.4 * FUSION_360_MM_TO_PX:.3f} 
                     a {1.05 * FUSION_360_MM_TO_PX:.3f},{1.05 * FUSION_360_MM_TO_PX:.3f} 0 0 1 {1.05 * FUSION_360_MM_TO_PX:.3f},{-1.05 * FUSION_360_MM_TO_PX:.3f} 
                     h {0.23 * FUSION_360_MM_TO_PX:.3f} {2.1999999 * FUSION_360_MM_TO_PX:.3f} z"""

        group.add(dwg.path(d=path1_d, fill="none", stroke="#000000", stroke_width="0.1", stroke_linecap="round", stroke_linejoin="round"))

        # Secondary path (left switch mount)
        path2_d = f"""m {(5.130002 - 6.7) * FUSION_360_MM_TO_PX:.3f},{(2.0998362 - 4.725) * FUSION_360_MM_TO_PX:.3f} 
                     v {-1 * FUSION_360_MM_TO_PX:.3f} 
                     a {1.1 * FUSION_360_MM_TO_PX:.3f},{1.1 * FUSION_360_MM_TO_PX:.3f} 0 0 0 {-2.1999999 * FUSION_360_MM_TO_PX:.3f},0 
                     v {1 * FUSION_360_MM_TO_PX:.3f} z"""

        group.add(dwg.path(d=path2_d, fill="none", stroke="#000000", stroke_width="0.1", stroke_linecap="round", stroke_linejoin="round"))

        dwg.add(group)

    def add_diode_recess(dwg, center_x_px, center_y_px, rotation=0):
        """Add a pill-shaped diode recess centered at the given pixel coordinates.
        
        The pill shape consists of:
        - A rectangular center section (3.4mm tall)
        - Semicircles at top and bottom (2.4mm diameter)
        - Total height: 5.8mm
        - Oriented vertically with semicircles at top and bottom
        """
        # Diode recess dimensions in mm
        box_height = 3.4  # mm
        semicircle_diameter = 2.4  # mm
        semicircle_radius = semicircle_diameter / 2  # 1.2 mm
        total_height = 5.8  # mm (box_height + semicircle_diameter)
        pill_width = 2.4  # mm (width equals semicircle diameter)
        
        # Convert to pixels
        box_height_px = box_height * FUSION_360_MM_TO_PX
        radius_px = semicircle_radius * FUSION_360_MM_TO_PX
        total_height_px = total_height * FUSION_360_MM_TO_PX
        half_width_px = radius_px  # Half width equals radius
        
        # Create group for rotation and positioning
        # Add 90 degrees to the rotation to align with diode orientation
        effective_rotation = rotation + 90
        if abs(effective_rotation) < 0.1:
            # No rotation
            group = dwg.g(transform=f"translate({center_x_px:.3f},{center_y_px:.3f})")
        else:
            # With rotation
            group = dwg.g(transform=f"translate({center_x_px:.3f},{center_y_px:.3f}) rotate({effective_rotation:.3f})")
        
        # Calculate positions for the pill shape
        # The box extends from -box_height/2 to +box_height/2
        # The semicircles are centered at the top and bottom of the box
        box_half_height = box_height_px / 2
        top_semicircle_center_y = -box_half_height
        bottom_semicircle_center_y = box_half_height
        
        # Create a single path for the complete pill shape
        # Start at the leftmost point of the top semicircle
        path_d = f"M {-half_width_px:.3f},{top_semicircle_center_y:.3f}"
        
        # Top semicircle (left to right)
        path_d += f" A {radius_px:.3f},{radius_px:.3f} 0 0,1 {half_width_px:.3f},{top_semicircle_center_y:.3f}"
        
        # Right vertical line down to bottom semicircle
        path_d += f" L {half_width_px:.3f},{bottom_semicircle_center_y:.3f}"
        
        # Bottom semicircle (right to left)
        path_d += f" A {radius_px:.3f},{radius_px:.3f} 0 0,1 {-half_width_px:.3f},{bottom_semicircle_center_y:.3f}"
        
        # Left vertical line back up to complete the shape
        path_d += f" L {-half_width_px:.3f},{top_semicircle_center_y:.3f} Z"
        
        # Add the complete pill shape as a single path
        group.add(dwg.path(
            d=path_d,
            fill="none",
            stroke="#000000",
            stroke_width="0.1",
            stroke_linecap="round",
            stroke_linejoin="round"
        ))
        
        dwg.add(group)

    # Add hotswap profiles for both halves
    for half in ["left", "right"]:
        for key_name, x, y, rotation in positions[half]["switches"]:
            # Calculate hotswap center position
            hotswap_x = x + hotswap_offset_x
            hotswap_y = y + hotswap_offset_y

            # Convert mm coordinates to pixels
            hotswap_x_px = hotswap_x * FUSION_360_MM_TO_PX
            hotswap_y_px = hotswap_y * FUSION_360_MM_TO_PX

            # Add hotswap profile
            add_hotswap_profile(dwg, hotswap_x_px, hotswap_y_px, rotation)

    # Add mounting holes for both halves
    for half in ["left", "right"]:
        for key_name, x, y, rotation in positions[half]["switches"]:
            # Convert mm coordinates to pixels
            x_px = x * FUSION_360_MM_TO_PX
            y_px = y * FUSION_360_MM_TO_PX

            # Circle dimensions in pixels
            center_diameter_px = 3.0 * FUSION_360_MM_TO_PX
            side_diameter_px = 2.2 * FUSION_360_MM_TO_PX
            offset_distance_px = offset_distance * FUSION_360_MM_TO_PX

            if abs(rotation) < 0.1:  # No rotation for main keys
                # 3mm circle at center
                dwg.add(dwg.circle(center=(x_px, y_px), r=center_diameter_px / 2, fill="none", stroke="#000000", stroke_width="0.1"))

                # 2.2mm circle at x + 5.22mm (only right side, removed left side as requested)
                dwg.add(dwg.circle(center=(x_px + offset_distance_px, y_px), r=side_diameter_px / 2, fill="none", stroke="#000000", stroke_width="0.1"))
            else:  # Rotated thumb keys
                # Create group for rotation
                group = dwg.g(transform=f"translate({x_px:.3f},{y_px:.3f}) rotate({rotation:.3f})")

                # 3mm circle at center
                group.add(dwg.circle(center=(0, 0), r=center_diameter_px / 2, fill="none", stroke="#000000", stroke_width="0.1"))

                # 2.2mm circle at x + 5.22mm (only right side, removed left side as requested)
                group.add(dwg.circle(center=(offset_distance_px, 0), r=side_diameter_px / 2, fill="none", stroke="#000000", stroke_width="0.1"))

                dwg.add(group)

    # Add diode recesses for both halves
    for half in ["left", "right"]:
        for diode_name, x, y, rotation in positions[half]["diodes"]:
            # Convert mm coordinates to pixels
            x_px = x * FUSION_360_MM_TO_PX
            y_px = y * FUSION_360_MM_TO_PX

            # Add diode recess
            add_diode_recess(dwg, x_px, y_px, rotation)

    # Add midpoint separation line
    _add_midpoint_separation_line(dwg, positions, config, dimensions)

    # Add coordinate origin marker
    _add_coordinate_origin_marker(dwg)

    # Save the SVG
    dwg.save()
    print(f"Hotswap profile with mounting holes SVG exported to {filename}")
