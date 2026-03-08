'use client'

import { useRef, useState } from 'react'

interface MedScribeEmbedProps {
  url: string
}

export default function MedScribeEmbed({ url }: MedScribeEmbedProps) {
  const iframeRef = useRef<HTMLIFrameElement>(null)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)

  const handleLoad = () => {
    setIsLoading(false)
    setHasError(false)
  }

  const handleError = () => {
    setIsLoading(false)
    setHasError(true)
  }

  const handleRetry = () => {
    setIsLoading(true)
    setHasError(false)
    if (iframeRef.current) {
      iframeRef.current.src = url
    }
  }

  return (
    <div className="relative w-full h-full bg-gray-100">
      {/* Loading State */}
      {isLoading && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-50 z-10">
          <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin mb-4" />
          <p className="text-gray-600 font-medium">טוען את MedScribe AI...</p>
        </div>
      )}

      {/* Error State */}
      {hasError && (
        <div className="absolute inset-0 flex flex-col items-center justify-center bg-gray-50 z-10">
          <div className="text-5xl mb-4">⚠️</div>
          <p className="text-gray-800 font-semibold text-lg mb-2">לא ניתן לטעון את המערכת</p>
          <p className="text-gray-500 mb-6">ודא שהשרת פועל על {url}</p>
          <button
            onClick={handleRetry}
            className="bg-blue-600 text-white px-6 py-3 rounded-lg font-medium hover:bg-blue-700 transition-colors"
          >
            נסה שוב
          </button>
        </div>
      )}

      {/* Iframe */}
      <iframe
        ref={iframeRef}
        src={url}
        className="w-full h-full border-0"
        sandbox="allow-same-origin allow-scripts allow-forms allow-popups allow-modals allow-popups-to-escape-sandbox"
        allow="microphone; camera; clipboard-read; clipboard-write"
        onLoad={handleLoad}
        onError={handleError}
      />
    </div>
  )
}
