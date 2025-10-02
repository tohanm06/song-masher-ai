/**
 * Utility functions for formatting data
 */

export function formatDuration(seconds: number): string {
  if (seconds < 0) return '0:00'
  
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}

export function formatBPM(bpm: number): string {
  return Math.round(bpm).toString()
}

export function formatLUFS(lufs: number): string {
  return lufs.toFixed(1) + ' dB'
}

export function formatKey(key: string, camelot: string): string {
  return `${key} (${camelot})`
}

export function formatConfidence(confidence: number): string {
  return Math.round(confidence * 100) + '%'
}

export function formatStretchRatio(ratio: number): string {
  return ratio.toFixed(2) + 'x'
}

export function formatGain(gain: number): string {
  return gain.toFixed(1) + 'x'
}

export function formatProgress(progress: number): string {
  return Math.round(progress * 100) + '%'
}

export function formatTime(seconds: number): string {
  if (seconds < 0) return '0:00'
  
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}

export function formatPercentage(value: number, decimals: number = 1): string {
  return (value * 100).toFixed(decimals) + '%'
}

export function formatDecibels(db: number): string {
  return db.toFixed(1) + ' dB'
}

export function formatFrequency(hz: number): string {
  if (hz >= 1000) {
    return (hz / 1000).toFixed(1) + ' kHz'
  }
  return hz.toFixed(0) + ' Hz'
}

export function formatBitrate(kbps: number): string {
  return kbps.toFixed(0) + ' kbps'
}

export function formatSampleRate(hz: number): string {
  if (hz >= 1000) {
    return (hz / 1000).toFixed(1) + ' kHz'
  }
  return hz.toFixed(0) + ' Hz'
}
