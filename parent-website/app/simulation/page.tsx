import Link from 'next/link';

export const metadata = {
  title: 'סימולציות רפואיות · MedicalHub',
  description: 'סימולציות אינטראקטיביות של גוף האדם — איברים ומחזור דם',
};

export default function SimulationIndexPage() {
  return (
    <main
      style={{
        minHeight: '100vh',
        background: 'radial-gradient(ellipse at top, #0d2340 0%, #05111f 60%, #02060d 100%)',
        display: 'flex',
        flexDirection: 'column',
        alignItems: 'center',
        justifyContent: 'center',
        gap: '40px',
        padding: '40px 20px',
        direction: 'rtl',
        fontFamily: "'Assistant', system-ui, sans-serif",
      }}
    >
      <div style={{ textAlign: 'center' }}>
        <h1
          style={{
            color: '#f5c518',
            fontSize: '2.2rem',
            fontWeight: 800,
            marginBottom: '12px',
          }}
        >
          סימולציות רפואיות
        </h1>
        <p style={{ color: '#8ea5c9', fontSize: '1rem' }}>
          חקור את גוף האדם בצורה אינטראקטיבית
        </p>
      </div>

      <div
        style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          gap: '24px',
          width: '100%',
          maxWidth: '700px',
        }}
      >
        <Link href="/simulation/anatomy" style={{ textDecoration: 'none' }}>
          <div
            style={{
              background: 'rgba(15, 28, 48, 0.85)',
              border: '1px solid rgba(140, 180, 230, 0.18)',
              borderRadius: '20px',
              padding: '36px 28px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>🫀</div>
            <h2 style={{ color: '#ecf2fb', fontSize: '1.3rem', fontWeight: 700, marginBottom: '10px' }}>
              גוף האדם — איברים
            </h2>
            <p style={{ color: '#96abc9', fontSize: '0.9rem', lineHeight: 1.6 }}>
              גרור איברים, למד על תפקידיהם והפעל סימולציות של כל איבר
            </p>
          </div>
        </Link>

        <Link href="/simulation/circulatory" style={{ textDecoration: 'none' }}>
          <div
            style={{
              background: 'rgba(10, 30, 54, 0.85)',
              border: '1px solid rgba(120, 180, 255, 0.18)',
              borderRadius: '20px',
              padding: '36px 28px',
              cursor: 'pointer',
              transition: 'all 0.2s',
              textAlign: 'center',
            }}
          >
            <div style={{ fontSize: '3rem', marginBottom: '16px' }}>❤️</div>
            <h2 style={{ color: '#e6f0ff', fontSize: '1.3rem', fontWeight: 700, marginBottom: '10px' }}>
              מחזור הדם
            </h2>
            <p style={{ color: '#8ea5c9', fontSize: '0.9rem', lineHeight: 1.6 }}>
              צפה בזרימת הדם בזמן אמת תחת 6 תרחישים שונים
            </p>
          </div>
        </Link>
      </div>

      <Link
        href="/articles"
        style={{
          color: '#96abc9',
          fontSize: '0.9rem',
          textDecoration: 'none',
          border: '1px solid rgba(140,180,230,0.2)',
          padding: '8px 18px',
          borderRadius: '999px',
        }}
      >
        ← חזרה למאמרים
      </Link>
    </main>
  );
}
