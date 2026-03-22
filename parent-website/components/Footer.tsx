import Link from 'next/link'

export default function Footer() {
  return (
    <footer>
      <div className="footer-logo">MedicalHub</div>
      <div className="footer-links">
        <Link href="/articles">מאמרים</Link>
        <Link href="/forum">פורום</Link>
        <Link href="/experts">מומחים</Link>
        <Link href="/product">Doctor Scribe AI</Link>
      </div>
      <div className="footer-legal">
        <Link href="/terms">תנאי שימוש</Link>
        <span>|</span>
        <Link href="/privacy">מדיניות פרטיות</Link>
        <span>|</span>
        <Link href="/medical-disclaimer">הצהרת שימוש רפואי</Link>
      </div>
      <div className="footer-copy">© 2026 Medical Hub</div>
    </footer>
  )
}
