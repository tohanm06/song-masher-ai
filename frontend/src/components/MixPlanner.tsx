'use client'

import { useState, useEffect } from 'react'
import { Settings, Music, Zap, Key, AlertCircle, CheckCircle } from 'lucide-react'
import { useMashStore } from '@/state/useMashStore'

export function MixPlanner() {
  const { tracks, plan, setPlan } = useMashStore()
  const [selectedRecipe, setSelectedRecipe] = useState('AoverB')
  const [planning, setPlanning] = useState(false)
  const [planResult, setPlanResult] = useState<any>(null)

  const recipes = [
    {
      id: 'AoverB',
      name: 'A vocals + B instrumental',
      description: 'Track A vocals over Track B instrumental',
      icon: '🎤'
    },
    {
      id: 'BoverA', 
      name: 'B vocals + A instrumental',
      description: 'Track B vocals over Track A instrumental',
      icon: '🎵'
    },
    {
      id: 'HybridDrums',
      name: 'Hybrid drums',
      description: 'A vocals + B drums + mixed bass/other',
      icon: '🥁'
    }
  ]

  useEffect(() => {
    if (tracks.length >= 2 && tracks[0].analysis && tracks[1].analysis) {
      createPlan()
    }
  }, [tracks, selectedRecipe])

  const createPlan = async () => {
    if (tracks.length < 2 || !tracks[0].analysis || !tracks[1].analysis) return

    setPlanning(true)
    
    try {
      const response = await fetch('/api/plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          trackA: tracks[0].analysis,
          trackB: tracks[1].analysis,
          recipe: selectedRecipe
        })
      })

      if (!response.ok) {
        throw new Error('Planning failed')
      }

      const result = await response.json()
      setPlanResult(result)
      setPlan(result)
    } catch (error) {
      console.error('Planning failed:', error)
    } finally {
      setPlanning(false)
    }
  }

  const getCompatibilityScore = (score: number) => {
    if (score <= 1) return { color: 'text-green-600', label: 'Excellent' }
    if (score <= 2) return { color: 'text-yellow-600', label: 'Good' }
    if (score <= 3) return { color: 'text-orange-600', label: 'Acceptable' }
    return { color: 'text-red-600', label: 'Poor' }
  }

  const getStretchQuality = (quality: string) => {
    switch (quality) {
      case 'high': return { color: 'text-green-600', label: 'Minimal stretching' }
      case 'medium': return { color: 'text-yellow-600', label: 'Moderate stretching' }
      default: return { color: 'text-red-600', label: 'Heavy stretching' }
    }
  }

  return (
    <div className="card">
      <div className="flex items-center space-x-3 mb-6">
        <Settings className="w-6 h-6 text-primary-600" />
        <h2 className="text-xl font-semibold">Mashup Planning</h2>
      </div>

      {/* Recipe Selection */}
      <div className="mb-6">
        <h3 className="text-lg font-medium mb-4">Choose Strategy</h3>
        <div className="grid grid-cols-1 gap-3">
          {recipes.map((recipe) => (
            <label
              key={recipe.id}
              className={`
                relative flex items-center p-4 border-2 rounded-lg cursor-pointer transition-colors
                ${selectedRecipe === recipe.id
                  ? 'border-primary-500 bg-primary-50'
                  : 'border-gray-200 hover:border-gray-300'
                }
              `}
            >
              <input
                type="radio"
                name="recipe"
                value={recipe.id}
                checked={selectedRecipe === recipe.id}
                onChange={(e) => setSelectedRecipe(e.target.value)}
                className="sr-only"
              />
              <div className="flex items-center space-x-4">
                <div className="text-2xl">{recipe.icon}</div>
                <div>
                  <p className="font-medium text-gray-900">{recipe.name}</p>
                  <p className="text-sm text-gray-600">{recipe.description}</p>
                </div>
              </div>
            </label>
          ))}
        </div>
      </div>

      {/* Planning Results */}
      {planning && (
        <div className="flex items-center justify-center py-8">
          <div className="flex items-center space-x-3 text-primary-600">
            <div className="animate-spin rounded-full h-6 w-6 border-2 border-primary-600 border-t-transparent" />
            <span>Creating mashup plan...</span>
          </div>
        </div>
      )}

      {planResult && (
        <div className="space-y-6">
          {/* Key Alignment */}
          <div>
            <h3 className="text-lg font-medium mb-3">Key Alignment</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-3">
                <Key className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Target Key</p>
                  <p className="text-sm text-gray-600">{planResult.targetKey}</p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Music className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Key Shifts</p>
                  <p className="text-sm text-gray-600">
                    A: {planResult.keyShiftA > 0 ? '+' : ''}{planResult.keyShiftA} 
                    | B: {planResult.keyShiftB > 0 ? '+' : ''}{planResult.keyShiftB}
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Tempo Alignment */}
          <div>
            <h3 className="text-lg font-medium mb-3">Tempo Alignment</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="flex items-center space-x-3">
                <Zap className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Target BPM</p>
                  <p className="text-sm text-gray-600">
                    {Math.round(planResult.stretchMap.targetBpm)}
                  </p>
                </div>
              </div>
              <div className="flex items-center space-x-3">
                <Settings className="w-5 h-5 text-gray-400" />
                <div>
                  <p className="text-sm font-medium text-gray-900">Stretch Ratios</p>
                  <p className="text-sm text-gray-600">
                    A: {planResult.stretchMap.stretchA.toFixed(2)}x
                    | B: {planResult.stretchMap.stretchB.toFixed(2)}x
                  </p>
                </div>
              </div>
            </div>
          </div>

          {/* Section Alignment */}
          <div>
            <h3 className="text-lg font-medium mb-3">Section Alignment</h3>
            <div className="space-y-2">
              {planResult.sectionPairs.map((pair: any, index: number) => (
                <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded-lg">
                  <div className="flex items-center space-x-3">
                    <div className="w-2 h-2 bg-primary-500 rounded-full" />
                    <div>
                      <p className="text-sm font-medium text-gray-900">
                        {pair.sectionA.label} ↔ {pair.sectionB.label}
                      </p>
                      <p className="text-xs text-gray-500">
                        Confidence: {Math.round(pair.confidence * 100)}%
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quality Hints */}
          {planResult.qualityHints && planResult.qualityHints.length > 0 && (
            <div>
              <h3 className="text-lg font-medium mb-3">Quality Assessment</h3>
              <div className="space-y-2">
                {planResult.qualityHints.map((hint: string, index: number) => (
                  <div key={index} className="flex items-start space-x-2">
                    <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                    <p className="text-sm text-gray-700">{hint}</p>
                  </div>
                ))}
              </div>
            </div>
          )}
        </div>
      )}

      {/* Error State */}
      {!planning && !planResult && tracks.length >= 2 && (
        <div className="text-center py-8">
          <AlertCircle className="w-12 h-12 text-gray-400 mx-auto mb-4" />
          <p className="text-gray-500">Unable to create mashup plan</p>
          <button
            onClick={createPlan}
            className="mt-4 btn btn-primary"
          >
            Retry Planning
          </button>
        </div>
      )}
    </div>
  )
}
