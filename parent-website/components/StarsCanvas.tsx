'use client'
import { useRef, useEffect } from 'react'

export default function StarsCanvas() {
  const canvasRef = useRef<HTMLCanvasElement>(null)

  useEffect(() => {
    const canvas = canvasRef.current
    if (!canvas) return
    const ctx = canvas.getContext('2d')
    if (!ctx) return

    let W: number, H: number
    let animId: number

    const resize = () => {
      W = canvas.width  = window.innerWidth
      H = canvas.height = window.innerHeight
    }
    resize()
    window.addEventListener('resize', resize)

    interface Star { x: number; y: number; r: number; dx: number; dy: number; o: number }
    const stars: Star[] = []
    for (let i = 0; i < 80; i++) {
      stars.push({
        x:  Math.random() * 1400,
        y:  Math.random() * 900,
        r:  Math.random() * 1.8 + 0.3,
        dx: (Math.random() - 0.5) * 0.15,
        dy: -Math.random() * 0.5 - 0.15,
        o:  Math.random() * 0.7 + 0.2,
      })
    }

    const draw = () => {
      ctx.clearRect(0, 0, W, H)
      stars.forEach(s => {
        ctx.beginPath()
        ctx.arc(s.x, s.y, s.r, 0, Math.PI * 2)
        ctx.fillStyle = `rgba(255,255,255,${s.o})`
        ctx.fill()
        s.x += s.dx
        s.y += s.dy
        if (s.y < -10) { s.y = H + 10; s.x = Math.random() * W }
        if (s.x < -10) s.x = W + 10
        if (s.x > W + 10) s.x = -10
      })
      animId = requestAnimationFrame(draw)
    }
    draw()

    return () => {
      window.removeEventListener('resize', resize)
      cancelAnimationFrame(animId)
    }
  }, [])

  return (
    <canvas
      ref={canvasRef}
      aria-hidden="true"
      style={{
        position: 'fixed',
        inset: 0,
        width: '100%',
        height: '100%',
        pointerEvents: 'none',
        zIndex: 0,
      }}
    />
  )
}
