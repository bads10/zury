import { useState, useEffect, useCallback } from 'react'
import { useNavigate } from 'react-router-dom'
import { getGarments, deleteGarment, resolveImageUrl } from '../api'

function GarmentImage({ name, imageUrl }) {
  const [errored, setErrored] = useState(false)
  const initial = (name || '?')[0].toUpperCase()

  if (!imageUrl || errored) {
    return (
      <div className="garment-card__img-ph">
        <span className="garment-card__initial">{initial}</span>
      </div>
    )
  }
  return (
    <img
      className="garment-card__img"
      src={resolveImageUrl(imageUrl)}
      alt={name}
      loading="lazy"
      onError={() => setErrored(true)}
    />
  )
}

function CopyBtn({ slug, garmentId }) {
  const [copied, setCopied] = useState(false)

  function handleCopy() {
    const url = `https://zury.africa/try/${slug}?garment=${garmentId}`
    navigator.clipboard.writeText(url).then(() => {
      setCopied(true)
      setTimeout(() => setCopied(false), 2200)
    })
  }

  return (
    <button className={`btn btn--ghost btn-copy${copied ? ' btn-copy--ok' : ''}`} onClick={handleCopy}>
      {copied ? (
        <>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2.2" strokeLinecap="round"><polyline points="20 6 9 17 4 12"/></svg>
          Lien copié !
        </>
      ) : (
        <>
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><rect x="9" y="9" width="13" height="13" rx="2"/><path d="M5 15H4a2 2 0 0 1-2-2V4a2 2 0 0 1 2-2h9a2 2 0 0 1 2 2v1"/></svg>
          Copier lien Zury
        </>
      )}
    </button>
  )
}

function GarmentCard({ garment, slug, onDeleted }) {
  const navigate = useNavigate()
  const [deleting, setDeleting] = useState(false)

  async function handleDelete(e) {
    e.stopPropagation()
    if (!window.confirm(`Supprimer « ${garment.name} » ?`)) return
    setDeleting(true)
    try {
      await deleteGarment(garment.id)
      onDeleted(garment.id)
    } catch (err) {
      alert(err.message)
      setDeleting(false)
    }
  }

  function handleEdit(e) {
    e.stopPropagation()
    navigate(`/modifier/${garment.id}`)
  }

  return (
    <div className={`garment-card${deleting ? ' garment-card--deleting' : ''}`}>
      <div className="garment-card__media">
        <GarmentImage name={garment.name} imageUrl={garment.image_url} />
        <div className="garment-card__overlay">
          <button className="garment-card__overlay-btn garment-card__overlay-btn--edit" onClick={handleEdit} title="Modifier">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><path d="M11 4H4a2 2 0 0 0-2 2v14a2 2 0 0 0 2 2h14a2 2 0 0 0 2-2v-7"/><path d="M18.5 2.5a2.121 2.121 0 0 1 3 3L12 15l-4 1 1-4 9.5-9.5z"/></svg>
          </button>
          <button className="garment-card__overlay-btn garment-card__overlay-btn--delete" onClick={handleDelete} title="Supprimer">
            <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round"><polyline points="3 6 5 6 21 6"/><path d="M19 6l-1 14a2 2 0 0 1-2 2H8a2 2 0 0 1-2-2L5 6"/><path d="M10 11v6M14 11v6"/><path d="M9 6V4a1 1 0 0 1 1-1h4a1 1 0 0 1 1 1v2"/></svg>
          </button>
        </div>
      </div>

      <div className="garment-card__body">
        <span className="garment-card__name">{garment.name}</span>
        {garment.category && <span className="garment-card__cat">{garment.category}</span>}
        {garment.meta?.price != null && (
          <span className="garment-card__price">
            {Number(garment.meta.price).toLocaleString('fr-FR')} FCFA
          </span>
        )}
      </div>
      <div className="garment-card__foot">
        <CopyBtn slug={slug} garmentId={garment.id} />
      </div>
    </div>
  )
}

export default function Catalogue() {
  const navigate  = useNavigate()
  const slug      = localStorage.getItem('zury_slug') || ''
  const [garments, setGarments] = useState([])
  const [loading,  setLoading]  = useState(true)
  const [error,    setError]    = useState('')

  const load = useCallback(async () => {
    setLoading(true); setError('')
    try { setGarments(await getGarments(slug)) }
    catch (err) { setError(err.message) }
    finally { setLoading(false) }
  }, [slug])

  useEffect(() => { load() }, [load])

  const handleDeleted = id => setGarments(gs => gs.filter(g => g.id !== id))

  return (
    <>
      <div className="page-header">
        <h1>Catalogue</h1>
        {!loading && !error && (
          <p>{garments.length} vêtement{garments.length !== 1 ? 's' : ''}</p>
        )}
      </div>

      {loading && <div className="loading-center"><div className="spinner" /></div>}
      {!loading && error && <div className="alert-error">{error}</div>}

      {!loading && !error && garments.length === 0 && (
        <div className="empty-state">
          <div className="empty-state__icon">👗</div>
          <p>Aucun vêtement pour l'instant</p>
          <button className="btn btn--gold" onClick={() => navigate('/ajouter')}>
            Ajouter un vêtement
          </button>
        </div>
      )}

      {!loading && garments.length > 0 && (
        <div className="garment-grid">
          {garments.map(g => (
            <GarmentCard key={g.id} garment={g} slug={slug} onDeleted={handleDeleted} />
          ))}
        </div>
      )}

      <button className="fab" onClick={() => navigate('/ajouter')} aria-label="Ajouter">+</button>
    </>
  )
}
