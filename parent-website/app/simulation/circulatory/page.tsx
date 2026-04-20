'use client';

export default function CirculatorySimulationPage() {
  return (
    <div
      style={{
        position: 'fixed',
        inset: 0,
        zIndex: 9999,
        background: '#05111f',
      }}
    >
      <iframe
        src="/simulations/circulatory/index.html"
        style={{ width: '100%', height: '100%', border: 'none', display: 'block' }}
        title="סימולציות מחזור הדם"
        allow="fullscreen"
      />
    </div>
  );
}
