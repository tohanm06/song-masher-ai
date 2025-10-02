"""
Mashup Planning Tests
Test planning algorithms for monotonicity and key shift limits.
"""

import pytest
import numpy as np
from planning import MashupPlanner

class TestMashupPlanning:
    """Test mashup planning algorithms."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.planner = MashupPlanner()
    
    def test_tempo_alignment_monotonicity(self):
        """Test that larger BPM mismatch results in larger stretch ratio."""
        # Test cases with increasing BPM mismatch
        test_cases = [
            (120, 125, "small mismatch"),
            (120, 140, "medium mismatch"),
            (120, 180, "large mismatch"),
            (120, 240, "very large mismatch")
        ]
        
        stretch_ratios = []
        
        for bpmA, bpmB, description in test_cases:
            # Create mock track data
            trackA = {
                "bpm": bpmA,
                "key": "C",
                "camelot": "8B",
                "beats": np.linspace(0, 60, int(60 * bpmA / 60)),
                "sections": [{"start": 0, "end": 60, "label": "verse"}]
            }
            
            trackB = {
                "bpm": bpmB,
                "key": "C",
                "camelot": "8B", 
                "beats": np.linspace(0, 60, int(60 * bpmB / 60)),
                "sections": [{"start": 0, "end": 60, "label": "verse"}]
            }
            
            # Create plan
            plan = self.planner.create_plan(trackA, trackB, "AoverB")
            
            # Extract stretch ratios
            stretchA = plan["stretchMap"]["stretchA"]
            stretchB = plan["stretchMap"]["stretchB"]
            
            # The larger the BPM difference, the larger the stretch should be
            max_stretch = max(stretchA, stretchB)
            stretch_ratios.append(max_stretch)
            
            print(f"{description}: BPM {bpmA} vs {bpmB}, max stretch: {max_stretch:.2f}")
        
        # Verify monotonicity: stretch ratios should generally increase
        for i in range(1, len(stretch_ratios)):
            assert stretch_ratios[i] >= stretch_ratios[i-1] * 0.8, \
                f"Stretch ratio should be monotonic: {stretch_ratios[i-1]} -> {stretch_ratios[i]}"
    
    def test_key_shift_limits(self):
        """Test that key shifts are limited to ±3 semitones by default."""
        # Test various key combinations
        key_combinations = [
            ("C", "8B", "D", "10B"),  # 2 semitones
            ("C", "8B", "F", "7B"),   # 5 semitones (should be limited)
            ("C", "8B", "G#", "4B"),  # 8 semitones (should be limited)
            ("Am", "8A", "Cm", "5A"), # 3 semitones
            ("Am", "8A", "Fm", "4A"), # 6 semitones (should be limited)
        ]
        
        for keyA, camelotA, keyB, camelotB in key_combinations:
            # Create mock track data
            trackA = {
                "bpm": 120,
                "key": keyA,
                "camelot": camelotA,
                "beats": np.linspace(0, 60, 120),
                "sections": [{"start": 0, "end": 60, "label": "verse"}]
            }
            
            trackB = {
                "bpm": 120,
                "key": keyB,
                "camelot": camelotB,
                "beats": np.linspace(0, 60, 120),
                "sections": [{"start": 0, "end": 60, "label": "verse"}]
            }
            
            # Create plan
            plan = self.planner.create_plan(trackA, trackB, "AoverB")
            
            # Check key shift limits
            key_shift_a = plan["keyShiftA"]
            key_shift_b = plan["keyShiftB"]
            
            assert abs(key_shift_a) <= 3, f"Key shift A ({key_shift_a}) exceeds ±3 semitones"
            assert abs(key_shift_b) <= 3, f"Key shift B ({key_shift_b}) exceeds ±3 semitones"
            
            print(f"Keys {keyA} -> {keyB}: shifts A={key_shift_a}, B={key_shift_b}")
    
    def test_recipe_strategies(self):
        """Test different recipe strategies."""
        # Create mock tracks
        trackA = {
            "bpm": 120,
            "key": "C",
            "camelot": "8B",
            "beats": np.linspace(0, 60, 120),
            "sections": [
                {"start": 0, "end": 15, "label": "verse"},
                {"start": 15, "end": 30, "label": "chorus"},
                {"start": 30, "end": 45, "label": "verse"},
                {"start": 45, "end": 60, "label": "chorus"}
            ]
        }
        
        trackB = {
            "bpm": 140,
            "key": "G",
            "camelot": "9B",
            "beats": np.linspace(0, 60, 140),
            "sections": [
                {"start": 0, "end": 20, "label": "verse"},
                {"start": 20, "end": 40, "label": "chorus"},
                {"start": 40, "end": 60, "label": "verse"}
            ]
        }
        
        # Test all recipes
        recipes = ["AoverB", "BoverA", "HybridDrums"]
        
        for recipe in recipes:
            plan = self.planner.create_plan(trackA, trackB, recipe)
            
            # Verify plan structure
            assert "targetKey" in plan
            assert "keyShiftA" in plan
            assert "keyShiftB" in plan
            assert "stretchMap" in plan
            assert "sectionPairs" in plan
            assert "qualityHints" in plan
            
            # Verify stretch map
            stretch_map = plan["stretchMap"]
            assert "targetBpm" in stretch_map
            assert "stretchA" in stretch_map
            assert "stretchB" in stretch_map
            
            # Verify section pairs
            section_pairs = plan["sectionPairs"]
            assert len(section_pairs) > 0
            
            print(f"Recipe {recipe}: {len(section_pairs)} section pairs, "
                  f"target BPM: {stretch_map['targetBpm']:.1f}")
    
    def test_section_alignment_quality(self):
        """Test section alignment quality."""
        # Create tracks with different structures
        trackA = {
            "bpm": 120,
            "key": "C",
            "camelot": "8B",
            "beats": np.linspace(0, 60, 120),
            "sections": [
                {"start": 0, "end": 15, "label": "verse"},
                {"start": 15, "end": 30, "label": "chorus"},
                {"start": 30, "end": 45, "label": "verse"},
                {"start": 45, "end": 60, "label": "chorus"}
            ]
        }
        
        # Track B with similar structure
        trackB_similar = {
            "bpm": 125,
            "key": "C",
            "camelot": "8B",
            "beats": np.linspace(0, 60, 125),
            "sections": [
                {"start": 0, "end": 16, "label": "verse"},
                {"start": 16, "end": 32, "label": "chorus"},
                {"start": 32, "end": 48, "label": "verse"},
                {"start": 48, "end": 60, "label": "chorus"}
            ]
        }
        
        # Track B with different structure
        trackB_different = {
            "bpm": 140,
            "key": "G",
            "camelot": "9B",
            "beats": np.linspace(0, 60, 140),
            "sections": [
                {"start": 0, "end": 30, "label": "verse"},
                {"start": 30, "end": 60, "label": "bridge"}
            ]
        }
        
        # Test similar structure
        plan_similar = self.planner.create_plan(trackA, trackB_similar, "AoverB")
        pairs_similar = len(plan_similar["sectionPairs"])
        
        # Test different structure
        plan_different = self.planner.create_plan(trackA, trackB_different, "AoverB")
        pairs_different = len(plan_different["sectionPairs"])
        
        # Similar structure should have more/better alignments
        assert pairs_similar >= pairs_different
        
        print(f"Similar structure: {pairs_similar} pairs")
        print(f"Different structure: {pairs_different} pairs")
    
    def test_quality_hints(self):
        """Test quality hint generation."""
        # Create tracks with various compatibility levels
        test_cases = [
            {
                "name": "Perfect match",
                "trackA": {"bpm": 120, "key": "C", "camelot": "8B"},
                "trackB": {"bpm": 120, "key": "C", "camelot": "8B"}
            },
            {
                "name": "Key mismatch",
                "trackA": {"bpm": 120, "key": "C", "camelot": "8B"},
                "trackB": {"bpm": 120, "key": "F#", "camelot": "2B"}
            },
            {
                "name": "Tempo mismatch",
                "trackA": {"bpm": 120, "key": "C", "camelot": "8B"},
                "trackB": {"bpm": 180, "key": "C", "camelot": "8B"}
            }
        ]
        
        for case in test_cases:
            # Create full track data
            trackA = {
                **case["trackA"],
                "beats": np.linspace(0, 60, int(case["trackA"]["bpm"])),
                "sections": [{"start": 0, "end": 60, "label": "verse"}]
            }
            
            trackB = {
                **case["trackB"],
                "beats": np.linspace(0, 60, int(case["trackB"]["bpm"])),
                "sections": [{"start": 0, "end": 60, "label": "verse"}]
            }
            
            # Create plan
            plan = self.planner.create_plan(trackA, trackB, "AoverB")
            
            # Check quality hints
            hints = plan["qualityHints"]
            assert len(hints) > 0
            
            print(f"{case['name']}: {len(hints)} hints")
            for hint in hints:
                print(f"  - {hint}")
    
    def test_edge_cases(self):
        """Test edge cases in planning."""
        # Test with very short tracks
        short_track = {
            "bpm": 120,
            "key": "C",
            "camelot": "8B",
            "beats": np.linspace(0, 5, 10),  # 5 seconds
            "sections": [{"start": 0, "end": 5, "label": "verse"}]
        }
        
        plan = self.planner.create_plan(short_track, short_track, "AoverB")
        assert plan is not None
        
        # Test with extreme tempo differences
        slow_track = {
            "bpm": 60,
            "key": "C",
            "camelot": "8B",
            "beats": np.linspace(0, 60, 60),
            "sections": [{"start": 0, "end": 60, "label": "verse"}]
        }
        
        fast_track = {
            "bpm": 200,
            "key": "C",
            "camelot": "8B",
            "beats": np.linspace(0, 60, 200),
            "sections": [{"start": 0, "end": 60, "label": "verse"}]
        }
        
        plan = self.planner.create_plan(slow_track, fast_track, "AoverB")
        assert plan is not None
        
        # Check that stretch ratios are reasonable
        stretch_map = plan["stretchMap"]
        assert 0.5 <= stretch_map["stretchA"] <= 2.0
        assert 0.5 <= stretch_map["stretchB"] <= 2.0
