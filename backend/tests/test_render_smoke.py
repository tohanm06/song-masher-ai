"""
Render Smoke Tests
Test rendering pipeline with 10-second fixtures.
"""

import pytest
import numpy as np
import soundfile as sf
import tempfile
import os
from render import MashupRenderer

class TestRenderSmoke:
    """Test rendering pipeline with synthetic fixtures."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.renderer = MashupRenderer()
        self.sr = 44100
        self.duration = 10.0  # 10 seconds for quick testing
    
    def test_render_pipeline_no_clipping(self):
        """Test that rendered audio has no clipping."""
        # Create test stems
        stems = self._create_test_stems()
        
        # Create test plan
        plan = {
            "recipe": "AoverB",
            "targetKey": "C",
            "keyShiftA": 0,
            "keyShiftB": 0,
            "stretchMap": {
                "targetBpm": 120,
                "stretchA": 1.0,
                "stretchB": 1.0
            },
            "sectionPairs": [
                {
                    "sectionA": {"start": 0, "end": 10, "label": "verse"},
                    "sectionB": {"start": 0, "end": 10, "label": "verse"},
                    "alignment": 0,
                    "confidence": 0.8
                }
            ]
        }
        
        # Create test mix parameters
        mix_params = {
            "vocals_gain": 1.0,
            "drums_gain": 0.8,
            "bass_gain": 0.7,
            "other_gain": 0.6,
            "auto_eq": True,
            "sidechain_ducking": True,
            "de_esser": True
        }
        
        # Render mashup
        output_path = self.renderer.render(stems, plan, mix_params)
        
        # Load and check output
        audio, sr = sf.read(output_path)
        
        # Check for clipping
        max_amplitude = np.max(np.abs(audio))
        assert max_amplitude <= 0.99, f"Audio clipped at {max_amplitude:.3f}"
        
        # Check sample rate
        assert sr == self.sr
        
        # Check duration (should be close to 10 seconds)
        duration = len(audio) / sr
        assert 9.5 <= duration <= 10.5, f"Duration {duration:.2f}s not close to 10s"
        
        # Clean up
        os.unlink(output_path)
        for stem_path in stems.values():
            os.unlink(stem_path)
    
    def test_lufs_normalization(self):
        """Test LUFS normalization to -14 ±0.5 LUFS."""
        # Create test stems with various loudness levels
        stems = self._create_test_stems()
        
        # Create plan
        plan = {
            "recipe": "AoverB",
            "targetKey": "C",
            "keyShiftA": 0,
            "keyShiftB": 0,
            "stretchMap": {
                "targetBpm": 120,
                "stretchA": 1.0,
                "stretchB": 1.0
            },
            "sectionPairs": [
                {
                    "sectionA": {"start": 0, "end": 10, "label": "verse"},
                    "sectionB": {"start": 0, "end": 10, "label": "verse"},
                    "alignment": 0,
                    "confidence": 0.8
                }
            ]
        }
        
        # Mix parameters
        mix_params = {
            "vocals_gain": 1.0,
            "drums_gain": 0.8,
            "bass_gain": 0.7,
            "other_gain": 0.6
        }
        
        # Render mashup
        output_path = self.renderer.render(stems, plan, mix_params)
        
        # Check LUFS level
        audio, sr = sf.read(output_path)
        lufs = self._measure_lufs(audio, sr)
        
        # Should be within -14 ±0.5 LUFS
        assert -14.5 <= lufs <= -13.5, f"LUFS level {lufs:.2f} not within -14 ±0.5"
        
        # Clean up
        os.unlink(output_path)
        for stem_path in stems.values():
            os.unlink(stem_path)
    
    def test_headroom_management(self):
        """Test that headroom is properly managed."""
        # Create test stems
        stems = self._create_test_stems()
        
        # Create plan
        plan = {
            "recipe": "AoverB",
            "targetKey": "C",
            "keyShiftA": 0,
            "keyShiftB": 0,
            "stretchMap": {
                "targetBpm": 120,
                "stretchA": 1.0,
                "stretchB": 1.0
            },
            "sectionPairs": [
                {
                    "sectionA": {"start": 0, "end": 10, "label": "verse"},
                    "sectionB": {"start": 0, "end": 10, "label": "verse"},
                    "alignment": 0,
                    "confidence": 0.8
                }
            ]
        }
        
        # Mix parameters
        mix_params = {
            "vocals_gain": 1.0,
            "drums_gain": 0.8,
            "bass_gain": 0.7,
            "other_gain": 0.6
        }
        
        # Render mashup
        output_path = self.renderer.render(stems, plan, mix_params)
        
        # Check headroom
        audio, sr = sf.read(output_path)
        max_amplitude = np.max(np.abs(audio))
        
        # Should have at least 1 dB headroom (0.89 linear)
        assert max_amplitude <= 0.89, f"Headroom insufficient: {max_amplitude:.3f}"
        
        # Clean up
        os.unlink(output_path)
        for stem_path in stems.values():
            os.unlink(stem_path)
    
    def test_recipe_variations(self):
        """Test different recipe strategies."""
        stems = self._create_test_stems()
        
        recipes = ["AoverB", "BoverA", "HybridDrums"]
        
        for recipe in recipes:
            # Create plan for this recipe
            plan = {
                "recipe": recipe,
                "targetKey": "C",
                "keyShiftA": 0,
                "keyShiftB": 0,
                "stretchMap": {
                    "targetBpm": 120,
                    "stretchA": 1.0,
                    "stretchB": 1.0
                },
                "sectionPairs": [
                    {
                        "sectionA": {"start": 0, "end": 10, "label": "verse"},
                        "sectionB": {"start": 0, "end": 10, "label": "verse"},
                        "alignment": 0,
                        "confidence": 0.8
                    }
                ]
            }
            
            # Mix parameters
            mix_params = {
                "vocals_gain": 1.0,
                "drums_gain": 0.8,
                "bass_gain": 0.7,
                "other_gain": 0.6
            }
            
            # Render mashup
            output_path = self.renderer.render(stems, plan, mix_params)
            
            # Check output
            audio, sr = sf.read(output_path)
            
            # Should not clip
            max_amplitude = np.max(np.abs(audio))
            assert max_amplitude <= 0.99, f"Recipe {recipe} clipped at {max_amplitude:.3f}"
            
            # Should have reasonable duration
            duration = len(audio) / sr
            assert 9.5 <= duration <= 10.5, f"Recipe {recipe} duration {duration:.2f}s not close to 10s"
            
            # Clean up
            os.unlink(output_path)
    
    def test_pitch_time_transforms(self):
        """Test pitch and time transformations."""
        stems = self._create_test_stems()
        
        # Create plan with transformations
        plan = {
            "recipe": "AoverB",
            "targetKey": "C",
            "keyShiftA": 2,  # 2 semitones up
            "keyShiftB": -1,  # 1 semitone down
            "stretchMap": {
                "targetBpm": 120,
                "stretchA": 1.2,  # 20% slower
                "stretchB": 0.8   # 20% faster
            },
            "sectionPairs": [
                {
                    "sectionA": {"start": 0, "end": 10, "label": "verse"},
                    "sectionB": {"start": 0, "end": 10, "label": "verse"},
                    "alignment": 0,
                    "confidence": 0.8
                }
            ]
        }
        
        # Mix parameters
        mix_params = {
            "vocals_gain": 1.0,
            "drums_gain": 0.8,
            "bass_gain": 0.7,
            "other_gain": 0.6
        }
        
        # Render mashup
        output_path = self.renderer.render(stems, plan, mix_params)
        
        # Check output
        audio, sr = sf.read(output_path)
        
        # Should not clip
        max_amplitude = np.max(np.abs(audio))
        assert max_amplitude <= 0.99, f"Transformed audio clipped at {max_amplitude:.3f}"
        
        # Duration should be affected by stretch ratios
        duration = len(audio) / sr
        # With stretch ratios of 1.2 and 0.8, duration should be around 10s
        assert 9.0 <= duration <= 11.0, f"Transformed duration {duration:.2f}s not expected"
        
        # Clean up
        os.unlink(output_path)
        for stem_path in stems.values():
            os.unlink(stem_path)
    
    def _create_test_stems(self) -> dict:
        """Create test stem files."""
        stems = {}
        
        # Generate test audio
        t = np.linspace(0, self.duration, int(self.sr * self.duration), False)
        
        # Vocals: sine wave at 440 Hz
        vocals = np.sin(2 * np.pi * 440 * t) * 0.5
        
        # Drums: percussive pattern
        drums = np.zeros_like(t)
        for i in range(int(self.duration * 2)):  # 2 beats per second
            beat_time = i * 0.5
            if beat_time < self.duration:
                beat_start = int(beat_time * self.sr)
                beat_end = min(beat_start + int(0.01 * self.sr), len(drums))
                drums[beat_start:beat_end] = np.random.normal(0, 0.3, beat_end - beat_start)
        
        # Bass: sine wave at 110 Hz
        bass = np.sin(2 * np.pi * 110 * t) * 0.3
        
        # Other: chord progression
        other = np.zeros_like(t)
        chord_freqs = [261.63, 329.63, 392.00]  # C major chord
        for freq in chord_freqs:
            other += np.sin(2 * np.pi * freq * t) * 0.2
        
        # Save stems to temporary files
        stem_data = {
            "vocals": vocals,
            "drums": drums,
            "bass": bass,
            "other": other
        }
        
        for stem_name, audio in stem_data.items():
            with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
                sf.write(tmp_file.name, audio, self.sr)
                stems[stem_name] = tmp_file.name
        
        return stems
    
    def _measure_lufs(self, audio: np.ndarray, sr: int) -> float:
        """Measure LUFS level of audio."""
        try:
            import pyloudnorm as pyln
            
            # Create loudness meter
            meter = pyln.Meter(sr)
            
            # Measure loudness
            lufs = meter.integrated_loudness(audio)
            
            return float(lufs)
        except ImportError:
            # Fallback: estimate from RMS
            rms = np.sqrt(np.mean(audio**2))
            # Rough conversion (not accurate)
            lufs = 20 * np.log10(rms) - 3
            return float(lufs)
