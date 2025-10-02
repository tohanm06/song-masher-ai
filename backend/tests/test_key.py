"""
Key Detection Tests
Test synthetic chroma analysis and Camelot mapping.
"""

import pytest
import numpy as np
from analysis import AudioAnalyzer

class TestKeyDetection:
    """Test key detection accuracy with synthetic data."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = AudioAnalyzer()
    
    def test_c_major_chroma(self):
        """Test C major key detection."""
        # Create synthetic C major chroma
        chroma = np.array([1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 0.0, 0.0])
        
        # Test key detection
        key, camelot = self.analyzer._analyze_key_from_chroma(chroma)
        
        assert key == "C"
        assert camelot == "8B"
    
    def test_a_minor_chroma(self):
        """Test A minor key detection."""
        # Create synthetic A minor chroma
        chroma = np.array([1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0, 1.0, 1.0, 0.0, 1.0, 0.0])
        
        # Test key detection
        key, camelot = self.analyzer._analyze_key_from_chroma(chroma)
        
        assert key == "Am"
        assert camelot == "8A"
    
    def test_key_compatibility_matrix(self):
        """Test Camelot wheel compatibility."""
        from planning import MashupPlanner
        
        planner = MashupPlanner()
        
        # Test perfect match
        score = planner.key_compatibility["8B"]["8B"]
        assert score == 0
        
        # Test adjacent keys
        score = planner.key_compatibility["8B"]["9B"]
        assert score == 1
        
        # Test opposite keys
        score = planner.key_compatibility["8B"]["2B"]
        assert score == 5
    
    def test_key_shift_calculation(self):
        """Test key shift calculation."""
        from planning import MashupPlanner
        
        planner = MashupPlanner()
        
        # Test same key
        shift = planner._calculate_key_shift("8B", "8B")
        assert shift == 0
        
        # Test adjacent key
        shift = planner._calculate_key_shift("8B", "9B")
        assert shift == 1
        
        # Test opposite key
        shift = planner._calculate_key_shift("8B", "2B")
        assert shift == 6
    
    def test_synthetic_audio_key_detection(self):
        """Test key detection with synthetic audio."""
        # Create synthetic C major chord
        sr = 44100
        duration = 2.0
        t = np.linspace(0, duration, int(sr * duration), False)
        
        # C major chord frequencies
        frequencies = [261.63, 329.63, 392.00]  # C, E, G
        
        # Generate chord
        audio = np.zeros_like(t)
        for freq in frequencies:
            audio += np.sin(2 * np.pi * freq * t)
        
        # Normalize
        audio = audio / np.max(np.abs(audio))
        
        # Save temporary file
        import tempfile
        import soundfile as sf
        
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            sf.write(tmp_file.name, audio, sr)
            
            try:
                # Analyze
                result = self.analyzer.analyze(tmp_file.name)
                
                # Should detect C major
                assert result["key"] == "C"
                assert result["camelot"] == "8B"
                
            finally:
                import os
                os.unlink(tmp_file.name)

# Add helper method to AudioAnalyzer for testing
def _analyze_key_from_chroma(self, chroma: np.ndarray) -> tuple:
    """Analyze key from chroma vector (for testing)."""
    # Krumhansl-Schmuckler key profiles
    major_profile = np.array([6.35, 2.23, 3.48, 2.33, 4.38, 4.09, 2.52, 5.19, 2.39, 3.66, 2.29, 2.88])
    minor_profile = np.array([6.33, 2.68, 3.52, 5.38, 2.60, 3.53, 2.54, 4.75, 3.98, 2.69, 3.34, 3.17])
    
    # Normalize profiles
    major_profile = major_profile / np.sum(major_profile)
    minor_profile = minor_profile / np.sum(minor_profile)
    
    # Correlate with all 24 keys
    keys = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    correlations = []
    
    for i, key in enumerate(keys):
        # Major key correlation
        major_corr = np.corrcoef(chroma, np.roll(major_profile, i))[0, 1]
        correlations.append(('major', key, major_corr))
        
        # Minor key correlation
        minor_corr = np.corrcoef(chroma, np.roll(minor_profile, i))[0, 1]
        correlations.append(('minor', key, minor_corr))
    
    # Find best match
    best_mode, best_key, best_corr = max(correlations, key=lambda x: x[2])
    
    # Convert to Camelot wheel
    camelot_map = {
        'C': '8B', 'C#': '3B', 'D': '10B', 'D#': '5B', 'E': '12B', 'F': '7B',
        'F#': '2B', 'G': '9B', 'G#': '4B', 'A': '11B', 'A#': '6B', 'B': '1B'
    }
    
    if best_mode == 'minor':
        # Minor keys are 3 semitones up from major
        minor_to_major = {
            'C': 'A', 'C#': 'A#', 'D': 'B', 'D#': 'C', 'E': 'C#', 'F': 'D',
            'F#': 'D#', 'G': 'E', 'G#': 'F', 'A': 'F#', 'A#': 'G', 'B': 'G#'
        }
        major_key = minor_to_major[best_key]
        camelot = camelot_map[major_key]
    else:
        camelot = camelot_map[best_key]
    
    return f"{best_key}{best_mode[0].upper()}", camelot

# Monkey patch the method for testing
AudioAnalyzer._analyze_key_from_chroma = _analyze_key_from_chroma
