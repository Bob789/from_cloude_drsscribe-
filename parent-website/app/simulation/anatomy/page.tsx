'use client';

export default function AnatomySimulationPage() {
  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        background: '#0a1425',
      }}
    >
      <iframe
        src="/simulations/anatomy/index.html"
        style={{ width: '100%', height: '100%', border: 'none', display: 'block' }}
        title="גוף האדם — סימולציית איברים"
        allow="fullscreen"
      />
    </div>
  );
}
