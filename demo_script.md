# Song Masher AI - Demo Script (60 seconds)

## Quick Demo Flow

### 1. Upload Phase (10 seconds)
- **Action**: Drag and drop two audio files (2-6 minutes recommended)
- **Visual**: File drop zones with progress indicators
- **Result**: Files uploaded, analysis begins automatically

### 2. Analysis Phase (15 seconds)
- **Action**: Auto-analyze BPM, key, structure, loudness
- **Visual**: Real-time waveform display with beat markers
- **Result**: Display analysis cards with:
  - Duration, BPM, Key (Camelot notation)
  - Section breakdown (verse, chorus, bridge)
  - LUFS loudness level

### 3. Planning Phase (10 seconds)
- **Action**: Choose mashup strategy
- **Options**: 
  - "A vocals + B instrumental" (default)
  - "B vocals + A instrumental" 
  - "Hybrid drums"
- **Visual**: Strategy cards with descriptions
- **Result**: Auto-generated plan with key/tempo alignment

### 4. Timeline Phase (10 seconds)
- **Action**: Review and adjust mixing parameters
- **Visual**: Timeline with section markers, automation lanes
- **Controls**: Gain sliders, crossfade length, effect toggles
- **Result**: Final mix parameters confirmed

### 5. Rendering Phase (15 seconds)
- **Action**: Start render job
- **Visual**: Progress bar with status updates
- **Stages**: 
  - Stem separation (5s)
  - Audio transforms (5s) 
  - Mixing & mastering (5s)
- **Result**: High-quality WAV + project.json download

## Demo Talking Points

### Technical Highlights
- "GPU-accelerated stem separation using Demucs"
- "Beat-locked alignment with <40ms accuracy"
- "Professional mastering to -14 LUFS standard"
- "Deterministic re-rendering with project files"

### Quality Features
- "Automatic key matching with Camelot wheel"
- "Phrase-constrained DTW alignment"
- "Rubber Band HQ pitch/time stretching"
- "Sidechain ducking and auto-EQ"

### Performance Metrics
- "3-minute pair renders in ~15 seconds on GPU"
- "CPU fallback for accessibility"
- "Production-grade audio quality"

## Demo Assets

### Recommended Test Files
1. **Pop Song A**: 4/4 time, 120 BPM, C major
2. **Pop Song B**: 4/4 time, 140 BPM, G major
3. **Alternative**: Any two songs with clear structure

### Expected Results
- **Key Alignment**: Automatic C# major target
- **Tempo Sync**: 130 BPM target with 1.08x/0.93x stretches
- **Quality**: Professional mashup with proper mastering
- **Download**: WAV file + JSON project file

## Troubleshooting

### Common Issues
- **Upload fails**: Check file format (MP3, WAV, FLAC)
- **Analysis slow**: Normal for first run (model loading)
- **Render fails**: Check GPU memory or use CPU fallback
- **Quality issues**: Adjust mix parameters in timeline

### Fallback Options
- **Simple Mode**: `SIMPLE_MODE=true python -m backend.gradio_app`
- **CPU Only**: Set `DEMUCS_DEVICE=cpu` in environment
- **Local Storage**: Set `STORAGE_KIND=local` for development

## Success Metrics

### Technical Validation
- ✅ Beat alignment <40ms median error
- ✅ LUFS level -14 ±0.5 dB
- ✅ No clipping, ≥1dB headroom
- ✅ Key compatibility auto-selected
- ✅ Deterministic re-render capability

### User Experience
- ✅ Intuitive drag-and-drop interface
- ✅ Real-time analysis feedback
- ✅ Professional timeline controls
- ✅ Clear progress indicators
- ✅ High-quality output

## Post-Demo Q&A

### Common Questions
**Q: How does it compare to manual DJ software?**
A: AI-powered analysis and alignment, but with professional mastering and deterministic re-rendering.

**Q: Can it handle any genre?**
A: Optimized for pop/electronic, but works with any structured music.

**Q: What about copyright?**
A: Processes user uploads only, no bundled content.

**Q: How accurate is the key detection?**
A: Uses Krumhansl-Schmuckler algorithm with Camelot wheel mapping.

**Q: Can I export stems separately?**
A: Yes, stem separation is available as a separate endpoint.

### Technical Deep-Dive
- **Architecture**: Microservices with Docker Compose
- **ML Models**: Demucs for separation, librosa for analysis
- **Audio Processing**: Rubber Band for transforms, pyloudnorm for mastering
- **Storage**: S3/MinIO with presigned URLs
- **Queue**: Celery/RQ for background processing
