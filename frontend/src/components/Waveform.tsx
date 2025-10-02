'use client'

import { useEffect, useRef, useState } from 'react'
import WaveSurfer from 'wavesurfer.js'
import { Play, Pause } from 'lucide-react'

interface WaveformProps {
  audioUrl: string
  duration: number
  beats?: number[]
  downbeats?: number[]
  sections?: Array<{ start: number; end: number; label: string }>
  className?: string
}

export function Waveform({ 
  audioUrl, 
  duration, 
  beats = [], 
  downbeats = [], 
  sections = [],
  className = '' 
}: WaveformProps) {
  const waveformRef = useRef<HTMLDivElement>(null)
  const wavesurferRef = useRef<WaveSurfer | null>(null)
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)

  useEffect(() => {
    if (!waveformRef.current) return

    // Initialize WaveSurfer
    const wavesurfer = WaveSurfer.create({
      container: waveformRef.current,
      waveColor: '#e5e7eb',
      progressColor: '#3b82f6',
      cursorColor: '#1d4ed8',
      barWidth: 2,
      barRadius: 1,
      responsive: true,
      height: 80,
      normalize: true,
    })

    wavesurferRef.current = wavesurfer

    // Load audio
    wavesurfer.load(audioUrl)

    // Event listeners
    wavesurfer.on('play', () => setIsPlaying(true))
    wavesurfer.on('pause', () => setIsPlaying(false))
    wavesurfer.on('timeupdate', () => setCurrentTime(wavesurfer.getCurrentTime()))

    return () => {
      wavesurfer.destroy()
    }
  }, [audioUrl])

  const togglePlay = () => {
    if (wavesurferRef.current) {
      wavesurferRef.current.playPause()
    }
  }

  const seekTo = (time: number) => {
    if (wavesurferRef.current) {
      wavesurferRef.current.seekTo(time / duration)
    }
  }

  return (
    <div className={`space-y-3 ${className}`}>
      {/* Waveform */}
      <div className="relative">
        <div ref={waveformRef} className="w-full" />
        
        {/* Beat markers */}
        {beats.length > 0 && (
          <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
            {beats.map((beat, index) => (
              <div
                key={index}
                className="absolute top-0 w-0.5 h-full bg-blue-400 opacity-60"
                style={{ left: `${(beat / duration) * 100}%` }}
              />
            ))}
          </div>
        )}
        
        {/* Downbeat markers */}
        {downbeats.length > 0 && (
          <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
            {downbeats.map((downbeat, index) => (
              <div
                key={index}
                className="absolute top-0 w-0.5 h-full bg-red-500"
                style={{ left: `${(downbeat / duration) * 100}%` }}
              />
            ))}
          </div>
        )}
        
        {/* Section markers */}
        {sections.length > 0 && (
          <div className="absolute top-0 left-0 w-full h-full pointer-events-none">
            {sections.map((section, index) => {
              const startPercent = (section.start / duration) * 100
              const widthPercent = ((section.end - section.start) / duration) * 100
              
              return (
                <div
                  key={index}
                  className="absolute top-0 h-full opacity-20 pointer-events-none"
                  style={{ 
                    left: `${startPercent}%`, 
                    width: `${widthPercent}%`,
                    backgroundColor: getSectionColor(section.label)
                  }}
                />
              )
            })}
          </div>
        )}
      </div>

      {/* Controls */}
      <div className="flex items-center justify-between">
        <button
          onClick={togglePlay}
          className="flex items-center space-x-2 px-4 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 transition-colors"
        >
          {isPlaying ? (
            <Pause className="w-4 h-4" />
          ) : (
            <Play className="w-4 h-4" />
          )}
          <span className="text-sm font-medium">
            {isPlaying ? 'Pause' : 'Play'}
          </span>
        </button>

        <div className="text-sm text-gray-600">
          {formatTime(currentTime)} / {formatTime(duration)}
        </div>
      </div>

      {/* Section labels */}
      {sections.length > 0 && (
        <div className="flex space-x-1 text-xs">
          {sections.map((section, index) => {
            const startPercent = (section.start / duration) * 100
            const widthPercent = ((section.end - section.start) / duration) * 100
            
            return (
              <div
                key={index}
                className="text-center"
                style={{ 
                  width: `${widthPercent}%`,
                  marginLeft: index === 0 ? `${startPercent}%` : '0'
                }}
              >
                <div 
                  className="px-2 py-1 rounded text-white text-xs font-medium"
                  style={{ backgroundColor: getSectionColor(section.label) }}
                >
                  {section.label}
                </div>
              </div>
            )
          })}
        </div>
      )}
    </div>
  )
}

function getSectionColor(label: string): string {
  const colors: Record<string, string> = {
    'verse': '#3b82f6',
    'chorus': '#ef4444',
    'bridge': '#10b981',
    'intro': '#8b5cf6',
    'outro': '#f59e0b',
  }
  return colors[label.toLowerCase()] || '#6b7280'
}

function formatTime(seconds: number): string {
  const mins = Math.floor(seconds / 60)
  const secs = Math.floor(seconds % 60)
  return `${mins}:${secs.toString().padStart(2, '0')}`
}
