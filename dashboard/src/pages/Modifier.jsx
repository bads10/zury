import { useState, useEffect, useRef } from 'react'
import { useNavigate, useParams } from 'react-router-dom'
import { getGarment, updateGarment, uploadGarmentImage, resolveImageUrl } from '../api'

const CATEGORIES = ['robe', 'ensemble', 'tenue', 'chemise', 'pantalon', 'accessoire', 'autre']

export default function Modifier() {
  const { id }   = useParams()
  const navigate = useNavigate()
  const slug     = localStorage.getItem('zury_slug') || ''
  const fileRef  = useRef()

  const [form, setForm] = useState({
    name: '', price: '', fabric: '', category: '', description: '',
  })
  const [existingImageUrl, setExistingImageUrl] = useState('')
  const [imageFile,        setImageFile]        = useState(null)
  const [imagePreview,     setImagePreview]     = useState('')
  const [loadingData,      setLoadingData]      = useState(true)
  const [loading,          setLoading]          = useState(false)
  const [error,            setError]            = useState('')

  useEffect(() => {
    getGarment(slug, id)
      .then(g => {
        setForm({
          name:        g.name        || '',
          price:       g.meta?.price != null ? String(g.meta.price) : '',
          fabric:      g.meta?.fabric || '',
          category:    g.category    || '',
          description: g.description || '',
        })
        setExistingImageUrl(g.image_url || '')
        setLoadingData(false)
      })
      .catch(err => { setError(err.message); setLoadingData(false) })
  }, [id, slug])

  const set = field => e => setForm(f => ({ ...f, [field]: e.target.value }))

  function handleImageChange(e) {
    const file = e.target.files?.[0]
    if (!file) return
    setImageFile(file)
    const reader = new FileReader()
    reader.onload = ev => setImagePreview(ev.target.result)
    reader.readAsDataURL(file)
  }

  async function handleSubmit(e) {
    e.preventDefault()
    if (!form.name.trim()) return setError('Le nom est obligatoire')
    setError(''); setLoading(true)
    try {
      let image_url = null
      if (imageFile) {
        const res = await uploadGarmentImage(imageFile)
        image_url = res.image_url
      }
      const meta = {}
      if (form.price)  meta.price  = Number(form.price)
      if (form.fabric) meta.fabric = form.fabric
      await updateGarment(id, {
        name:        form.name,
        description: form.description || null,
        category:    form.category    || null,
        image_url,   // null = keep existing (backend ignores null)
        meta:        Object.keys(meta).length ? meta : null,
      })
      navigate('/catalogue')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  const previewSrc = imagePreview || resolveImageUrl(existingImageUrl)

  if (loadingData) return <div className="loading-center"><div className="spinner" /></div>

  return (
    <div className="ajouter-wrap">
      <div className="page-header">
        <h1>Modifier le vêtement</h1>
      </div>

      <form className="form-section" onSubmit={handleSubmit}>
        {error && <div className="alert-error">{error}</div>}

        {/* Image */}
        <div className="form-group">
          <label className="form-label">Photo</label>
          <div className="image-upload-zone" onClick={() => fileRef.current?.click()}>
            {previewSrc ? (
              <>
                <img className="image-upload-zone__preview" src={previewSrc} alt="Preview" />
                <span className="image-upload-zone__change">Changer</span>
              </>
            ) : (
              <div className="image-upload-zone__ph">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round">
                  <rect x="3" y="3" width="18" height="18" rx="3"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
                <span>Cliquer pour changer la photo</span>
              </div>
            )}
            <input ref={fileRef} type="file" accept="image/*"
              onChange={handleImageChange} style={{ display: 'none' }} />
          </div>
        </div>

        {/* Nom + prix */}
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Nom *</label>
            <input className="form-input" value={form.name} onChange={set('name')} required />
          </div>
          <div className="form-group">
            <label className="form-label">Prix (FCFA)</label>
            <input className="form-input" type="number" min="0" value={form.price} onChange={set('price')} />
          </div>
        </div>

        {/* Tissu + catégorie */}
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Tissu</label>
            <input className="form-input" value={form.fabric} onChange={set('fabric')} placeholder="Wax, Coton, Bazin…" />
          </div>
          <div className="form-group">
            <label className="form-label">Catégorie</label>
            <select className="form-select" value={form.category} onChange={set('category')}>
              <option value="">— Choisir —</option>
              {CATEGORIES.map(c => (
                <option key={c} value={c}>{c.charAt(0).toUpperCase() + c.slice(1)}</option>
              ))}
            </select>
          </div>
        </div>

        {/* Description */}
        <div className="form-group">
          <label className="form-label">Description</label>
          <textarea className="form-textarea" value={form.description} onChange={set('description')} />
        </div>

        <div className="form-actions">
          <button type="button" className="btn btn--ghost" onClick={() => navigate('/catalogue')}>
            Annuler
          </button>
          <button className="btn btn--gold" type="submit" disabled={loading}>
            {loading ? 'Enregistrement…' : 'Enregistrer'}
          </button>
        </div>
      </form>
    </div>
  )
}
