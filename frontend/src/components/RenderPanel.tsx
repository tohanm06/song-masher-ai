'use client'

import { useState, useEffect } from 'react'
import { Play, Download, Loader2, CheckCircle, AlertCircle, Music } from 'lucide-react'
import { useMashStore } from '@/state/useMashStore'

export function RenderPanel() {
  const { tracks, plan } = useMashStore()
  const [rendering, setRendering] = useState(false)
  const [renderJob, setRenderJob] = useState<any>(null)
  const [progress, setProgress] = useState(0)
  const [status, setStatus] = useState('idle')
  const [downloadUrls, setDownloadUrls] = useState<{mashup?: string, project?: string}>({})

  const startRender = async () => {
    if (!tracks[0]?.analysis || !tracks[1]?.analysis || !plan) return

    setRendering(true)
    setStatus('separating')

    try {
      // Step 1: Separate stems
      const stems = {}
      for (let i = 0; i < tracks.length; i++) {
        const formData = new FormData()
        formData.append('file', tracks[i].file)

        const response = await fetch('/api/separate', {
          method: 'POST',
          body: formData,
        })

        if (!response.ok) {
          throw new Error('Stem separation failed')
        }

        const separation = await response.json()
        Object.assign(stems, separation)
      }

      setProgress(25)
      setStatus('planning')

      // Step 2: Create render job
      const renderResponse = await fetch('/api/render', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          stems,
          plan,
          mixParams: {
            vocals_gain: 1.0,
            drums_gain: 0.8,
            bass_gain: 0.7,
            other_gain: 0.6,
            crossfade_length: 0.5,
            auto_eq: true,
            sidechain_ducking: true,
            de_esser: true
          }
        })
      })

      if (!renderResponse.ok) {
        throw new Error('Render job creation failed')
      }

      const { jobId } = await renderResponse.json()
      setRenderJob({ jobId })
      setProgress(50)
      setStatus('rendering')

      // Step 3: Poll for progress
      pollProgress(jobId)

    } catch (error) {
      console.error('Render failed:', error)
      setStatus('error')
      setRendering(false)
    }
  }

  const pollProgress = async (jobId: string) => {
    const pollInterval = setInterval(async () => {
      try {
        const response = await fetch(`/api/progress/${jobId}`)
        if (!response.ok) return

        const progressData = await response.json()
        setProgress(progressData.progress * 100)

        if (progressData.status === 'completed') {
          clearInterval(pollInterval)
          setStatus('completed')
          setRendering(false)
          
          // Get download URLs
          const downloadResponse = await fetch(`/api/download/${jobId}`)
          if (downloadResponse.ok) {
            const urls = await downloadResponse.json()
            setDownloadUrls(urls)
          }
        } else if (progressData.status === 'failed') {
          clearInterval(pollInterval)
          setStatus('error')
          setRendering(false)
        }
      } catch (error) {
        console.error('Progress polling failed:', error)
        clearInterval(pollInterval)
        setStatus('error')
        setRendering(false)
      }
    }, 1000)
  }

  const getStatusIcon = () => {
    switch (status) {
      case 'separating':
        return <Loader2 className="w-5 h-5 animate-spin text-blue-600" />
      case 'planning':
        return <Loader2 className="w-5 h-5 animate-spin text-yellow-600" />
      case 'rendering':
        return <Loader2 className="w-5 h-5 animate-spin text-green-600" />
      case 'completed':
        return <CheckCircle className="w-5 h-5 text-green-600" />
      case 'error':
        return <AlertCircle className="w-5 h-5 text-red-600" />
      default:
        return <Music className="w-5 h-5 text-gray-400" />
    }
  }

  const getStatusText = () => {
    switch (status) {
      case 'separating':
        return 'Separating stems...'
      case 'planning':
        return 'Creating mashup plan...'
      case 'rendering':
        return 'Rendering mashup...'
      case 'completed':
        return 'Mashup completed!'
      case 'error':
        return 'Render failed'
      default:
        return 'Ready to render'
    }
  }

  const canRender = tracks.length >= 2 && tracks[0]?.analysis && tracks[1]?.analysis && plan

  return (
    <div className="card">
      <div className="flex items-center space-x-3 mb-6">
        <Music className="w-6 h-6 text-primary-600" />
        <h2 className="text-xl font-semibold">Render Mashup</h2>
      </div>

      {/* Render Status */}
      <div className="mb-6">
        <div className="flex items-center space-x-3 mb-4">
          {getStatusIcon()}
          <span className="font-medium text-gray-900">{getStatusText()}</span>
        </div>

        {/* Progress Bar */}
        {(rendering || status === 'completed') && (
          <div className="w-full bg-gray-200 rounded-full h-2 mb-4">
            <div
              className="bg-primary-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progress}%` }}
            />
          </div>
        )}

        {/* Progress Text */}
        {rendering && (
          <div className="text-sm text-gray-600">
            {Math.round(progress)}% complete
          </div>
        )}
      </div>

      {/* Render Button */}
      {status === 'idle' && (
        <button
          onClick={startRender}
          disabled={!canRender}
          className={`
            w-full flex items-center justify-center space-x-2 px-6 py-3 rounded-lg font-medium transition-colors
            ${canRender
              ? 'bg-primary-600 text-white hover:bg-primary-700'
              : 'bg-gray-300 text-gray-500 cursor-not-allowed'
            }
          `}
        >
          <Play className="w-5 h-5" />
          <span>Start Render</span>
        </button>
      )}

      {/* Retry Button */}
      {status === 'error' && (
        <button
          onClick={startRender}
          className="w-full flex items-center justify-center space-x-2 px-6 py-3 bg-red-600 text-white rounded-lg font-medium hover:bg-red-700 transition-colors"
        >
          <AlertCircle className="w-5 h-5" />
          <span>Retry Render</span>
        </button>
      )}

      {/* Download Links */}
      {status === 'completed' && (downloadUrls.mashup_url || downloadUrls.project_url) && (
        <div className="space-y-4">
          <div className="border-t pt-4">
            <h3 className="text-lg font-medium mb-4">Download Results</h3>
            
            <div className="space-y-3">
              {downloadUrls.mashup_url && (
                <a
                  href={downloadUrls.mashup_url}
                  download
                  className="flex items-center space-x-3 p-4 bg-green-50 border border-green-200 rounded-lg hover:bg-green-100 transition-colors"
                >
                  <Download className="w-5 h-5 text-green-600" />
                  <div>
                    <p className="font-medium text-green-900">Final Mashup</p>
                    <p className="text-sm text-green-600">High-quality WAV file</p>
                  </div>
                </a>
              )}

              {downloadUrls.project_url && (
                <a
                  href={downloadUrls.project_url}
                  download
                  className="flex items-center space-x-3 p-4 bg-blue-50 border border-blue-200 rounded-lg hover:bg-blue-100 transition-colors"
                >
                  <Download className="w-5 h-5 text-blue-600" />
                  <div>
                    <p className="font-medium text-blue-900">Project File</p>
                    <p className="text-sm text-blue-600">JSON with all parameters</p>
                  </div>
                </a>
              )}
            </div>
          </div>
        </div>
      )}

      {/* Requirements Check */}
      {!canRender && (
        <div className="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div className="flex items-start space-x-3">
            <AlertCircle className="w-5 h-5 text-yellow-600 mt-0.5" />
            <div>
              <p className="font-medium text-yellow-900">Requirements not met</p>
              <ul className="text-sm text-yellow-700 mt-1 space-y-1">
                {tracks.length < 2 && <li>• Upload at least 2 audio files</li>}
                {tracks.length >= 2 && (!tracks[0]?.analysis || !tracks[1]?.analysis) && (
                  <li>• Complete audio analysis for both tracks</li>
                )}
                {tracks.length >= 2 && tracks[0]?.analysis && tracks[1]?.analysis && !plan && (
                  <li>• Create mashup plan</li>
                )}
              </ul>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
