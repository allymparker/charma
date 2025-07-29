#!/usr/bin/env python3
"""
Output utilities for keyboard layout calculator.

Contains functions for displaying and exporting keyboard layout positions.
"""

from typing import Dict, List, Tuple
import svgwrite
from layout import KeyboardLayoutConfig, KeyboardLayoutCalculator


def print_positions(config: KeyboardLayoutConfig, positions: Dict[str, Dict[str, List[Tuple[str, float, float, float]]]]):
    """Print all key and diode positions in a readable format."""
    print("Keyboard Layout Positions (center coordinates in mm)")
    print("=" * 70)
    
    print("\nLeft Half:")
    print("-" * 45)
    for component_type, components in positions['left'].items():
        print(f"{component_type.capitalize()}:")
        for component_name, x, y, rotation in components:
            print(f"  {component_name}: ({x:6.2f}, {y:6.2f}, {rotation:6.1f}°)")
    
    print("\nRight Half:")
    print("-" * 45)
    for component_type, components in positions['right'].items():
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
    with open(filename, 'w') as f:
        f.write("Reference,X(mm),Y(mm),Rotation(degrees),Half,Type\n")
        
        for key_name, x, y, rotation in positions['left']['switches']:
            f.write(f"{key_name},{x:.3f},{y:.3f},{rotation:.1f},Left,Switch\n")
        
        for diode_name, x, y, rotation in positions['left']['diodes']:
            f.write(f"{diode_name},{x:.3f},{y:.3f},{rotation:.1f},Left,Diode\n")
        
        # Add specific components for left half
        for component_type, components in positions['left'].items():
            if component_type not in ['switches', 'diodes']:
                for component_name, x, y, rotation in components:
                    f.write(f"{component_name},{x:.3f},{y:.3f},{rotation:.1f},Left,{component_type}\n")
        
        for key_name, x, y, rotation in positions['right']['switches']:
            f.write(f"{key_name},{x:.3f},{y:.3f},{rotation:.1f},Right,Switch\n")
        
        for diode_name, x, y, rotation in positions['right']['diodes']:
            f.write(f"{diode_name},{x:.3f},{y:.3f},{rotation:.1f},Right,Diode\n")
        
        # Add specific components for right half
        for component_type, components in positions['right'].items():
            if component_type not in ['switches', 'diodes']:
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
    # Calculate SVG dimensions (accounting for center coordinates and rotation)
    all_switch_positions = positions['left']['switches'] + positions['right']['switches']
    all_diode_positions = positions['left']['diodes'] + positions['right']['diodes']
    
    # Collect all specific component positions
    all_specific_positions = []
    for half in ['left', 'right']:
        for component_type, components in positions[half].items():
            if component_type not in ['switches', 'diodes']:
                all_specific_positions.extend(components)
    
    # Calculate bounds considering switches, diodes, and specific components
    switch_min_x = min(x - config.footprint_width/2 for _, x, y, r in all_switch_positions)
    switch_max_x = max(x + config.footprint_width/2 for _, x, y, r in all_switch_positions)
    switch_min_y = min(y - config.footprint_height/2 for _, x, y, r in all_switch_positions)
    switch_max_y = max(y + config.footprint_height/2 for _, x, y, r in all_switch_positions)
    
    diode_min_x = min(x - config.diode_width/2 for _, x, y, r in all_diode_positions)
    diode_max_x = max(x + config.diode_width/2 for _, x, y, r in all_diode_positions)
    diode_min_y = min(y - config.diode_height/2 for _, x, y, r in all_diode_positions)
    diode_max_y = max(y + config.diode_height/2 for _, x, y, r in all_diode_positions)
    
    # Include specific components in bounds calculation
    if all_specific_positions:
        specific_min_x = min(x - 2 for _, x, y, r in all_specific_positions)  # 2mm margin for dot
        specific_max_x = max(x + 2 for _, x, y, r in all_specific_positions)
        specific_min_y = min(y - 2 for _, x, y, r in all_specific_positions)
        specific_max_y = max(y + 2 for _, x, y, r in all_specific_positions)
        
        min_x = min(switch_min_x, diode_min_x, specific_min_x) - 10
        max_x = max(switch_max_x, diode_max_x, specific_max_x) + 10
        min_y = min(switch_min_y, diode_min_y, specific_min_y) - 25  # More space at top
        max_y = max(switch_max_y, diode_max_y, specific_max_y) + 10  # Less space at bottom
    else:
        min_x = min(switch_min_x, diode_min_x) - 10
        max_x = max(switch_max_x, diode_max_x) + 10
        min_y = min(switch_min_y, diode_min_y) - 25  # More space at top
        max_y = max(switch_max_y, diode_max_y) + 10  # Less space at bottom (no legend)
    
    width = max_x - min_x
    height = max_y - min_y
    
    # Create SVG drawing (using mm units for visualization)
    dwg = svgwrite.Drawing(
        filename,
        size=(f'{width:.1f}mm', f'{height:.1f}mm'),
        viewBox=f'{min_x:.1f} {min_y:.1f} {width:.1f} {height:.1f}'
    )
    
    # Add background
    dwg.add(dwg.rect(
        insert=(min_x, min_y),
        size=(width, height),
        fill='#f8f9fa',
        stroke='none'
    ))
    
    # Add grid pattern
    grid_pattern = dwg.defs.add(dwg.pattern(
        id='grid',
        patternUnits='userSpaceOnUse',
        size=(10, 10)
    ))
    grid_pattern.add(dwg.path(
        d='M 10 0 L 0 0 0 10',
        fill='none',
        stroke='#e9ecef',
        stroke_width=0.5
    ))
    
    # Apply grid to background
    dwg.add(dwg.rect(
        insert=(min_x, min_y),
        size=(width, height),
        fill='url(#grid)'
    ))
    
    # Add title
    dwg.add(dwg.text(
        'Split Column Staggered Keyboard Layout',
        insert=((min_x + max_x) / 2, min_y + 8),
        text_anchor='middle',
        font_family='Arial, sans-serif',
        font_size='4',
        fill='#212529',
        font_weight='bold'
    ))
    
    # Add half labels
    dwg.add(dwg.text(
        'Left Half',
        insert=(36, min_y + 18),
        text_anchor='middle',
        font_family='Arial, sans-serif',
        font_size='3',
        fill='#6c757d'
    ))
    
    dwg.add(dwg.text(
        'Right Half',
        insert=(155, min_y + 18),
        text_anchor='middle',
        font_family='Arial, sans-serif',
        font_size='3',
        fill='#6c757d'
    ))
    
    # Add key rectangles and labels for left half
    for key_name, x, y, rotation in positions['left']['switches']:
        # Use same color for all left switches
        fill_color = "#e3f2fd"
        stroke_color = "#1976d2"
        text_color = "#1976d2"
        
        if abs(rotation) < 0.1:  # No rotation for main keys
            # Add switch rectangle
            dwg.add(dwg.rect(
                insert=(x - config.footprint_width/2, y - config.footprint_height/2),
                size=(config.footprint_width, config.footprint_height),
                fill=fill_color,
                stroke=stroke_color,
                stroke_width=0.01
            ))
            # Add label
            dwg.add(dwg.text(
                key_name,
                insert=(x, y + 1),
                text_anchor='middle',
                font_family='Arial, sans-serif',
                font_size='2.5',
                fill=text_color,
                font_weight='bold'
            ))
        else:  # Rotated thumb keys
            group = dwg.g(transform=f'translate({x:.1f},{y:.1f}) rotate({rotation:.1f})')
            group.add(dwg.rect(
                insert=(-config.footprint_width/2, -config.footprint_height/2),
                size=(config.footprint_width, config.footprint_height),
                fill=fill_color,
                stroke=stroke_color,
                stroke_width=0.01
            ))
            group.add(dwg.text(
                key_name,
                insert=(0, 1),
                text_anchor='middle',
                font_family='Arial, sans-serif',
                font_size='2.5',
                fill=text_color,
                font_weight='bold'
            ))
            dwg.add(group)
    
    # Add diode rectangles and labels for left half
    for diode_name, x, y, rotation in positions['left']['diodes']:
        # Use same color for all left diodes
        fill_color = "#a8dadc"
        stroke_color = "#457b9d"
        text_color = "#1d3557"
        
        if abs(rotation) < 0.1:  # No rotation for main keys
            # Add diode rectangle
            dwg.add(dwg.rect(
                insert=(x - config.diode_width/2, y - config.diode_height/2),
                size=(config.diode_width, config.diode_height),
                fill=fill_color,
                stroke=stroke_color,
                stroke_width=0.1
            ))
            # Add label
            dwg.add(dwg.text(
                diode_name,
                insert=(x, y + 0.5),
                text_anchor='middle',
                font_family='Arial, sans-serif',
                font_size='1.5',
                fill=text_color,
                font_weight='bold'
            ))
        else:  # Rotated thumb diodes
            group = dwg.g(transform=f'translate({x:.1f},{y:.1f}) rotate({rotation:.1f})')
            group.add(dwg.rect(
                insert=(-config.diode_width/2, -config.diode_height/2),
                size=(config.diode_width, config.diode_height),
                fill=fill_color,
                stroke=stroke_color,
                stroke_width=0.1
            ))
            group.add(dwg.text(
                diode_name,
                insert=(0, 0.5),
                text_anchor='middle',
                font_family='Arial, sans-serif',
                font_size='1.5',
                fill=text_color,
                font_weight='bold'
            ))
            dwg.add(group)
    
    # Add key rectangles and labels for right half
    for key_name, x, y, rotation in positions['right']['switches']:
        # Use same color for all right switches
        fill_color = "#f3e5f5"
        stroke_color = "#7b1fa2"
        text_color = "#7b1fa2"
        
        if abs(rotation) < 0.1:  # No rotation for main keys
            # Add switch rectangle
            dwg.add(dwg.rect(
                insert=(x - config.footprint_width/2, y - config.footprint_height/2),
                size=(config.footprint_width, config.footprint_height),
                fill=fill_color,
                stroke=stroke_color,
                stroke_width=0.01
            ))
            # Add label
            dwg.add(dwg.text(
                key_name,
                insert=(x, y + 1),
                text_anchor='middle',
                font_family='Arial, sans-serif',
                font_size='2.5',
                fill=text_color,
                font_weight='bold'
            ))
        else:  # Rotated thumb keys
            group = dwg.g(transform=f'translate({x:.1f},{y:.1f}) rotate({rotation:.1f})')
            group.add(dwg.rect(
                insert=(-config.footprint_width/2, -config.footprint_height/2),
                size=(config.footprint_width, config.footprint_height),
                fill=fill_color,
                stroke=stroke_color,
                stroke_width=0.01
            ))
            group.add(dwg.text(
                key_name,
                insert=(0, 1),
                text_anchor='middle',
                font_family='Arial, sans-serif',
                font_size='2.5',
                fill=text_color,
                font_weight='bold'
            ))
            dwg.add(group)
    
    # Add diode rectangles and labels for right half
    for diode_name, x, y, rotation in positions['right']['diodes']:
        # Use same color for all right diodes
        fill_color = "#dda0dd"
        stroke_color = "#9a031e"
        text_color = "#5f0a87"
        
        if abs(rotation) < 0.1:  # No rotation for main keys
            # Add diode rectangle
            dwg.add(dwg.rect(
                insert=(x - config.diode_width/2, y - config.diode_height/2),
                size=(config.diode_width, config.diode_height),
                fill=fill_color,
                stroke=stroke_color,
                stroke_width=0.1
            ))
            # Add label
            dwg.add(dwg.text(
                diode_name,
                insert=(x, y + 0.5),
                text_anchor='middle',
                font_family='Arial, sans-serif',
                font_size='1.5',
                fill=text_color,
                font_weight='bold'
            ))
        else:  # Rotated thumb diodes
            group = dwg.g(transform=f'translate({x:.1f},{y:.1f}) rotate({rotation:.1f})')
            group.add(dwg.rect(
                insert=(-config.diode_width/2, -config.diode_height/2),
                size=(config.diode_width, config.diode_height),
                fill=fill_color,
                stroke=stroke_color,
                stroke_width=0.1
            ))
            group.add(dwg.text(
                diode_name,
                insert=(0, 0.5),
                text_anchor='middle',
                font_family='Arial, sans-serif',
                font_size='1.5',
                fill=text_color,
                font_weight='bold'
            ))
            dwg.add(group)
    
    # Add specific components for both halves
    for half in ['left', 'right']:
        for component_type, components in positions[half].items():
            if component_type not in ['switches', 'diodes']:
                # Choose color based on component type
                if component_type == 'MCU':
                    fill_color = "#ff6b35"
                    stroke_color = "#d63031"
                    text_color = "#2d3436"
                elif component_type == 'HOLE':
                    fill_color = "#636e72"
                    stroke_color = "#2d3436"
                    text_color = "#2d3436"
                elif component_type == 'BAT':
                    fill_color = "#00b894"
                    stroke_color = "#00a085"
                    text_color = "#2d3436"
                elif component_type == 'RSW':
                    fill_color = "#e17055"
                    stroke_color = "#d63031"
                    text_color = "#2d3436"
                else:
                    fill_color = "#74b9ff"
                    stroke_color = "#0984e3"
                    text_color = "#2d3436"
                
                for component_name, x, y, rotation in components:
                    if component_type == 'HOLE':
                        # Make holes 3mm circles (radius = 1.5mm)
                        dwg.add(dwg.circle(
                            center=(x, y),
                            r=1.5,
                            fill=fill_color,
                            stroke=stroke_color,
                            stroke_width=0.1
                        ))
                        dwg.add(dwg.text(
                            component_name,
                            insert=(x, y - 3),
                            text_anchor='middle',
                            font_family='Arial, sans-serif',
                            font_size='2',
                            fill=text_color,
                            font_weight='bold'
                        ))
                    else:
                        # Make all other components small dots (radius = 0.5mm)
                        dwg.add(dwg.circle(
                            center=(x, y),
                            r=0.5,
                            fill=fill_color,
                            stroke=stroke_color,
                            stroke_width=0.1
                        ))
                        dwg.add(dwg.text(
                            component_name,
                            insert=(x, y - 2),
                            text_anchor='middle',
                            font_family='Arial, sans-serif',
                            font_size='1.5',
                            fill=text_color,
                            font_weight='bold'
                        ))
    
    # Add thumb arc origins
    # Calculate left thumb arc origin
    ref_x, ref_y = KeyboardLayoutCalculator.calculate_left_position(config, config.num_rows - 1, config.thumb_arc_col_start)
    left_origin_x = ref_x + config.thumb_arc_config.offset_x
    left_origin_y = ref_y + config.thumb_arc_config.offset_y + config.thumb_arc_config.radius
    
    # Calculate right thumb arc origin by mirroring the left origin
    right_origin_x, right_origin_y = KeyboardLayoutCalculator.mirror_position(config, left_origin_x, left_origin_y)
    
    # Add left thumb arc origin marker
    dwg.add(dwg.circle(
        center=(left_origin_x, left_origin_y),
        r=0.5,
        fill='#d32f2f',
        stroke='#b71c1c',
        stroke_width=0.1
    ))
    dwg.add(dwg.circle(
        center=(left_origin_x, left_origin_y),
        r=3,
        fill='none',
        stroke='#d32f2f',
        stroke_width=0.05,
        stroke_dasharray='0.5,0.5'
    ))
    dwg.add(dwg.text(
        'L-ARC',
        insert=(left_origin_x, left_origin_y - 4),
        text_anchor='middle',
        font_family='Arial, sans-serif',
        font_size='1.5',
        fill='#d32f2f',
        font_weight='bold'
    ))
    
    # Add right thumb arc origin marker
    dwg.add(dwg.circle(
        center=(right_origin_x, right_origin_y),
        r=0.5,
        fill='#d32f2f',
        stroke='#b71c1c',
        stroke_width=0.1
    ))
    dwg.add(dwg.circle(
        center=(right_origin_x, right_origin_y),
        r=3,
        fill='none',
        stroke='#d32f2f',
        stroke_width=0.05,
        stroke_dasharray='0.5,0.5'
    ))
    dwg.add(dwg.text(
        'R-ARC',
        insert=(right_origin_x, right_origin_y - 4),
        text_anchor='middle',
        font_family='Arial, sans-serif',
        font_size='1.5',
        fill='#d32f2f',
        font_weight='bold'
    ))
    
    # Add coordinate origin (0,0)
    origin_group = dwg.g()
    origin_group.add(dwg.circle(
        center=(0, 0),
        r=0.5,
        fill='#ff4444',
        stroke='#cc0000',
        stroke_width=0.1
    ))
    origin_group.add(dwg.circle(
        center=(0, 0),
        r=5,
        fill='none',
        stroke='#ff4444',
        stroke_width=0.05,
        stroke_dasharray='1,1'
    ))
    origin_group.add(dwg.line(
        start=(-10, 0),
        end=(10, 0),
        stroke='#ff4444',
        stroke_width=0.1
    ))
    origin_group.add(dwg.line(
        start=(0, -10),
        end=(0, 10),
        stroke='#ff4444',
        stroke_width=0.1
    ))
    origin_group.add(dwg.text(
        'ORIGIN',
        insert=(0, -7),
        text_anchor='middle',
        font_family='Arial, sans-serif',
        font_size='2',
        fill='#ff4444',
        font_weight='bold'
    ))
    origin_group.add(dwg.text(
        '(0.0, 0.0)',
        insert=(0, 10),
        text_anchor='middle',
        font_family='Arial, sans-serif',
        font_size='1.5',
        fill='#666666'
    ))
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
    # Conversion factor for Fusion 360: 1mm = 96/25.4 pixels (96 DPI)
    mm_to_px = 96.0 / 25.4
    
    # Calculate SVG dimensions based on switch positions only
    all_switch_positions = positions['left']['switches'] + positions['right']['switches']
    
    # Calculate bounds considering only switches (in mm)
    switch_min_x = min(x - config.footprint_width/2 for _, x, y, r in all_switch_positions)
    switch_max_x = max(x + config.footprint_width/2 for _, x, y, r in all_switch_positions)
    switch_min_y = min(y - config.footprint_height/2 for _, x, y, r in all_switch_positions)
    switch_max_y = max(y + config.footprint_height/2 for _, x, y, r in all_switch_positions)
    
    # Add margin for clean viewing (in mm)
    margin = 20
    min_x_mm = switch_min_x - margin
    max_x_mm = switch_max_x + margin
    min_y_mm = switch_min_y - margin
    max_y_mm = switch_max_y + margin
    
    width_mm = max_x_mm - min_x_mm
    height_mm = max_y_mm - min_y_mm
    
    # Convert to pixels for Fusion 360 compatibility
    min_x_px = min_x_mm * mm_to_px
    min_y_px = min_y_mm * mm_to_px
    width_px = width_mm * mm_to_px
    height_px = height_mm * mm_to_px
    
    # Create SVG drawing with pixel units for Fusion 360 compatibility
    dwg = svgwrite.Drawing(
        filename,
        size=(f'{width_px:.3f}px', f'{height_px:.3f}px'),
        viewBox=f'{min_x_px:.3f} {min_y_px:.3f} {width_px:.3f} {height_px:.3f}'
    )

    # Add switch rectangles for both halves
    for half in ['left', 'right']:
        for key_name, x, y, rotation in positions[half]['switches']:
            # Convert mm coordinates to pixels
            x_px = x * mm_to_px
            y_px = y * mm_to_px
            width_px_rect = config.footprint_width * mm_to_px
            height_px_rect = config.footprint_height * mm_to_px
            
            if abs(rotation) < 0.1:  # No rotation for main keys
                # Add switch outline rectangle
                dwg.add(dwg.rect(
                    insert=(x_px - width_px_rect/2, y_px - height_px_rect/2),
                    size=(width_px_rect, height_px_rect),
                    fill='none',
                    stroke='#000000',
                    stroke_width='0.38'
                ))
            else:  # Rotated thumb keys
                # Create group for rotation
                group = dwg.g(transform=f'translate({x_px:.3f},{y_px:.3f}) rotate({rotation:.3f})')
                group.add(dwg.rect(
                    insert=(-width_px_rect/2, -height_px_rect/2),
                    size=(width_px_rect, height_px_rect),
                    fill='none',
                    stroke='#000000',
                    stroke_width='0.38'
                ))
                dwg.add(group)
    
    # Calculate the midpoint between the two halves
    left_switches = positions['left']['switches']
    right_switches = positions['right']['switches']
    
    # Find the rightmost x coordinate of left switches (in mm)
    left_max_x_mm = max(x + config.footprint_width/2 for _, x, y, r in left_switches)
    
    # Find the leftmost x coordinate of right switches (in mm)
    right_min_x_mm = min(x - config.footprint_width/2 for _, x, y, r in right_switches)
    
    # Calculate the midpoint (in mm, then convert to pixels)
    midpoint_x_mm = (left_max_x_mm + right_min_x_mm) / 2
    midpoint_x_px = midpoint_x_mm * mm_to_px
    
    # Add midpoint separation line
    dwg.add(dwg.line(
        start=(midpoint_x_px, min_y_px),
        end=(midpoint_x_px, min_y_px + height_px),
        stroke='#0066cc',
        stroke_width='0.57',
        stroke_dasharray='7.56,3.78'
    ))
    
    # Add coordinate origin marker
    origin_group = dwg.g()
    origin_group.add(dwg.circle(
        center=(0, 0),
        r=3.78,
        fill='none',
        stroke='#ff0000',
        stroke_width='0.76'
    ))
    origin_group.add(dwg.line(
        start=(-18.9, 0),
        end=(18.9, 0),
        stroke='#ff0000',
        stroke_width='0.76'
    ))
    origin_group.add(dwg.line(
        start=(0, -18.9),
        end=(0, 18.9),
        stroke='#ff0000',
        stroke_width='0.76'
    ))
    dwg.add(origin_group)
    
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
    # Conversion factor for Fusion 360: 1mm = 96/25.4 pixels (96 DPI)
    mm_to_px = 96.0 / 25.4
    
    # Calculate SVG dimensions based on switch positions with keepout zones
    all_switch_positions = positions['left']['switches'] + positions['right']['switches']
    
    # Calculate bounds considering switches and keepout zones (16mm is the largest)
    keepout_size = 16.0  # mm
    switch_min_x = min(x - keepout_size/2 for _, x, y, r in all_switch_positions)
    switch_max_x = max(x + keepout_size/2 for _, x, y, r in all_switch_positions)
    switch_min_y = min(y - keepout_size/2 for _, x, y, r in all_switch_positions)
    switch_max_y = max(y + keepout_size/2 for _, x, y, r in all_switch_positions)
    
    # Add margin for clean viewing (in mm)
    margin = 20
    min_x_mm = switch_min_x - margin
    max_x_mm = switch_max_x + margin
    min_y_mm = switch_min_y - margin
    max_y_mm = switch_max_y + margin
    
    width_mm = max_x_mm - min_x_mm
    height_mm = max_y_mm - min_y_mm
    
    # Convert to pixels for Fusion 360 compatibility
    min_x_px = min_x_mm * mm_to_px
    min_y_px = min_y_mm * mm_to_px
    width_px = width_mm * mm_to_px
    height_px = height_mm * mm_to_px
    
    # Create SVG drawing with pixel units for Fusion 360 compatibility
    dwg = svgwrite.Drawing(
        filename,
        size=(f'{width_px:.3f}px', f'{height_px:.3f}px'),
        viewBox=f'{min_x_px:.3f} {min_y_px:.3f} {width_px:.3f} {height_px:.3f}'
    )

    # Add switch plate holes and recesses for both halves
    for half in ['left', 'right']:
        for key_name, x, y, rotation in positions[half]['switches']:
            # Convert mm coordinates to pixels
            x_px = x * mm_to_px
            y_px = y * mm_to_px
            
            # Hole and recess dimensions in pixels
            hole_14_px = 14.0 * mm_to_px
            recess_16_px = 16.0 * mm_to_px
            
            if abs(rotation) < 0.1:  # No rotation for main keys
                # 16mm recess (outer rectangle)
                dwg.add(dwg.rect(
                    insert=(x_px - recess_16_px/2, y_px - recess_16_px/2),
                    size=(recess_16_px, recess_16_px),
                    fill='none',
                    stroke='#000000',
                    stroke_width='0.1'
                ))
                
                # 14mm hole (inner rectangle)
                dwg.add(dwg.rect(
                    insert=(x_px - hole_14_px/2, y_px - hole_14_px/2),
                    size=(hole_14_px, hole_14_px),
                    fill='none',
                    stroke='#000000',
                    stroke_width='0.1'
                ))
            else:  # Rotated thumb keys
                # Create group for rotation
                group = dwg.g(transform=f'translate({x_px:.3f},{y_px:.3f}) rotate({rotation:.3f})')
                
                # 16mm recess (outer rectangle)
                group.add(dwg.rect(
                    insert=(-recess_16_px/2, -recess_16_px/2),
                    size=(recess_16_px, recess_16_px),
                    fill='none',
                    stroke='#000000',
                    stroke_width='0.1'
                ))
                
                # 14mm hole (inner rectangle)
                group.add(dwg.rect(
                    insert=(-hole_14_px/2, -hole_14_px/2),
                    size=(hole_14_px, hole_14_px),
                    fill='none',
                    stroke='#000000',
                    stroke_width='0.1'
                ))
                
                dwg.add(group)
    
    # Add coordinate origin marker
    origin_group = dwg.g()
    origin_group.add(dwg.circle(
        center=(0, 0),
        r=3.78,
        fill='none',
        stroke='#000000',
        stroke_width='0.1'
    ))
    origin_group.add(dwg.line(
        start=(-18.9, 0),
        end=(18.9, 0),
        stroke='#000000',
        stroke_width='0.1'
    ))
    origin_group.add(dwg.line(
        start=(0, -18.9),
        end=(0, 18.9),
        stroke='#000000',
        stroke_width='0.1'
    ))
    dwg.add(origin_group)
    
    # Save the SVG
    dwg.save()
    print(f"Switch plate SVG exported to {filename}")
