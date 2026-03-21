import Link from 'next/link'

export default function ArticlesHeader() {
  return (
    <header className="site-header">
      <div className="header-container">
        <div className="header-top">
          <Link href="/" className="brand">
            <div className="logo-circle">MH</div>
            <div>
              <div className="brand-name">Medical Hub</div>
              <div className="brand-sub">מאמרים • פורום • מומחים • תמלול</div>
            </div>
          </Link>
          <div className="header-btns">
            <Link href="/login" className="hbtn hbtn-ghost">התחברות</Link>
            <Link href="/product" className="hbtn hbtn-cta">שירות תמלול לקליניקה</Link>
          </div>
        </div>
        <nav className="site-nav">
          <Link href="/"        className="nav-pill">דף הבית</Link>
          <Link href="/articles" className="nav-pill active">מאמרים</Link>
          <Link href="/forum"   className="nav-pill">פורום</Link>
          <Link href="/experts" className="nav-pill">מומחים</Link>
        </nav>
      </div>
    </header>
  )
}
