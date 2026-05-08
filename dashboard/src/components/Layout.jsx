import { NavLink, Outlet, useNavigate } from 'react-router-dom'

const IconGrid = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round">
    <rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/>
    <rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/>
  </svg>
)
const IconPlus = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
    <circle cx="12" cy="12" r="9"/><line x1="12" y1="8" x2="12" y2="16"/><line x1="8" y1="12" x2="16" y2="12"/>
  </svg>
)
const IconChart = () => (
  <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round">
    <line x1="18" y1="20" x2="18" y2="10"/><line x1="12" y1="20" x2="12" y2="4"/><line x1="6" y1="20" x2="6" y2="14"/>
  </svg>
)

const NAV = [
  { to: '/catalogue', label: 'Catalogue',     Icon: IconGrid  },
  { to: '/ajouter',   label: 'Ajouter',       Icon: IconPlus  },
  { to: '/stats',     label: 'Statistiques',  Icon: IconChart },
]

export default function Layout() {
  const navigate = useNavigate()
  const sellerName = localStorage.getItem('zury_seller_name') || 'Vendeur'

  function logout() {
    ['zury_token', 'zury_slug', 'zury_seller_name', 'zury_seller_id'].forEach(k =>
      localStorage.removeItem(k)
    )
    navigate('/login', { replace: true })
  }

  const linkClass = ({ isActive }) => `nav-link${isActive ? ' active' : ''}`

  return (
    <div className="layout">
      <aside className="sidebar">
        <div className="sidebar__logo">ZURY</div>
        <nav className="sidebar__nav">
          {NAV.map(({ to, label, Icon }) => (
            <NavLink key={to} to={to} className={linkClass}>
              <Icon />{label}
            </NavLink>
          ))}
        </nav>
        <div className="sidebar__footer">
          <div className="sidebar__seller">{sellerName}</div>
          <button className="btn-logout" onClick={logout}>Déconnexion</button>
        </div>
      </aside>

      <main className="layout__main">
        <Outlet />
      </main>

      <nav className="bottom-nav">
        <div className="bottom-nav__items">
          {NAV.map(({ to, label, Icon }) => (
            <NavLink key={to} to={to} className={({ isActive }) => `bottom-nav__item${isActive ? ' active' : ''}`}>
              <Icon /><span>{label}</span>
            </NavLink>
          ))}
        </div>
      </nav>
    </div>
  )
}
