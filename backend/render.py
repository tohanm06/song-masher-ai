"""
Mashup Rendering Module
Rubber Band transforms, mixing, and mastering pipeline.
"""

import os
import tempfile
import numpy as np
import soundfile as sf
from typing import Dict, List, Any, Optional
import subprocess
from pathlib import Path

try:
    import pyloudnorm as pyln
    PYLN_AVAILABLE = True
except ImportError:
    PYLN_AVAILABLE = False

class MashupRenderer:
    """Production-grade mashup rendering with Rubber Band and mastering."""
    
    def __init__(self):
        self.sr = 44100
        self.target_lufs = -14.0
        self.headroom_db = 1.0
        
    def render(self, stems: Dict[str, str], plan: Dict[str, Any], 
               mix_params: Dict[str, Any]) -> str:
        """Render complete mashup with all processing stages."""
        try:
            # Stage 1: Apply tempo/pitch transforms
            transformed_stems = self._apply_transforms(stems, plan)
            
            # Stage 2: Align and mix stems
            mixed_audio = self._mix_stems(transformed_stems, plan, mix_params)
            
            # Stage 3: Apply mixing effects
            processed_audio = self._apply_mixing_effects(mixed_audio, mix_params)
            
            # Stage 4: Mastering
            mastered_audio = self._master_audio(processed_audio)
            
            # Save final output
            output_path = self._save_output(mastered_audio)
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Rendering failed: {str(e)}")
    
    def _apply_transforms(self, stems: Dict[str, str], plan: Dict[str, Any]) -> Dict[str, str]:
        """Apply Rubber Band pitch/time transforms."""
        transformed = {}
        
        for stem_name, stem_path in stems.items():
            if stem_name not in ["vocals", "drums", "bass", "other"]:
                continue
                
            # Determine which track this stem belongs to
            track = "A" if stem_name in ["vocals"] else "B"
            
            # Get transform parameters
            if track == "A":
                stretch_ratio = plan["stretchMap"]["stretchA"]
                pitch_shift = plan["keyShiftA"]
            else:
                stretch_ratio = plan["stretchMap"]["stretchB"]
                pitch_shift = plan["keyShiftB"]
            
            # Apply Rubber Band transform
            transformed_path = self._rubber_band_transform(
                stem_path, stretch_ratio, pitch_shift
            )
            transformed[stem_name] = transformed_path
        
        return transformed
    
    def _rubber_band_transform(self, input_path: str, stretch_ratio: float, 
                              pitch_shift: int) -> str:
        """Apply Rubber Band pitch/time stretching."""
        # Create temporary output file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            output_path = tmp_file.name
        
        try:
            # Rubber Band command
            cmd = [
                "rubberband",
                "--formant",  # Preserve formants for vocals
                "--realtime",  # Faster processing
                "--pitch", str(pitch_shift),
                "--tempo", str(stretch_ratio),
                input_path,
                output_path
            ]
            
            # Run Rubber Band
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode != 0:
                print(f"Rubber Band warning: {result.stderr}")
                # Fallback: copy original file
                import shutil
                shutil.copy2(input_path, output_path)
            
            return output_path
            
        except FileNotFoundError:
            print("Rubber Band not found, using fallback")
            # Fallback: copy original file
            import shutil
            shutil.copy2(input_path, output_path)
            return output_path
    
    def _mix_stems(self, stems: Dict[str, str], plan: Dict[str, Any], 
                   mix_params: Dict[str, Any]) -> np.ndarray:
        """Mix stems according to recipe and alignment."""
        # Load all stems
        stem_audios = {}
        max_length = 0
        
        for stem_name, stem_path in stems.items():
            audio, sr = sf.read(stem_path)
            if sr != self.sr:
                # Resample if needed
                import librosa
                audio = librosa.resample(audio, orig_sr=sr, target_sr=self.sr)
            
            stem_audios[stem_name] = audio
            max_length = max(max_length, len(audio))
        
        # Initialize mix
        mix = np.zeros(max_length)
        
        # Apply recipe-specific mixing
        recipe = plan.get("recipe", "AoverB")
        
        if recipe == "AoverB":
            # A vocals over B instrumental
            if "vocals" in stem_audios:
                mix += stem_audios["vocals"] * mix_params.get("vocals_gain", 1.0)
            if "drums" in stem_audios:
                mix += stem_audios["drums"] * mix_params.get("drums_gain", 0.8)
            if "bass" in stem_audios:
                mix += stem_audios["bass"] * mix_params.get("bass_gain", 0.7)
            if "other" in stem_audios:
                mix += stem_audios["other"] * mix_params.get("other_gain", 0.6)
                
        elif recipe == "BoverA":
            # B vocals over A instrumental
            if "vocals" in stem_audios:
                mix += stem_audios["vocals"] * mix_params.get("vocals_gain", 1.0)
            if "drums" in stem_audios:
                mix += stem_audios["drums"] * mix_params.get("drums_gain", 0.8)
            if "bass" in stem_audios:
                mix += stem_audios["bass"] * mix_params.get("bass_gain", 0.7)
            if "other" in stem_audios:
                mix += stem_audios["other"] * mix_params.get("other_gain", 0.6)
                
        elif recipe == "HybridDrums":
            # Hybrid approach
            if "vocals" in stem_audios:
                mix += stem_audios["vocals"] * mix_params.get("vocals_gain", 1.0)
            if "drums" in stem_audios:
                mix += stem_audios["drums"] * mix_params.get("drums_gain", 0.9)
            if "bass" in stem_audios:
                mix += stem_audios["bass"] * mix_params.get("bass_gain", 0.8)
            if "other" in stem_audios:
                mix += stem_audios["other"] * mix_params.get("other_gain", 0.7)
        
        return mix
    
    def _apply_mixing_effects(self, audio: np.ndarray, mix_params: Dict[str, Any]) -> np.ndarray:
        """Apply mixing effects: EQ, sidechain ducking, crossfades."""
        processed = audio.copy()
        
        # Auto-EQ: Notch filter at 2-5 kHz for backing tracks
        if mix_params.get("auto_eq", True):
            processed = self._apply_auto_eq(processed)
        
        # Sidechain ducking
        if mix_params.get("sidechain_ducking", True):
            processed = self._apply_sidechain_ducking(processed)
        
        # De-esser
        if mix_params.get("de_esser", True):
            processed = self._apply_de_esser(processed)
        
        return processed
    
    def _apply_auto_eq(self, audio: np.ndarray) -> np.ndarray:
        """Apply automatic EQ to reduce masking."""
        # Simple notch filter at 3 kHz
        from scipy import signal
        
        # Design notch filter
        nyquist = self.sr / 2
        low_freq = 2000 / nyquist
        high_freq = 5000 / nyquist
        
        # Butterworth band-stop filter
        b, a = signal.butter(4, [low_freq, high_freq], btype='bandstop')
        
        # Apply filter
        filtered = signal.filtfilt(b, a, audio)
        
        return filtered
    
    def _apply_sidechain_ducking(self, audio: np.ndarray) -> np.ndarray:
        """Apply sidechain ducking for vocal clarity."""
        # Simple sidechain implementation
        # In production, use more sophisticated algorithms
        
        # Detect vocal transients (simplified)
        from scipy import signal
        
        # High-pass filter to isolate vocal frequencies
        nyquist = self.sr / 2
        high_freq = 200 / nyquist
        b, a = signal.butter(2, high_freq, btype='high')
        vocal_band = signal.filtfilt(b, a, audio)
        
        # Envelope follower
        envelope = np.abs(vocal_band)
        envelope = signal.savgol_filter(envelope, 21, 3)  # Smooth envelope
        
        # Apply ducking
        ducking_amount = -3.0  # dB
        ducking_factor = 10 ** (ducking_amount / 20)
        
        ducked = audio * (1 - envelope * (1 - ducking_factor))
        
        return ducked
    
    def _apply_de_esser(self, audio: np.ndarray) -> np.ndarray:
        """Apply de-essing to reduce sibilance."""
        # Simple de-esser implementation
        from scipy import signal
        
        # High-pass filter for sibilance detection
        nyquist = self.sr / 2
        sibilance_freq = 5000 / nyquist
        b, a = signal.butter(2, sibilance_freq, btype='high')
        sibilance_band = signal.filtfilt(b, a, audio)
        
        # Detect sibilance
        sibilance_threshold = 0.1  # Adjust based on analysis
        sibilance_mask = np.abs(sibilance_band) > sibilance_threshold
        
        # Apply reduction
        reduction_db = -6.0
        reduction_factor = 10 ** (reduction_db / 20)
        
        processed = audio.copy()
        processed[sibilance_mask] *= reduction_factor
        
        return processed
    
    def _master_audio(self, audio: np.ndarray) -> np.ndarray:
        """Apply mastering: LUFS normalization and headroom management."""
        # Ensure no clipping
        if np.max(np.abs(audio)) > 0.99:
            audio = audio / np.max(np.abs(audio)) * 0.99
        
        # LUFS normalization
        if PYLN_AVAILABLE:
            audio = self._normalize_lufs(audio)
        else:
            # Fallback: RMS normalization
            audio = self._normalize_rms(audio)
        
        # Apply headroom
        headroom_factor = 10 ** (-self.headroom_db / 20)
        audio *= headroom_factor
        
        return audio
    
    def _normalize_lufs(self, audio: np.ndarray) -> np.ndarray:
        """Normalize to target LUFS using pyloudnorm."""
        try:
            # Create loudness meter
            meter = pyln.Meter(self.sr)
            
            # Measure current loudness
            current_lufs = meter.integrated_loudness(audio)
            
            # Calculate gain adjustment
            gain_db = self.target_lufs - current_lufs
            gain_linear = 10 ** (gain_db / 20)
            
            # Apply gain
            normalized = audio * gain_linear
            
            # Ensure no clipping
            if np.max(np.abs(normalized)) > 0.99:
                normalized = normalized / np.max(np.abs(normalized)) * 0.99
            
            return normalized
            
        except Exception as e:
            print(f"LUFS normalization failed: {e}")
            return self._normalize_rms(audio)
    
    def _normalize_rms(self, audio: np.ndarray) -> np.ndarray:
        """Fallback RMS normalization."""
        # Target RMS level (roughly equivalent to -14 LUFS)
        target_rms = 0.1
        
        current_rms = np.sqrt(np.mean(audio**2))
        if current_rms > 0:
            gain = target_rms / current_rms
            audio = audio * gain
        
        return audio
    
    def _save_output(self, audio: np.ndarray) -> str:
        """Save final audio output."""
        with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as tmp_file:
            output_path = tmp_file.name
        
        # Save as 24-bit WAV for maximum quality
        sf.write(output_path, audio, self.sr, subtype='PCM_24')
        
        return output_path
    
    def create_project_json(self, plan: Dict[str, Any], mix_params: Dict[str, Any]) -> Dict[str, Any]:
        """Create project JSON for reproducible rendering."""
        return {
            "version": "1.0.0",
            "plan": plan,
            "mixParams": mix_params,
            "settings": {
                "sampleRate": self.sr,
                "targetLUFS": self.target_lufs,
                "headroomDB": self.headroom_db
            },
            "timestamp": "2024-01-01T00:00:00Z"  # In production, use actual timestamp
        }
