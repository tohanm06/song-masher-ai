"""
Beat Analysis Tests
Test beat tracking accuracy with metronome tracks.
"""

import pytest
import numpy as np
import soundfile as sf
import tempfile
import os
from analysis import AudioAnalyzer

class TestBeatAnalysis:
    """Test beat tracking accuracy with synthetic metronome tracks."""
    
    def setup_method(self):
        """Set up test fixtures."""
        self.analyzer = AudioAnalyzer()
        self.sr = 44100
    
    def test_metronome_120_bpm(self):
        """Test beat tracking with 120 BPM metronome."""
        # Create 120 BPM metronome track
        duration = 10.0  # 10 seconds
        bpm = 120.0
        beat_interval = 60.0 / bpm  # 0.5 seconds
        
        # Generate metronome clicks
        t = np.linspace(0, duration, int(self.sr * duration), False)
        audio = np.zeros_like(t)
        
        # Add clicks at beat intervals
        for i in range(int(duration / beat_interval)):
            click_time = i * beat_interval
            click_start = int(click_time * self.sr)
            click_end = min(click_start + int(0.01 * self.sr), len(audio))
            
            if click_start < len(audio):
                # Generate click (short sine wave)
                click_duration = click_end - click_start
                click_t = np.linspace(0, 0.01, click_duration, False)
                click = np.sin(2 * np.pi * 1000 * click_t) * np.exp(-click_t * 50)
                audio[click_start:click_end] = click
        
        # Analyze
        result = self._analyze_audio(audio)
        
        # Check BPM accuracy (within ±2 BPM)
        assert abs(result["bpm"] - bpm) <= 2.0
        
        # Check beat timing accuracy (within ±20ms)
        expected_beats = np.arange(0, duration, beat_interval)
        detected_beats = np.array(result["beats"])
        
        for expected_beat in expected_beats:
            # Find closest detected beat
            closest_idx = np.argmin(np.abs(detected_beats - expected_beat))
            closest_beat = detected_beats[closest_idx]
            error_ms = abs(closest_beat - expected_beat) * 1000
            
            assert error_ms <= 20.0, f"Beat timing error: {error_ms}ms"
    
    def test_metronome_140_bpm(self):
        """Test beat tracking with 140 BPM metronome."""
        # Create 140 BPM metronome track
        duration = 8.0  # 8 seconds
        bpm = 140.0
        beat_interval = 60.0 / bpm  # ~0.429 seconds
        
        # Generate metronome clicks
        t = np.linspace(0, duration, int(self.sr * duration), False)
        audio = np.zeros_like(t)
        
        # Add clicks at beat intervals
        for i in range(int(duration / beat_interval)):
            click_time = i * beat_interval
            click_start = int(click_time * self.sr)
            click_end = min(click_start + int(0.01 * self.sr), len(audio))
            
            if click_start < len(audio):
                # Generate click
                click_duration = click_end - click_start
                click_t = np.linspace(0, 0.01, click_duration, False)
                click = np.sin(2 * np.pi * 1000 * click_t) * np.exp(-click_t * 50)
                audio[click_start:click_end] = click
        
        # Analyze
        result = self._analyze_audio(audio)
        
        # Check BPM accuracy
        assert abs(result["bpm"] - bpm) <= 2.0
        
        # Check beat timing accuracy
        expected_beats = np.arange(0, duration, beat_interval)
        detected_beats = np.array(result["beats"])
        
        for expected_beat in expected_beats:
            closest_idx = np.argmin(np.abs(detected_beats - expected_beat))
            closest_beat = detected_beats[closest_idx]
            error_ms = abs(closest_beat - expected_beat) * 1000
            
            assert error_ms <= 20.0, f"Beat timing error: {error_ms}ms"
    
    def test_downbeat_detection(self):
        """Test downbeat detection with 4/4 time signature."""
        # Create 4/4 metronome with emphasis on downbeats
        duration = 8.0  # 8 seconds
        bpm = 120.0
        beat_interval = 60.0 / bpm
        measure_interval = beat_interval * 4  # 4 beats per measure
        
        # Generate metronome with downbeat emphasis
        t = np.linspace(0, duration, int(self.sr * duration), False)
        audio = np.zeros_like(t)
        
        for i in range(int(duration / beat_interval)):
            beat_time = i * beat_interval
            beat_start = int(beat_time * self.sr)
            beat_end = min(beat_start + int(0.01 * self.sr), len(audio))
            
            if beat_start < len(audio):
                # Check if this is a downbeat (every 4th beat)
                is_downbeat = (i % 4) == 0
                
                # Generate click with emphasis for downbeats
                click_duration = beat_end - beat_start
                click_t = np.linspace(0, 0.01, click_duration, False)
                
                if is_downbeat:
                    # Louder click for downbeat
                    click = np.sin(2 * np.pi * 1000 * click_t) * np.exp(-click_t * 30) * 1.5
                else:
                    # Normal click
                    click = np.sin(2 * np.pi * 1000 * click_t) * np.exp(-click_t * 50)
                
                audio[beat_start:beat_end] = click
        
        # Analyze
        result = self._analyze_audio(audio)
        
        # Check that downbeats are detected
        assert len(result["downbeats"]) > 0
        
        # Check downbeat timing accuracy
        expected_downbeats = np.arange(0, duration, measure_interval)
        detected_downbeats = np.array(result["downbeats"])
        
        for expected_downbeat in expected_downbeats:
            closest_idx = np.argmin(np.abs(detected_downbeats - expected_downbeat))
            closest_downbeat = detected_downbeats[closest_idx]
            error_ms = abs(closest_downbeat - expected_downbeat) * 1000
            
            assert error_ms <= 40.0, f"Downbeat timing error: {error_ms}ms"
    
    def test_variable_tempo(self):
        """Test beat tracking with variable tempo."""
        # Create track with tempo change from 120 to 140 BPM
        duration = 10.0
        t = np.linspace(0, duration, int(self.sr * duration), False)
        audio = np.zeros_like(t)
        
        # First half: 120 BPM
        first_half_duration = duration / 2
        first_half_beats = np.arange(0, first_half_duration, 60.0 / 120.0)
        
        # Second half: 140 BPM
        second_half_start = duration / 2
        second_half_beats = np.arange(second_half_start, duration, 60.0 / 140.0)
        
        all_beats = np.concatenate([first_half_beats, second_half_beats])
        
        # Generate clicks
        for beat_time in all_beats:
            click_start = int(beat_time * self.sr)
            click_end = min(click_start + int(0.01 * self.sr), len(audio))
            
            if click_start < len(audio):
                click_duration = click_end - click_start
                click_t = np.linspace(0, 0.01, click_duration, False)
                click = np.sin(2 * np.pi * 1000 * click_t) * np.exp(-click_t * 50)
                audio[click_start:click_end] = click
        
        # Analyze
        result = self._analyze_audio(audio)
        
        # Should detect average tempo around 130 BPM
        assert 125 <= result["bpm"] <= 135
        
        # Check that beats are detected reasonably well
        detected_beats = np.array(result["beats"])
        assert len(detected_beats) >= len(all_beats) * 0.8  # At least 80% of beats detected
    
    def _analyze_audio(self, audio: np.ndarray) -> dict:
        """Analyze audio and return results."""
        # Save to temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            sf.write(tmp_file.name, audio, self.sr)
            
            try:
                # Analyze
                result = self.analyzer.analyze(tmp_file.name)
                return result
            finally:
                os.unlink(tmp_file.name)
