'use client'

import { useState, useEffect } from 'react'
import { Play, Pause, Volume2, VolumeX, Settings } from 'lucide-react'
import { useMashStore } from '@/state/useMashStore'

export function Timeline() {
  const { tracks, plan } = useMashStore()
  const [isPlaying, setIsPlaying] = useState(false)
  const [currentTime, setCurrentTime] = useState(0)
  const [mixParams, setMixParams] = useState({
    vocals_gain: 1.0,
    drums_gain: 0.8,
    bass_gain: 0.7,
    other_gain: 0.6,
    crossfade_length: 0.5,
    auto_eq: true,
    sidechain_ducking: true,
    de_esser: true
  })

  const maxDuration = Math.max(
    tracks[0]?.analysis?.duration || 0,
    tracks[1]?.analysis?.duration || 0
  )

  const formatTime = (seconds: number) => {
    const mins = Math.floor(seconds / 60)
    const secs = Math.floor(seconds % 60)
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  const handleGainChange = (stem: string, value: number) => {
    setMixParams(prev => ({
      ...prev,
      [`${stem}_gain`]: value
    }))
  }

  const handleCrossfadeChange = (value: number) => {
    setMixParams(prev => ({
      ...prev,
      crossfade_length: value
    }))
  }

  const toggleEffect = (effect: string) => {
    setMixParams(prev => ({
      ...prev,
      [effect]: !prev[effect as keyof typeof prev]
    }))
  }

  return (
    <div className="card">
      <div className="flex items-center space-x-3 mb-6">
        <Settings className="w-6 h-6 text-primary-600" />
        <h2 className="text-xl font-semibold">Timeline & Mixing</h2>
      </div>

      {/* Playback Controls */}
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center space-x-4">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
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
            {formatTime(currentTime)} / {formatTime(maxDuration)}
          </div>
        </div>

        <div className="flex items-center space-x-2">
          <button className="p-2 text-gray-400 hover:text-gray-600">
            <Volume2 className="w-4 h-4" />
          </button>
          <button className="p-2 text-gray-400 hover:text-gray-600">
            <VolumeX className="w-4 h-4" />
          </button>
        </div>
      </div>

      {/* Timeline Visualization */}
      <div className="mb-6">
        <div className="relative h-32 bg-gray-100 rounded-lg overflow-hidden">
          {/* Track A */}
          <div className="absolute top-0 left-0 w-full h-16 bg-blue-100 border-b border-blue-200">
            <div className="p-2">
              <div className="text-xs font-medium text-blue-800">Track A</div>
              <div className="text-xs text-blue-600">
                {tracks[0]?.analysis?.key} | {Math.round(tracks[0]?.analysis?.bpm || 0)} BPM
              </div>
            </div>
          </div>

          {/* Track B */}
          <div className="absolute top-16 left-0 w-full h-16 bg-green-100 border-b border-green-200">
            <div className="p-2">
              <div className="text-xs font-medium text-green-800">Track B</div>
              <div className="text-xs text-green-600">
                {tracks[1]?.analysis?.key} | {Math.round(tracks[1]?.analysis?.bpm || 0)} BPM
              </div>
            </div>
          </div>

          {/* Section Markers */}
          {plan?.sectionPairs && (
            <div className="absolute top-0 left-0 w-full h-full">
              {plan.sectionPairs.map((pair: any, index: number) => {
                const startPercent = (pair.sectionA.start / maxDuration) * 100
                const widthPercent = ((pair.sectionA.end - pair.sectionA.start) / maxDuration) * 100
                
                return (
                  <div
                    key={index}
                    className="absolute top-0 h-full border-l-2 border-r-2 border-primary-500 opacity-60"
                    style={{
                      left: `${startPercent}%`,
                      width: `${widthPercent}%`
                    }}
                  />
                )
              })}
            </div>
          )}

          {/* Playhead */}
          <div
            className="absolute top-0 w-0.5 h-full bg-red-500 z-10"
            style={{ left: `${(currentTime / maxDuration) * 100}%` }}
          />
        </div>
      </div>

      {/* Mixing Controls */}
      <div className="space-y-6">
        <h3 className="text-lg font-medium">Mixing Parameters</h3>

        {/* Gain Controls */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Vocals Gain
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={mixParams.vocals_gain}
              onChange={(e) => handleGainChange('vocals', parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-gray-500 mt-1">
              {mixParams.vocals_gain.toFixed(1)}x
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Drums Gain
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={mixParams.drums_gain}
              onChange={(e) => handleGainChange('drums', parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-gray-500 mt-1">
              {mixParams.drums_gain.toFixed(1)}x
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Bass Gain
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={mixParams.bass_gain}
              onChange={(e) => handleGainChange('bass', parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-gray-500 mt-1">
              {mixParams.bass_gain.toFixed(1)}x
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Other Gain
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={mixParams.other_gain}
              onChange={(e) => handleGainChange('other', parseFloat(e.target.value))}
              className="w-full"
            />
            <div className="text-xs text-gray-500 mt-1">
              {mixParams.other_gain.toFixed(1)}x
            </div>
          </div>
        </div>

        {/* Crossfade Length */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Crossfade Length: {mixParams.crossfade_length}s
          </label>
          <input
            type="range"
            min="0"
            max="2"
            step="0.1"
            value={mixParams.crossfade_length}
            onChange={(e) => handleCrossfadeChange(parseFloat(e.target.value))}
            className="w-full"
          />
        </div>

        {/* Effect Toggles */}
        <div className="grid grid-cols-3 gap-4">
          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={mixParams.auto_eq}
              onChange={() => toggleEffect('auto_eq')}
              className="rounded"
            />
            <span className="text-sm font-medium text-gray-700">Auto EQ</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={mixParams.sidechain_ducking}
              onChange={() => toggleEffect('sidechain_ducking')}
              className="rounded"
            />
            <span className="text-sm font-medium text-gray-700">Sidechain</span>
          </label>

          <label className="flex items-center space-x-2">
            <input
              type="checkbox"
              checked={mixParams.de_esser}
              onChange={() => toggleEffect('de_esser')}
              className="rounded"
            />
            <span className="text-sm font-medium text-gray-700">De-esser</span>
          </label>
        </div>
      </div>
    </div>
  )
}
