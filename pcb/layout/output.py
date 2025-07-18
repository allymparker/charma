#!/usr/bin/env python3
"""
Output utilities for keyboard layout calculator.

Contains functions for displaying and exporting keyboard layout positions.
"""

from typing import Dict, List, Tuple
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
    for key_name, x, y, rotation in positions['left']['switches']:
        # Use same color for all left switches
        fill_color = "#e3f2fd"
        stroke_color = "#1976d2"
        text_color = "#1976d2"
        
        if abs(rotation) < 0.1:  # No rotation for main keys
            # Convert center coordinates to top-left for rectangle drawing
            rect_x = x - config.footprint_width/2
            rect_y = y - config.footprint_height/2
            svg_content += f'''  <!-- {key_name} -->
  <rect x="{rect_x:.1f}" y="{rect_y:.1f}" 
        width="{config.footprint_width:.1f}" height="{config.footprint_height:.1f}"
        fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.1"/>
  <text x="{x:.1f}" y="{y + 1:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
        fill="{text_color}" font-weight="bold">{key_name}</text>
'''
        else:  # Rotated thumb keys
            # Convert center coordinates to top-left for rectangle drawing
            rect_x = -config.footprint_width/2
            rect_y = -config.footprint_height/2
            svg_content += f'''  <!-- {key_name} -->
  <g transform="translate({x:.1f},{y:.1f}) rotate({rotation:.1f})">
    <rect x="{rect_x:.1f}" y="{rect_y:.1f}" 
          width="{config.footprint_width:.1f}" height="{config.footprint_height:.1f}"
          fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.1"/>
    <text x="0" y="1" 
          text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
          fill="{text_color}" font-weight="bold">{key_name}</text>
  </g>
'''
    
    # Add diode rectangles and labels for left half
    for diode_name, x, y, rotation in positions['left']['diodes']:
        # Use same color for all left diodes
        fill_color = "#a8dadc"
        stroke_color = "#457b9d"
        text_color = "#1d3557"
        
        if abs(rotation) < 0.1:  # No rotation for main keys
            # Convert center coordinates to top-left for rectangle drawing
            rect_x = x - config.diode_width/2
            rect_y = y - config.diode_height/2
            svg_content += f'''  <!-- {diode_name} -->
  <rect x="{rect_x:.1f}" y="{rect_y:.1f}" 
        width="{config.diode_width:.1f}" height="{config.diode_height:.1f}"
        fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.1"/>
  <text x="{x:.1f}" y="{y + 0.5:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="1.5" 
        fill="{text_color}" font-weight="bold">{diode_name}</text>
'''
        else:  # Rotated thumb diodes
            # Convert center coordinates to top-left for rectangle drawing
            rect_x = -config.diode_width/2
            rect_y = -config.diode_height/2
            svg_content += f'''  <!-- {diode_name} -->
  <g transform="translate({x:.1f},{y:.1f}) rotate({rotation:.1f})">
    <rect x="{rect_x:.1f}" y="{rect_y:.1f}" 
          width="{config.diode_width:.1f}" height="{config.diode_height:.1f}"
          fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.1"/>
    <text x="0" y="0.5" 
          text-anchor="middle" font-family="Arial, sans-serif" font-size="1.5" 
          fill="{text_color}" font-weight="bold">{diode_name}</text>
  </g>
'''
    
    # Add key rectangles and labels for right half
    for key_name, x, y, rotation in positions['right']['switches']:
        # Use same color for all right switches
        fill_color = "#f3e5f5"
        stroke_color = "#7b1fa2"
        text_color = "#7b1fa2"
        
        if abs(rotation) < 0.1:  # No rotation for main keys
            # Convert center coordinates to top-left for rectangle drawing
            rect_x = x - config.footprint_width/2
            rect_y = y - config.footprint_height/2
            svg_content += f'''  <!-- {key_name} -->
  <rect x="{rect_x:.1f}" y="{rect_y:.1f}" 
        width="{config.footprint_width:.1f}" height="{config.footprint_height:.1f}"
        fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.1"/>
  <text x="{x:.1f}" y="{y + 1:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
        fill="{text_color}" font-weight="bold">{key_name}</text>
'''
        else:  # Rotated thumb keys
            # Convert center coordinates to top-left for rectangle drawing
            rect_x = -config.footprint_width/2
            rect_y = -config.footprint_height/2
            svg_content += f'''  <!-- {key_name} -->
  <g transform="translate({x:.1f},{y:.1f}) rotate({rotation:.1f})">
    <rect x="{rect_x:.1f}" y="{rect_y:.1f}" 
          width="{config.footprint_width:.1f}" height="{config.footprint_height:.1f}"
          fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.1"/>
    <text x="0" y="1" 
          text-anchor="middle" font-family="Arial, sans-serif" font-size="2.5" 
          fill="{text_color}" font-weight="bold">{key_name}</text>
  </g>
'''
    
    # Add diode rectangles and labels for right half
    for diode_name, x, y, rotation in positions['right']['diodes']:
        # Use same color for all right diodes
        fill_color = "#dda0dd"
        stroke_color = "#9a031e"
        text_color = "#5f0a87"
        
        if abs(rotation) < 0.1:  # No rotation for main keys
            # Convert center coordinates to top-left for rectangle drawing
            rect_x = x - config.diode_width/2
            rect_y = y - config.diode_height/2
            svg_content += f'''  <!-- {diode_name} -->
  <rect x="{rect_x:.1f}" y="{rect_y:.1f}" 
        width="{config.diode_width:.1f}" height="{config.diode_height:.1f}"
        fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.1"/>
  <text x="{x:.1f}" y="{y + 0.5:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="1.5" 
        fill="{text_color}" font-weight="bold">{diode_name}</text>
'''
        else:  # Rotated thumb diodes
            # Convert center coordinates to top-left for rectangle drawing
            rect_x = -config.diode_width/2
            rect_y = -config.diode_height/2
            svg_content += f'''  <!-- {diode_name} -->
  <g transform="translate({x:.1f},{y:.1f}) rotate({rotation:.1f})">
    <rect x="{rect_x:.1f}" y="{rect_y:.1f}" 
          width="{config.diode_width:.1f}" height="{config.diode_height:.1f}"
          fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.1"/>
    <text x="0" y="0.5" 
          text-anchor="middle" font-family="Arial, sans-serif" font-size="1.5" 
          fill="{text_color}" font-weight="bold">{diode_name}</text>
  </g>
'''
    
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
                    svg_content += f'''  <!-- {component_name} -->
  <circle cx="{x:.1f}" cy="{y:.1f}" r="1.5" 
          fill="{fill_color}" stroke="{stroke_color}" stroke-width="0.2"/>
  <text x="{x:.1f}" y="{y - 3:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="2" 
        fill="{text_color}" font-weight="bold">{component_name}</text>
'''
    
    # Add thumb arc origins
    # Calculate left thumb arc origin
    ref_x, ref_y = KeyboardLayoutCalculator.calculate_left_position(config, config.num_rows - 1, config.thumb_arc_col_start)
    left_origin_x = ref_x + config.thumb_offset_x
    left_origin_y = ref_y + config.thumb_offset_y + config.thumb_arc_radius
    
    # Calculate right thumb arc origin by mirroring the left origin
    right_origin_x, right_origin_y = KeyboardLayoutCalculator.mirror_position(config, left_origin_x, left_origin_y)
    
    # Add left thumb arc origin marker
    svg_content += f'''  <!-- Left Thumb Arc Origin -->
  <circle cx="{left_origin_x:.1f}" cy="{left_origin_y:.1f}" r="1" 
          fill="#d32f2f" stroke="#b71c1c" stroke-width="0.2"/>
  <circle cx="{left_origin_x:.1f}" cy="{left_origin_y:.1f}" r="3" 
          fill="none" stroke="#d32f2f" stroke-width="0.1" stroke-dasharray="0.5,0.5"/>
  <text x="{left_origin_x:.1f}" y="{left_origin_y - 4:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="1.5" 
        fill="#d32f2f" font-weight="bold">L-ARC</text>
'''
    
    # Add right thumb arc origin marker
    svg_content += f'''  <!-- Right Thumb Arc Origin -->
  <circle cx="{right_origin_x:.1f}" cy="{right_origin_y:.1f}" r="1" 
          fill="#d32f2f" stroke="#b71c1c" stroke-width="0.2"/>
  <circle cx="{right_origin_x:.1f}" cy="{right_origin_y:.1f}" r="3" 
          fill="none" stroke="#d32f2f" stroke-width="0.1" stroke-dasharray="0.5,0.5"/>
  <text x="{right_origin_x:.1f}" y="{right_origin_y - 4:.1f}" 
        text-anchor="middle" font-family="Arial, sans-serif" font-size="1.5" 
        fill="#d32f2f" font-weight="bold">R-ARC</text>
  
  <!-- Origin Point -->
  <g>
    <circle cx="{config.origin_x:.1f}" cy="{config.origin_y:.1f}" r="2" 
            fill="#ff4444" stroke="#cc0000" stroke-width="0.3"/>
    <circle cx="{config.origin_x:.1f}" cy="{config.origin_y:.1f}" r="5" 
            fill="none" stroke="#ff4444" stroke-width="0.2" stroke-dasharray="1,1"/>
    <line x1="{config.origin_x - 10:.1f}" y1="{config.origin_y:.1f}" 
          x2="{config.origin_x + 10:.1f}" y2="{config.origin_y:.1f}" 
          stroke="#ff4444" stroke-width="0.3"/>
    <line x1="{config.origin_x:.1f}" y1="{config.origin_y - 10:.1f}" 
          x2="{config.origin_x:.1f}" y2="{config.origin_y + 10:.1f}" 
          stroke="#ff4444" stroke-width="0.3"/>
    <text x="{config.origin_x:.1f}" y="{config.origin_y - 7:.1f}" 
          text-anchor="middle" font-family="Arial, sans-serif" font-size="2" 
          fill="#ff4444" font-weight="bold">ORIGIN</text>
    <text x="{config.origin_x:.1f}" y="{config.origin_y + 10:.1f}" 
          text-anchor="middle" font-family="Arial, sans-serif" font-size="1.5" 
          fill="#666666">({config.origin_x:.1f}, {config.origin_y:.1f})</text>
  </g>
</svg>'''
    
    with open(filename, 'w') as f:
        f.write(svg_content)
    
    print(f"SVG visualization exported to {filename}")
