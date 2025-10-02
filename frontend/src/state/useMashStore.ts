'use client'

import { create } from 'zustand'
import { persist } from 'zustand/middleware'

interface Track {
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

interface MashupPlan {
  targetKey: string
  keyShiftA: number
  keyShiftB: number
  stretchMap: {
    targetBpm: number
    stretchA: number
    stretchB: number
    quality: string
  }
  sectionPairs: Array<{
    sectionA: { start: number; end: number; label: string }
    sectionB: { start: number; end: number; label: string }
    alignment: number
    confidence: number
  }>
  qualityHints: string[]
  recipe: string
  compatibility: {
    keyScore: number
    tempoScore: number
    structureScore: number
    overallScore: number
  }
}

interface MashStore {
  // State
  tracks: Track[]
  plan: MashupPlan | null
  currentStep: 'upload' | 'analyze' | 'plan' | 'render'
  
  // Actions
  addTrack: (file: File) => Promise<void>
  removeTrack: (index: number) => void
  updateTrackAnalysis: (index: number, analysis: Track['analysis']) => void
  setPlan: (plan: MashupPlan) => void
  setCurrentStep: (step: 'upload' | 'analyze' | 'plan' | 'render') => void
  reset: () => void
}

export const useMashStore = create<MashStore>()(
  persist(
    (set, get) => ({
      // Initial state
      tracks: [],
      plan: null,
      currentStep: 'upload',

      // Add track
      addTrack: async (file: File) => {
        const tracks = get().tracks
        
        if (tracks.length >= 2) {
          throw new Error('Maximum 2 tracks allowed')
        }

        const newTrack: Track = { file }
        set({ tracks: [...tracks, newTrack] })
        
        // Auto-advance to analyze step if we have 2 tracks
        if (tracks.length + 1 === 2) {
          set({ currentStep: 'analyze' })
        }
      },

      // Remove track
      removeTrack: (index: number) => {
        const tracks = get().tracks
        const newTracks = tracks.filter((_, i) => i !== index)
        set({ tracks: newTracks })
        
        // Reset to upload if no tracks
        if (newTracks.length === 0) {
          set({ currentStep: 'upload' })
        }
      },

      // Update track analysis
      updateTrackAnalysis: (index: number, analysis: Track['analysis']) => {
        const tracks = get().tracks
        const newTracks = tracks.map((track, i) => 
          i === index ? { ...track, analysis } : track
        )
        set({ tracks: newTracks })
        
        // Auto-advance to plan step if both tracks are analyzed
        if (newTracks.length === 2 && newTracks.every(t => t.analysis)) {
          set({ currentStep: 'plan' })
        }
      },

      // Set mashup plan
      setPlan: (plan: MashupPlan) => {
        set({ plan })
        set({ currentStep: 'render' })
      },

      // Set current step
      setCurrentStep: (step) => {
        set({ currentStep: step })
      },

      // Reset store
      reset: () => {
        set({
          tracks: [],
          plan: null,
          currentStep: 'upload'
        })
      }
    }),
    {
      name: 'mash-store',
      partialize: (state) => ({
        // Only persist essential data
        tracks: state.tracks.map(track => ({
          ...track,
          file: {
            name: track.file.name,
            size: track.file.size,
            type: track.file.type
          } as any // File objects can't be serialized
        })),
        plan: state.plan,
        currentStep: state.currentStep
      })
    }
  )
)
