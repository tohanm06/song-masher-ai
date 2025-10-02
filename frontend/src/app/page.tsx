'use client'

import { useState } from 'react'
import { FileDrop } from '@/components/FileDrop'
import { AnalysisCard } from '@/components/AnalysisCard'
import { MixPlanner } from '@/components/MixPlanner'
import { Timeline } from '@/components/Timeline'
import { RenderPanel } from '@/components/RenderPanel'
import { useMashStore } from '@/state/useMashStore'

export default function Home() {
  const { tracks, currentStep } = useMashStore()
  
  return (
    <main className="container mx-auto px-4 py-8">
      <div className="max-w-6xl mx-auto">
        {/* Header */}
        <div className="text-center mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            Song Masher AI
          </h1>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            Create professional mashups with AI-powered stem separation, 
            beat alignment, and key matching.
          </p>
        </div>

        {/* Progress Steps */}
        <div className="mb-8">
          <div className="flex items-center justify-center space-x-8">
            {[
              { id: 'upload', label: 'Upload', icon: '📁' },
              { id: 'analyze', label: 'Analyze', icon: '🔍' },
              { id: 'plan', label: 'Plan', icon: '📋' },
              { id: 'render', label: 'Render', icon: '🎵' },
            ].map((step, index) => (
              <div key={step.id} className="flex items-center">
                <div className={`
                  w-12 h-12 rounded-full flex items-center justify-center text-lg font-semibold
                  ${currentStep === step.id 
                    ? 'bg-primary-600 text-white' 
                    : currentStep === 'upload' && index === 0
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-200 text-gray-600'
                  }
                `}>
                  {step.icon}
                </div>
                <span className={`
                  ml-2 text-sm font-medium
                  ${currentStep === step.id ? 'text-primary-600' : 'text-gray-500'}
                `}>
                  {step.label}
                </span>
                {index < 3 && (
                  <div className={`
                    w-8 h-0.5 ml-4
                    ${currentStep === step.id ? 'bg-primary-600' : 'bg-gray-200'}
                  `} />
                )}
              </div>
            ))}
          </div>
        </div>

        {/* Main Content */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left Column - Upload & Analysis */}
          <div className="space-y-6">
            <FileDrop />
            
            {tracks.length > 0 && (
              <div className="space-y-4">
                {tracks.map((track, index) => (
                  <AnalysisCard key={index} track={track} index={index} />
                ))}
              </div>
            )}
          </div>

          {/* Right Column - Planning & Rendering */}
          <div className="space-y-6">
            {tracks.length >= 2 && (
              <>
                <MixPlanner />
                <Timeline />
                <RenderPanel />
              </>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-16 text-center text-sm text-gray-500">
          <p>
            Song Masher AI - Professional audio mashup tool with AI-powered analysis
          </p>
          <p className="mt-2">
            Built with Next.js, FastAPI, and advanced audio processing
          </p>
        </div>
      </div>
    </main>
  )
}
