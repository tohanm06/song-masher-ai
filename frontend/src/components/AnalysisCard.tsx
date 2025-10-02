'use client'

import { useState, useEffect } from 'react'
import { Music, Clock, Zap, Key, Volume2, Loader2 } from 'lucide-react'
import { Waveform } from './Waveform'
import { useMashStore } from '@/state/useMashStore'

interface AnalysisCardProps {
  track: {
    file: File
    analysis?: {
      duration: number
      bpm: number
      beats: number[]
      downbeats: number[]
      key: string
      camelot: string
      sections: Array<{ start: number; end: number; label: string }>
      lufs: number
    }
  }
  index: number
}

export function AnalysisCard({ track, index }: AnalysisCardProps) {
  const { updateTrackAnalysis } = useMashStore()
  const [analyzing, setAnalyzing] = useState(false)
  const [audioUrl, setAudioUrl] = useState<string>('')

  useEffect(() => {
    // Create object URL for audio
    const url = URL.createObjectURL(track.file)
    setAudioUrl(url)

    // Auto-analyze if not already analyzed
    if (!track.analysis) {
      analyzeTrack()
    }

    return () => {
      URL.revokeObjectURL(url)
    }
  }, [track.file])

  const analyzeTrack = async () => {
    setAnalyzing(true)
    
    try {
      const formData = new FormData()
      formData.append('file', track.file)

      const response = await fetch('/api/analyze', {
        method: 'POST',
        body: formData,
      })

      if (!response.ok) {
        throw new Error('Analysis failed')
      }

      const analysis = await response.json()
      updateTrackAnalysis(index, analysis)
    } catch (error) {
      console.error('Analysis failed:', error)
    } finally {
      setAnalyzing(false)
    }
  }

  const formatDuration = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const formatBPM = (bpm: number) => {
    return Math.round(bpm)
  }

  const formatLUFS = (lufs: number) => {
    return lufs.toFixed(1)
  }

  return (
    <div className="card">
      <div className="flex items-center justify-between mb-4">
        <div className="flex items-center space-x-3">
          <div className="w-10 h-10 bg-primary-100 rounded-lg flex items-center justify-center">
            <Music className="w-5 h-5 text-primary-600" />
          </div>
          <div>
            <h3 className="font-semibold text-gray-900">
              Track {index + 1}
            </h3>
            <p className="text-sm text-gray-500">
              {track.file.name}
            </p>
          </div>
        </div>
        
        {analyzing && (
          <div className="flex items-center space-x-2 text-primary-600">
            <Loader2 className="w-4 h-4 animate-spin" />
            <span className="text-sm">Analyzing...</span>
          </div>
        )}
      </div>

      {/* Audio Waveform */}
      {audioUrl && (
        <div className="mb-6">
          <Waveform
            audioUrl={audioUrl}
            duration={track.analysis?.duration || 0}
            beats={track.analysis?.beats || []}
            downbeats={track.analysis?.downbeats || []}
            sections={track.analysis?.sections || []}
          />
        </div>
      )}

      {/* Analysis Results */}
      {track.analysis ? (
        <div className="grid grid-cols-2 gap-4">
          <div className="flex items-center space-x-3">
            <Clock className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">Duration</p>
              <p className="text-sm text-gray-600">
                {formatDuration(track.analysis.duration)}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Zap className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">BPM</p>
              <p className="text-sm text-gray-600">
                {formatBPM(track.analysis.bpm)}
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Key className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">Key</p>
              <p className="text-sm text-gray-600">
                {track.analysis.key} ({track.analysis.camelot})
              </p>
            </div>
          </div>

          <div className="flex items-center space-x-3">
            <Volume2 className="w-5 h-5 text-gray-400" />
            <div>
              <p className="text-sm font-medium text-gray-900">LUFS</p>
              <p className="text-sm text-gray-600">
                {formatLUFS(track.analysis.lufs)} dB
              </p>
            </div>
          </div>
        </div>
      ) : (
        <div className="text-center py-8">
          <p className="text-gray-500">
            {analyzing ? 'Analyzing audio...' : 'Click to analyze'}
          </p>
        </div>
      )}

      {/* Sections */}
      {track.analysis?.sections && track.analysis.sections.length > 0 && (
        <div className="mt-4">
          <h4 className="text-sm font-medium text-gray-900 mb-2">Sections</h4>
          <div className="flex flex-wrap gap-2">
            {track.analysis.sections.map((section, sectionIndex) => (
              <div
                key={sectionIndex}
                className="px-3 py-1 bg-gray-100 rounded-full text-xs font-medium text-gray-700"
              >
                {section.label} ({formatDuration(section.start)} - {formatDuration(section.end)})
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
