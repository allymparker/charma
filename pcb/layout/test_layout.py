#!/usr/bin/env python3
"""
Unit tests for the KeyboardLayoutCalculator position calculation methods.

These tests cover:
- calculate_left_position: Basic position calculation for left half keys
- calculate_thumb_position: Thumb key position calculation with arc layout
- mirror_position: Position mirroring for creating right half from left half
- mirror_thumb_position: Thumb position mirroring with rotation handling
- calculate_diode_position: Diode placement relative to switches (rotated and non-rotated)
- generate_all_positions: Complete layout generation and validation

Test coverage includes:
- Basic functionality and edge cases
- Column stagger handling
- Thumb arc geometry
- Mirror symmetry validation
- Component naming conventions
- Coordinate precision and finite number validation
"""

import unittest
import math
from layout import (
    KeyboardLayoutCalculator,
    KeyboardLayoutConfig,
    ThumbArcConfig,
    SpecificPosition
)


class TestKeyboardLayoutCalculator(unittest.TestCase):
    """Test cases for KeyboardLayoutCalculator methods."""
    
    def setUp(self):
        """Set up test configuration."""
        # Simple test configuration
        self.column_stagger = {
            0: 0.0,
            1: -5.0,
            2: -2.0,
            3: 2.0,
            4: 1.0,
        }
        
        self.thumb_arc_config = ThumbArcConfig(
            radius=50.0,
            start_angle=-90,
            end_angle=-45,
            offset_x=0,
            offset_y=5.0
        )
        
        self.specific_positions = [
            SpecificPosition("MCU", 1, 10.0, 10.0, -90.0),
        ]
        
        self.config = KeyboardLayoutConfig(
            origin_x=10.0,
            origin_y=20.0,
            num_rows=3,
            column_stagger=self.column_stagger,
            num_thumb_keys=2,
            thumb_arc_col_start=2,
            thumb_arc_config=self.thumb_arc_config,
            specific_positions=self.specific_positions
        )

    def test_calculate_left_position_basic(self):
        """Test basic left position calculation."""
        # Test origin position (row 0, col 0)
        x, y = KeyboardLayoutCalculator.calculate_left_position(self.config, 0, 0)
        
        # Expected: origin + adjustments + center offset
        expected_x = self.config.origin_x + (-0.5 * self.config.x_pitch) + 0.25 + (self.config.footprint_width / 2)
        expected_y = self.config.origin_y + (-0.5 * self.config.y_pitch) + 0.25 + (self.config.footprint_height / 2) + self.column_stagger[0]
        
        self.assertAlmostEqual(x, expected_x, places=2)
        self.assertAlmostEqual(y, expected_y, places=2)

    def test_calculate_left_position_with_stagger(self):
        """Test left position calculation with column stagger."""
        # Test column 1 which has stagger
        x, y = KeyboardLayoutCalculator.calculate_left_position(self.config, 0, 1)
        
        # Expected: includes stagger for columns 0 and 1
        expected_stagger = self.column_stagger[0] + self.column_stagger[1]
        expected_x = self.config.origin_x + (0.5 * self.config.x_pitch) + 0.25 + (self.config.footprint_width / 2)
        expected_y = self.config.origin_y + (-0.5 * self.config.y_pitch) + 0.25 + (self.config.footprint_height / 2) + expected_stagger
        
        self.assertAlmostEqual(x, expected_x, places=2)
        self.assertAlmostEqual(y, expected_y, places=2)

    def test_calculate_left_position_different_rows(self):
        """Test left position calculation for different rows."""
        x1, y1 = KeyboardLayoutCalculator.calculate_left_position(self.config, 0, 0)
        x2, y2 = KeyboardLayoutCalculator.calculate_left_position(self.config, 1, 0)
        
        # X should be the same for same column
        self.assertAlmostEqual(x1, x2, places=2)
        
        # Y should differ by y_pitch
        self.assertAlmostEqual(y2 - y1, self.config.y_pitch, places=2)

    def test_calculate_thumb_position_single_key(self):
        """Test thumb position calculation with single thumb key."""
        # Create config with single thumb key
        single_thumb_config = KeyboardLayoutConfig(
            origin_x=10.0,
            origin_y=20.0,
            num_rows=3,
            column_stagger=self.column_stagger,
            num_thumb_keys=1,
            thumb_arc_col_start=2,
            thumb_arc_config=self.thumb_arc_config,
            specific_positions=self.specific_positions
        )
        
        x, y, rotation = KeyboardLayoutCalculator.calculate_thumb_position(single_thumb_config, 0, is_left=True)
        
        # Single key should have 0 angle, so rotation should be 90
        self.assertAlmostEqual(rotation, 90.0, places=1)
        
        # Position should be at arc center (angle = 0)
        ref_x, ref_y = KeyboardLayoutCalculator.calculate_left_position(single_thumb_config, single_thumb_config.num_rows - 1, single_thumb_config.thumb_arc_col_start)
        arc_origin_x = ref_x + single_thumb_config.thumb_arc_config.offset_x
        arc_origin_y = ref_y + single_thumb_config.thumb_arc_config.offset_y + single_thumb_config.thumb_arc_config.radius
        
        expected_x = arc_origin_x + single_thumb_config.thumb_arc_config.radius  # cos(0) = 1
        expected_y = arc_origin_y  # sin(0) = 0
        
        self.assertAlmostEqual(x, expected_x, places=2)
        self.assertAlmostEqual(y, expected_y, places=2)

    def test_calculate_thumb_position_multiple_keys(self):
        """Test thumb position calculation with multiple thumb keys."""
        # Test first thumb key (index 0)
        x1, y1, rotation1 = KeyboardLayoutCalculator.calculate_thumb_position(self.config, 0, is_left=True)
        
        # Test second thumb key (index 1)
        x2, y2, rotation2 = KeyboardLayoutCalculator.calculate_thumb_position(self.config, 1, is_left=True)
        
        # Rotations should be different
        self.assertNotAlmostEqual(rotation1, rotation2, places=1)
        
        # First key should be at start angle + 90
        expected_rotation1 = self.thumb_arc_config.start_angle + 90.0
        self.assertAlmostEqual(rotation1, expected_rotation1, places=1)
        
        # Second key should be at end angle + 90
        expected_rotation2 = self.thumb_arc_config.end_angle + 90.0
        self.assertAlmostEqual(rotation2, expected_rotation2, places=1)

    def test_mirror_position(self):
        """Test position mirroring for right half."""
        left_x, left_y = KeyboardLayoutCalculator.calculate_left_position(self.config, 0, 0)
        right_x, right_y = KeyboardLayoutCalculator.mirror_position(self.config, left_x, left_y)
        
        # Y should be the same
        self.assertAlmostEqual(left_y, right_y, places=2)
        
        # X should be mirrored
        left_half_width = (self.config.num_cols - 1) * self.config.x_pitch + self.config.footprint_width
        expected_right_x = left_half_width + self.config.split_separation + (left_half_width - left_x)
        self.assertAlmostEqual(right_x, expected_right_x, places=2)

    def test_mirror_thumb_position(self):
        """Test thumb position mirroring for right half."""
        left_x, left_y, left_rotation = KeyboardLayoutCalculator.calculate_thumb_position(self.config, 0, is_left=True)
        right_x, right_y, right_rotation = KeyboardLayoutCalculator.mirror_thumb_position(self.config, left_x, left_y, left_rotation)
        
        # Y should be the same
        self.assertAlmostEqual(left_y, right_y, places=2)
        
        # Rotation should be negated
        self.assertAlmostEqual(right_rotation, -left_rotation, places=2)
        
        # X should be mirrored using same logic as regular mirror
        left_half_width = (self.config.num_cols - 1) * self.config.x_pitch + self.config.footprint_width
        expected_right_x = left_half_width + self.config.split_separation + (left_half_width - left_x)
        self.assertAlmostEqual(right_x, expected_right_x, places=2)

    def test_calculate_diode_position_no_rotation(self):
        """Test diode position calculation for non-rotated switches."""
        switch_x, switch_y = 50.0, 60.0
        switch_rotation = 0.0
        
        diode_x, diode_y, diode_rotation = KeyboardLayoutCalculator.calculate_diode_position(
            self.config, switch_x, switch_y, switch_rotation
        )
        
        # For non-rotated switches, offset is applied directly
        expected_x = switch_x + self.config.diode_offset_x
        expected_y = switch_y + self.config.diode_offset_y
        expected_rotation = self.config.diode_orientation
        
        self.assertAlmostEqual(diode_x, expected_x, places=2)
        self.assertAlmostEqual(diode_y, expected_y, places=2)
        self.assertAlmostEqual(diode_rotation, expected_rotation, places=2)

    def test_calculate_diode_position_with_rotation(self):
        """Test diode position calculation for rotated switches."""
        switch_x, switch_y = 50.0, 60.0
        switch_rotation = 45.0  # 45 degrees
        
        diode_x, diode_y, diode_rotation = KeyboardLayoutCalculator.calculate_diode_position(
            self.config, switch_x, switch_y, switch_rotation
        )
        
        # For rotated switches, offset vector is rotated
        rot_rad = math.radians(switch_rotation)
        expected_offset_x = (self.config.diode_offset_x * math.cos(rot_rad) - 
                           self.config.diode_offset_y * math.sin(rot_rad))
        expected_offset_y = (self.config.diode_offset_x * math.sin(rot_rad) + 
                           self.config.diode_offset_y * math.cos(rot_rad))
        
        expected_x = switch_x + expected_offset_x
        expected_y = switch_y + expected_offset_y
        expected_rotation = switch_rotation + self.config.diode_orientation
        
        self.assertAlmostEqual(diode_x, expected_x, places=2)
        self.assertAlmostEqual(diode_y, expected_y, places=2)
        self.assertAlmostEqual(diode_rotation, expected_rotation, places=2)

    def test_generate_all_positions_structure(self):
        """Test the structure of generated positions."""
        positions = KeyboardLayoutCalculator.generate_all_positions(self.config)
        
        # Check top-level structure
        self.assertIn('left', positions)
        self.assertIn('right', positions)
        
        # Check second-level structure
        for half in ['left', 'right']:
            self.assertIn('switches', positions[half])
            self.assertIn('diodes', positions[half])
            self.assertIn('MCU', positions[half])  # From specific_positions
        
        # Check counts
        expected_main_keys = self.config.num_rows * self.config.num_cols
        expected_total_keys = expected_main_keys + self.config.num_thumb_keys
        
        for half in ['left', 'right']:
            self.assertEqual(len(positions[half]['switches']), expected_total_keys)
            self.assertEqual(len(positions[half]['diodes']), expected_total_keys)

    def test_generate_all_positions_naming(self):
        """Test the naming convention of generated positions."""
        positions = KeyboardLayoutCalculator.generate_all_positions(self.config)
        
        # Check left switches naming
        left_switches = positions['left']['switches']
        self.assertEqual(left_switches[0][0], 'SWL1')  # First switch
        self.assertEqual(left_switches[-1][0], f'SWL{len(left_switches)}')  # Last switch
        
        # Check right switches naming
        right_switches = positions['right']['switches']
        self.assertEqual(right_switches[0][0], 'SWR1')  # First switch
        self.assertEqual(right_switches[-1][0], f'SWR{len(right_switches)}')  # Last switch
        
        # Check diode naming matches switches
        left_diodes = positions['left']['diodes']
        right_diodes = positions['right']['diodes']
        
        for i, (switch_name, _, _, _) in enumerate(left_switches):
            diode_name = left_diodes[i][0]
            expected_diode = switch_name.replace('SW', 'D')
            self.assertEqual(diode_name, expected_diode)
        
        for i, (switch_name, _, _, _) in enumerate(right_switches):
            diode_name = right_diodes[i][0]
            expected_diode = switch_name.replace('SW', 'D')
            self.assertEqual(diode_name, expected_diode)

    def test_generate_all_positions_symmetry(self):
        """Test that left and right halves have proper symmetry."""
        positions = KeyboardLayoutCalculator.generate_all_positions(self.config)
        
        # Check that left and right have same number of components
        for component_type in ['switches', 'diodes']:
            left_count = len(positions['left'][component_type])
            right_count = len(positions['right'][component_type])
            self.assertEqual(left_count, right_count)
        
        # The right half reverses column order, so we need to map correctly
        # For main keys: left switch at (row, col) corresponds to right switch at (row, num_cols-1-col)
        # But the indexing in the results is sequential, so we need to calculate the mapping
        
        main_keys = self.config.num_rows * self.config.num_cols
        thumb_keys = self.config.num_thumb_keys
        
        left_switches = positions['left']['switches']
        right_switches = positions['right']['switches']
        
        # Test main keys symmetry
        for row in range(self.config.num_rows):
            for col in range(self.config.num_cols):
                # Left index: row * num_cols + col
                left_idx = row * self.config.num_cols + col
                # Right index: row * num_cols + (num_cols - 1 - col)
                right_idx = row * self.config.num_cols + (self.config.num_cols - 1 - col)
                
                left_y = left_switches[left_idx][2]  # Y coordinate
                right_y = right_switches[right_idx][2]  # Y coordinate
                self.assertAlmostEqual(left_y, right_y, places=2)
        
        # Test thumb keys symmetry (they should have same Y coordinates)
        for thumb_idx in range(thumb_keys):
            left_thumb_idx = main_keys + thumb_idx
            right_thumb_idx = main_keys + thumb_idx
            
            left_y = left_switches[left_thumb_idx][2]
            right_y = right_switches[right_thumb_idx][2]
            self.assertAlmostEqual(left_y, right_y, places=2)

    def test_edge_cases(self):
        """Test edge cases and boundary conditions."""
        # Test with zero thumb keys
        zero_thumb_config = KeyboardLayoutConfig(
            origin_x=10.0,
            origin_y=20.0,
            num_rows=3,
            column_stagger=self.column_stagger,
            num_thumb_keys=0,
            thumb_arc_col_start=2,
            thumb_arc_config=self.thumb_arc_config,
            specific_positions=[]
        )
        
        positions = KeyboardLayoutCalculator.generate_all_positions(zero_thumb_config)
        expected_keys = zero_thumb_config.num_rows * zero_thumb_config.num_cols
        
        self.assertEqual(len(positions['left']['switches']), expected_keys)
        self.assertEqual(len(positions['right']['switches']), expected_keys)

    def test_coordinate_precision(self):
        """Test that coordinates maintain reasonable precision."""
        positions = KeyboardLayoutCalculator.generate_all_positions(self.config)
        
        # Check that all coordinates are finite numbers
        for half in ['left', 'right']:
            for component_type in ['switches', 'diodes']:
                for name, x, y, rotation in positions[half][component_type]:
                    self.assertTrue(math.isfinite(x), f"Non-finite X coordinate for {name}")
                    self.assertTrue(math.isfinite(y), f"Non-finite Y coordinate for {name}")
                    self.assertTrue(math.isfinite(rotation), f"Non-finite rotation for {name}")


if __name__ == '__main__':
    unittest.main()
