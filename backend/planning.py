"""
Mashup Planning Module
Key/tempo alignment and phrase-constrained DTW for optimal mashup strategies.
"""

import numpy as np
from typing import Dict, List, Any, Tuple
from scipy.spatial.distance import cdist
from scipy.optimize import linear_sum_assignment

class MashupPlanner:
    """Advanced mashup planning with key/tempo alignment and phrase matching."""
    
    def __init__(self):
        # Key compatibility matrix (Camelot wheel)
        self.key_compatibility = self._build_key_compatibility()
        
        # Recipe templates
        self.recipes = {
            "AoverB": {
                "description": "A vocals over B instrumental",
                "stems": {"A": "vocals", "B": "drums+bass+other"},
                "priority": "key_match"
            },
            "BoverA": {
                "description": "B vocals over A instrumental", 
                "stems": {"B": "vocals", "A": "drums+bass+other"},
                "priority": "key_match"
            },
            "HybridDrums": {
                "description": "A vocals + B drums + mixed bass/other",
                "stems": {"A": "vocals", "B": "drums", "mixed": "bass+other"},
                "priority": "tempo_match"
            }
        }
    
    def create_plan(self, trackA: Dict[str, Any], trackB: Dict[str, Any], recipe: str) -> Dict[str, Any]:
        """Create comprehensive mashup plan with alignment strategy."""
        if recipe not in self.recipes:
            raise ValueError(f"Unknown recipe: {recipe}")
        
        # Analyze compatibility
        compatibility = self._analyze_compatibility(trackA, trackB)
        
        # Choose target key
        target_key, key_shift_a, key_shift_b = self._choose_target_key(
            trackA["key"], trackB["key"], recipe
        )
        
        # Calculate tempo alignment
        stretch_map = self._calculate_tempo_alignment(
            trackA["bpm"], trackB["bpm"], trackA["beats"], trackB["beats"]
        )
        
        # Section pairing with DTW
        section_pairs = self._pair_sections(
            trackA["sections"], trackB["sections"], 
            trackA["beats"], trackB["beats"]
        )
        
        # Quality assessment
        quality_hints = self._assess_quality(
            compatibility, stretch_map, section_pairs
        )
        
        return {
            "targetKey": target_key,
            "keyShiftA": key_shift_a,
            "keyShiftB": key_shift_b,
            "stretchMap": stretch_map,
            "sectionPairs": section_pairs,
            "qualityHints": quality_hints,
            "recipe": recipe,
            "compatibility": compatibility
        }
    
    def _build_key_compatibility(self) -> Dict[str, Dict[str, int]]:
        """Build Camelot wheel compatibility matrix."""
        # Camelot wheel positions
        camelot_keys = {
            "1A": 0, "2A": 1, "3A": 2, "4A": 3, "5A": 4, "6A": 5,
            "7A": 6, "8A": 7, "9A": 8, "10A": 9, "11A": 10, "12A": 11,
            "1B": 12, "2B": 13, "3B": 14, "4B": 15, "5B": 16, "6B": 17,
            "7B": 18, "8B": 19, "9B": 20, "10B": 21, "11B": 22, "12B": 23
        }
        
        compatibility = {}
        for key, pos in camelot_keys.items():
            compatibility[key] = {}
            for other_key, other_pos in camelot_keys.items():
                # Calculate distance on wheel
                distance = min(abs(pos - other_pos), 24 - abs(pos - other_pos))
                
                # Compatibility score (0 = perfect, 12 = opposite)
                if distance == 0:
                    score = 0  # Same key
                elif distance == 1:
                    score = 1  # Adjacent (perfect)
                elif distance == 2:
                    score = 2  # Very good
                elif distance <= 4:
                    score = 3  # Good
                elif distance <= 6:
                    score = 4  # Acceptable
                else:
                    score = 5  # Poor
                
                compatibility[key][other_key] = score
        
        return compatibility
    
    def _analyze_compatibility(self, trackA: Dict[str, Any], trackB: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze overall track compatibility."""
        # Key compatibility
        key_score = self.key_compatibility.get(trackA["camelot"], {}).get(trackB["camelot"], 5)
        
        # Tempo compatibility
        tempo_ratio = trackA["bpm"] / trackB["bpm"]
        if 0.8 <= tempo_ratio <= 1.25:
            tempo_score = 0  # Excellent
        elif 0.7 <= tempo_ratio <= 1.4:
            tempo_score = 1  # Good
        elif 0.6 <= tempo_ratio <= 1.6:
            tempo_score = 2  # Acceptable
        else:
            tempo_score = 3  # Poor
        
        # Structure compatibility
        structure_score = self._assess_structure_compatibility(
            trackA["sections"], trackB["sections"]
        )
        
        return {
            "keyScore": key_score,
            "tempoScore": tempo_score,
            "structureScore": structure_score,
            "overallScore": (key_score + tempo_score + structure_score) / 3
        }
    
    def _assess_structure_compatibility(self, sectionsA: List[Dict], sectionsB: List[Dict]) -> int:
        """Assess how well track structures match."""
        # Count section types
        typesA = [s["label"] for s in sectionsA]
        typesB = [s["label"] for s in sectionsB]
        
        # Calculate similarity
        from collections import Counter
        countA = Counter(typesA)
        countB = Counter(typesB)
        
        # Jaccard similarity
        all_types = set(typesA + typesB)
        intersection = sum(min(countA[t], countB[t]) for t in all_types)
        union = sum(max(countA[t], countB[t]) for t in all_types)
        
        if union == 0:
            return 0
        
        similarity = intersection / union
        
        if similarity >= 0.8:
            return 0  # Excellent
        elif similarity >= 0.6:
            return 1  # Good
        elif similarity >= 0.4:
            return 2  # Acceptable
        else:
            return 3  # Poor
    
    def _choose_target_key(self, keyA: str, keyB: str, recipe: str) -> Tuple[str, int, int]:
        """Choose optimal target key and calculate shifts."""
        # Parse keys (assume format like "Cm" or "C#m")
        camelotA = self._key_to_camelot(keyA)
        camelotB = self._key_to_camelot(keyB)
        
        # Find best compromise key
        best_key = None
        best_score = float('inf')
        
        for target in self.key_compatibility.keys():
            scoreA = self.key_compatibility[target].get(camelotA, 5)
            scoreB = self.key_compatibility[target].get(camelotB, 5)
            total_score = scoreA + scoreB
            
            if total_score < best_score:
                best_score = total_score
                best_key = target
        
        # Calculate shifts
        shiftA = self._calculate_key_shift(camelotA, best_key)
        shiftB = self._calculate_key_shift(camelotB, best_key)
        
        return best_key, shiftA, shiftB
    
    def _key_to_camelot(self, key: str) -> str:
        """Convert key string to Camelot notation."""
        # This is a simplified mapping - in production, use proper music theory
        key_map = {
            "C": "8B", "C#": "3B", "D": "10B", "D#": "5B", "E": "12B", "F": "7B",
            "F#": "2B", "G": "9B", "G#": "4B", "A": "11B", "A#": "6B", "B": "1B",
            "Cm": "5A", "C#m": "12A", "Dm": "7A", "D#m": "2A", "Em": "9A", "Fm": "4A",
            "F#m": "11A", "Gm": "6A", "G#m": "1A", "Am": "8A", "A#m": "3A", "Bm": "10A"
        }
        return key_map.get(key, "8B")  # Default to C major
    
    def _calculate_key_shift(self, from_key: str, to_key: str) -> int:
        """Calculate semitone shift between keys."""
        # Simplified calculation - in production, use proper music theory
        camelot_positions = {
            "1A": 0, "2A": 1, "3A": 2, "4A": 3, "5A": 4, "6A": 5,
            "7A": 6, "8A": 7, "9A": 8, "10A": 9, "11A": 10, "12A": 11,
            "1B": 12, "2B": 13, "3B": 14, "4B": 15, "5B": 16, "6B": 17,
            "7B": 18, "8B": 19, "9B": 20, "10B": 21, "11B": 22, "12B": 23
        }
        
        from_pos = camelot_positions.get(from_key, 0)
        to_pos = camelot_positions.get(to_key, 0)
        
        # Calculate shift (simplified)
        shift = (to_pos - from_pos) % 12
        if shift > 6:
            shift -= 12
        
        return shift
    
    def _calculate_tempo_alignment(self, bpmA: float, bpmB: float, 
                                 beatsA: List[float], beatsB: List[float]) -> Dict[str, float]:
        """Calculate tempo alignment and stretch ratios."""
        # Choose target tempo (usually the more common one)
        target_bpm = bpmA if bpmA > bpmB else bpmB
        
        # Calculate stretch ratios
        stretchA = target_bpm / bpmA
        stretchB = target_bpm / bpmB
        
        # Limit extreme stretches
        stretchA = max(0.5, min(2.0, stretchA))
        stretchB = max(0.5, min(2.0, stretchB))
        
        return {
            "targetBpm": target_bpm,
            "stretchA": stretchA,
            "stretchB": stretchB,
            "quality": "high" if max(stretchA, stretchB) < 1.5 else "medium"
        }
    
    def _pair_sections(self, sectionsA: List[Dict], sectionsB: List[Dict],
                      beatsA: List[float], beatsB: List[float]) -> List[Dict[str, Any]]:
        """Pair sections using phrase-constrained DTW."""
        # Create feature vectors for each section
        featuresA = self._extract_section_features(sectionsA, beatsA)
        featuresB = self._extract_section_features(sectionsB, beatsB)
        
        # DTW alignment
        alignment = self._dtw_align(featuresA, featuresB)
        
        # Create section pairs
        pairs = []
        for i, (a_idx, b_idx) in enumerate(alignment):
            if a_idx < len(sectionsA) and b_idx < len(sectionsB):
                pairs.append({
                    "sectionA": sectionsA[a_idx],
                    "sectionB": sectionsB[b_idx],
                    "alignment": i,
                    "confidence": 0.8  # Simplified
                })
        
        return pairs
    
    def _extract_section_features(self, sections: List[Dict], beats: List[float]) -> np.ndarray:
        """Extract features for DTW alignment."""
        features = []
        for section in sections:
            # Simple features: duration, type, position
            duration = section["end"] - section["start"]
            section_type = {"verse": 0, "chorus": 1, "bridge": 2}.get(section["label"], 0)
            position = section["start"] / max(beats) if beats else 0
            
            features.append([duration, section_type, position])
        
        return np.array(features)
    
    def _dtw_align(self, featuresA: np.ndarray, featuresB: np.ndarray) -> List[Tuple[int, int]]:
        """Dynamic Time Warping alignment."""
        # Calculate distance matrix
        distances = cdist(featuresA, featuresB, metric='euclidean')
        
        # DTW algorithm (simplified)
        m, n = distances.shape
        dtw = np.zeros((m + 1, n + 1))
        dtw[0, 0] = 0
        dtw[1:, 0] = np.inf
        dtw[0, 1:] = np.inf
        
        # Fill DTW matrix
        for i in range(1, m + 1):
            for j in range(1, n + 1):
                dtw[i, j] = distances[i-1, j-1] + min(
                    dtw[i-1, j],      # insertion
                    dtw[i, j-1],      # deletion
                    dtw[i-1, j-1]     # match
                )
        
        # Backtrack to find alignment
        alignment = []
        i, j = m, n
        while i > 0 and j > 0:
            alignment.append((i-1, j-1))
            if dtw[i-1, j] <= dtw[i, j-1] and dtw[i-1, j] <= dtw[i-1, j-1]:
                i -= 1
            elif dtw[i, j-1] <= dtw[i-1, j-1]:
                j -= 1
            else:
                i -= 1
                j -= 1
        
        return list(reversed(alignment))
    
    def _assess_quality(self, compatibility: Dict, stretch_map: Dict, 
                       section_pairs: List[Dict]) -> List[str]:
        """Assess mashup quality and provide hints."""
        hints = []
        
        # Key compatibility
        if compatibility["keyScore"] <= 1:
            hints.append("Excellent key compatibility")
        elif compatibility["keyScore"] <= 2:
            hints.append("Good key compatibility")
        else:
            hints.append("Consider key adjustment for better harmony")
        
        # Tempo compatibility
        if compatibility["tempoScore"] <= 1:
            hints.append("Tempo alignment looks good")
        else:
            hints.append("Significant tempo adjustment needed")
        
        # Stretch quality
        if stretch_map["quality"] == "high":
            hints.append("Minimal tempo stretching required")
        else:
            hints.append("Moderate tempo stretching - check audio quality")
        
        # Structure alignment
        if len(section_pairs) >= 3:
            hints.append("Good structural alignment found")
        else:
            hints.append("Limited structural overlap - consider manual alignment")
        
        return hints
