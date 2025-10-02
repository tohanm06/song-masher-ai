'use client'

import { useCallback, useState } from 'react'
import { Upload, Music, X } from 'lucide-react'
import { useMashStore } from '@/state/useMashStore'

export function FileDrop() {
  const { addTrack, tracks } = useMashStore()
  const [isDragOver, setIsDragOver] = useState(false)
  const [uploading, setUploading] = useState(false)

  const handleDrop = useCallback(async (files: FileList) => {
    setUploading(true)
    
    try {
      for (const file of Array.from(files)) {
        if (file.type.startsWith('audio/')) {
          await addTrack(file)
        }
      }
    } catch (error) {
      console.error('Upload failed:', error)
    } finally {
      setUploading(false)
    }
  }, [addTrack])

  const handleDragOver = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(true)
  }, [])

  const handleDragLeave = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
  }, [])

  const handleDropEvent = useCallback((e: React.DragEvent) => {
    e.preventDefault()
    setIsDragOver(false)
    
    if (e.dataTransfer.files) {
      handleDrop(e.dataTransfer.files)
    }
  }, [handleDrop])

  const handleFileInput = useCallback((e: React.ChangeEvent<HTMLInputElement>) => {
    if (e.target.files) {
      handleDrop(e.target.files)
    }
  }, [handleDrop])

  return (
    <div className="card">
      <h2 className="text-xl font-semibold mb-4">Upload Audio Files</h2>
      
      <div
        className={`
          relative border-2 border-dashed rounded-lg p-8 text-center transition-colors
          ${isDragOver 
            ? 'border-primary-500 bg-primary-50' 
            : 'border-gray-300 hover:border-primary-400'
          }
        `}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDropEvent}
      >
        <input
          type="file"
          multiple
          accept="audio/*"
          onChange={handleFileInput}
          className="absolute inset-0 w-full h-full opacity-0 cursor-pointer"
        />
        
        <div className="space-y-4">
          <div className="mx-auto w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center">
            <Music className="w-8 h-8 text-primary-600" />
          </div>
          
          <div>
            <p className="text-lg font-medium text-gray-900">
              {isDragOver ? 'Drop files here' : 'Drag & drop audio files'}
            </p>
            <p className="text-sm text-gray-500 mt-1">
              or click to browse (MP3, WAV, FLAC, etc.)
            </p>
          </div>
          
          {uploading && (
            <div className="flex items-center justify-center space-x-2 text-primary-600">
              <div className="animate-spin rounded-full h-4 w-4 border-2 border-primary-600 border-t-transparent" />
              <span className="text-sm">Uploading...</span>
            </div>
          )}
        </div>
      </div>

      {/* Uploaded Files */}
      {tracks.length > 0 && (
        <div className="mt-6">
          <h3 className="text-sm font-medium text-gray-700 mb-3">
            Uploaded Files ({tracks.length}/2)
          </h3>
          <div className="space-y-2">
            {tracks.map((track, index) => (
              <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                <div className="flex items-center space-x-3">
                  <Music className="w-4 h-4 text-gray-500" />
                  <div>
                    <p className="text-sm font-medium text-gray-900">
                      {track.file.name}
                    </p>
                    <p className="text-xs text-gray-500">
                      {formatFileSize(track.file.size)}
                    </p>
                  </div>
                </div>
                <button
                  onClick={() => removeTrack(index)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <X className="w-4 h-4" />
                </button>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

function formatFileSize(bytes: number): string {
  if (bytes === 0) return '0 Bytes'
  
  const k = 1024
  const sizes = ['Bytes', 'KB', 'MB', 'GB']
  const i = Math.floor(Math.log(bytes) / Math.log(k))
  
  return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i]
}
