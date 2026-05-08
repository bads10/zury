import { useState, useRef } from 'react'
import { useNavigate } from 'react-router-dom'
import { uploadGarmentImage, createGarment } from '../api'

const CATEGORIES = ['robe', 'ensemble', 'tenue', 'chemise', 'pantalon', 'accessoire', 'autre']

export default function Ajouter() {
  const navigate = useNavigate()
  const fileRef  = useRef()
  const [form, setForm] = useState({
    name: '', price: '', fabric: '', category: '', description: '',
  })
  const [imageFile,    setImageFile]    = useState(null)
  const [imagePreview, setImagePreview] = useState('')
  const [loading,  setLoading]  = useState(false)
  const [error,    setError]    = useState('')

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
      await createGarment({
        name:        form.name,
        description: form.description || null,
        category:    form.category    || null,
        image_url,
        meta: Object.keys(meta).length ? meta : null,
      })
      navigate('/catalogue')
    } catch (err) {
      setError(err.message)
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="ajouter-wrap">
      <div className="page-header">
        <h1>Ajouter un vêtement</h1>
      </div>

      <form className="form-section" onSubmit={handleSubmit}>
        {error && <div className="alert-error">{error}</div>}

        {/* Image */}
        <div className="form-group">
          <label className="form-label">Photo</label>
          <div className="image-upload-zone" onClick={() => fileRef.current?.click()}>
            {imagePreview ? (
              <>
                <img className="image-upload-zone__preview" src={imagePreview} alt="Preview" />
                <span className="image-upload-zone__change">Changer</span>
              </>
            ) : (
              <div className="image-upload-zone__ph">
                <svg width="36" height="36" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.4" strokeLinecap="round">
                  <rect x="3" y="3" width="18" height="18" rx="3"/>
                  <circle cx="8.5" cy="8.5" r="1.5"/>
                  <polyline points="21 15 16 10 5 21"/>
                </svg>
                <span>Cliquer pour ajouter une photo</span>
                <span className="image-upload-zone__hint">JPG, PNG · recommandé 480 × 720</span>
              </div>
            )}
            <input
              ref={fileRef}
              type="file"
              accept="image/*"
              onChange={handleImageChange}
              style={{ display: 'none' }}
            />
          </div>
        </div>

        {/* Nom + prix */}
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Nom *</label>
            <input className="form-input" value={form.name} onChange={set('name')}
              placeholder="Robe Safran" required />
          </div>
          <div className="form-group">
            <label className="form-label">Prix (FCFA)</label>
            <input className="form-input" type="number" min="0" value={form.price}
              onChange={set('price')} placeholder="15 000" />
          </div>
        </div>

        {/* Tissu + catégorie */}
        <div className="form-row">
          <div className="form-group">
            <label className="form-label">Tissu</label>
            <input className="form-input" value={form.fabric} onChange={set('fabric')}
              placeholder="Wax, Coton, Bazin…" />
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
          <textarea className="form-textarea" value={form.description}
            onChange={set('description')}
            placeholder="Coupe évasée, manches 3/4, disponible en plusieurs tailles…" />
        </div>

        <div className="form-actions">
          <button type="button" className="btn btn--ghost"
            onClick={() => navigate('/catalogue')}>
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
