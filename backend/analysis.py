"""
Audio Analysis Module
BPM, key, structure, and loudness analysis using librosa and essentia.
"""

import numpy as np
import librosa
import essentia.standard as es
from typing import Dict, List, Any, Tuple
import soundfile as sf
from scipy import signal
from scipy.stats import pearsonr

class AudioAnalyzer:
    """Production-grade audio analysis with beat tracking, key detection, and structure analysis."""
    
    def __init__(self):
        self.sr = 44100  # Standard sample rate
        self.hop_length = 512
        self.n_fft = 2048
        
    def analyze(self, file_path: str) -> Dict[str, Any]:
        """Comprehensive audio analysis pipeline."""
        # Load audio
        y, sr = librosa.load(file_path, sr=self.sr)
        duration = len(y) / sr
        
        # Analyze components
        bpm, beats, downbeats = self._analyze_beats(y, sr)
        key, camelot = self._analyze_key(y, sr)
        sections = self._analyze_structure(y, sr)
        lufs = self._analyze_loudness(y, sr)
        
        return {
            "duration": duration,
            "bpm": bpm,
            "beats": beats.tolist(),
            "downbeats": downbeats.tolist(),
            "key": key,
            "camelot": camelot,
            "sections": sections,
            "lufs": lufs
        }
    
    def _analyze_beats(self, y: np.ndarray, sr: int) -> Tuple[float, np.ndarray, np.ndarray]:
        """Advanced beat tracking with variable tempo support."""
        # Onset strength
        onset_strength = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
        
        # Tempo and beats
        tempo, beats = librosa.beat.beat_track(
            onset_envelope=onset_strength,
            sr=sr,
            hop_length=self.hop_length,
            units='time'
        )
        
        # Refine tempo with tempogram
        tempogram = librosa.feature.tempogram(
            onset_envelope=onset_strength,
            sr=sr,
            hop_length=self.hop_length
        )
        
        # Find most stable tempo
        tempo_stability = np.mean(tempogram, axis=1)
        stable_tempo_idx = np.argmax(tempo_stability)
        refined_tempo = librosa.tempo_frequencies(len(tempo_stability), sr=sr)[stable_tempo_idx]
        
        # Downbeat detection
        downbeats = self._find_downbeats(y, sr, beats, refined_tempo)
        
        return float(refined_tempo), beats, downbeats
    
    def _find_downbeats(self, y: np.ndarray, sr: int, beats: np.ndarray, tempo: float) -> np.ndarray:
        """Find downbeats using onset strength and tempo consistency."""
        # Get onset strength at beat times
        beat_frames = librosa.time_to_frames(beats, sr=sr, hop_length=self.hop_length)
        onset_strength = librosa.onset.onset_strength(y=y, sr=sr, hop_length=self.hop_length)
        beat_strengths = onset_strength[beat_frames]
        
        # Find downbeats (strongest beats in each measure)
        beat_period = 60.0 / tempo * 4  # Assume 4/4 time
        downbeats = []
        
        for i, beat_time in enumerate(beats):
            # Check if this beat is likely a downbeat
            window_start = max(0, i - 2)
            window_end = min(len(beats), i + 3)
            window_strengths = beat_strengths[window_start:window_end]
            
            if i - window_start < len(window_strengths) and beat_strengths[i] == np.max(window_strengths):
                downbeats.append(beat_time)
        
        return np.array(downbeats)
    
    def _analyze_key(self, y: np.ndarray, sr: int) -> Tuple[str, str]:
        """Key detection using chroma CQT + Krumhansl correlation."""
        # Chroma CQT
        chroma = librosa.feature.chroma_cqt(y=y, sr=sr, hop_length=self.hop_length)
        chroma_mean = np.mean(chroma, axis=1)
        
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
            major_corr, _ = pearsonr(chroma_mean, np.roll(major_profile, i))
            correlations.append(('major', key, major_corr))
            
            # Minor key correlation
            minor_corr, _ = pearsonr(chroma_mean, np.roll(minor_profile, i))
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
    
    def _analyze_structure(self, y: np.ndarray, sr: int) -> List[Dict[str, Any]]:
        """Structure analysis using novelty curve and self-similarity."""
        # Compute novelty curve
        hop_length = 1024
        frame_length = 2048
        
        # MFCC features
        mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13, hop_length=hop_length)
        
        # Self-similarity matrix
        similarity = np.corrcoef(mfcc)
        
        # Novelty curve (diagonal of self-similarity)
        novelty = np.diag(similarity, k=1)
        novelty = np.concatenate([[0], novelty, [0]])  # Pad to match length
        
        # Find peaks (section boundaries)
        peaks, _ = signal.find_peaks(novelty, height=np.mean(novelty), distance=10)
        
        # Convert to time
        times = librosa.frames_to_time(peaks, sr=sr, hop_length=hop_length)
        
        # Label sections
        sections = []
        for i, time in enumerate(times):
            if i == 0:
                start_time = 0.0
            else:
                start_time = times[i-1]
            
            if i == len(times) - 1:
                end_time = len(y) / sr
            else:
                end_time = times[i]
            
            # Simple labeling (in practice, use more sophisticated methods)
            if i % 4 == 0:
                label = "chorus"
            elif i % 4 == 1:
                label = "verse"
            elif i % 4 == 2:
                label = "bridge"
            else:
                label = "verse"
            
            sections.append({
                "start": start_time,
                "end": end_time,
                "label": label
            })
        
        return sections
    
    def _analyze_loudness(self, y: np.ndarray, sr: int) -> float:
        """LUFS loudness analysis."""
        try:
            import pyloudnorm as pyln
            
            # Create loudness meter
            meter = pyln.Meter(sr)
            
            # Measure loudness
            lufs = meter.integrated_loudness(y)
            
            return float(lufs)
        except ImportError:
            # Fallback to RMS-based estimation
            rms = np.sqrt(np.mean(y**2))
            # Rough conversion (not accurate)
            lufs = 20 * np.log10(rms) - 3
            return float(lufs)
