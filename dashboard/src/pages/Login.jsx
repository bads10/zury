import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { login, getMe } from '../api'

export default function Login() {
  const navigate = useNavigate()
  const [email,    setEmail]    = useState('')
  const [password, setPassword] = useState('')
  const [error,    setError]    = useState('')
  const [loading,  setLoading]  = useState(false)

  async function handleSubmit(e) {
    e.preventDefault()
    setError('')
    setLoading(true)
    try {
      const { access_token } = await login(email, password)
      localStorage.setItem('zury_token', access_token)
      const me = await getMe()
      localStorage.setItem('zury_slug',        me.slug)
      localStorage.setItem('zury_seller_name', me.name)
      localStorage.setItem('zury_seller_id',   me.id)
      navigate('/catalogue', { replace: true })
    } catch (err) {
      setError(err.message || 'Identifiants invalides')
      localStorage.removeItem('zury_token')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="login-screen">
      <div className="login-card">
        <div className="login-card__logo">ZURY</div>
        <p className="login-card__sub">Espace vendeur</p>

        <form className="login-form" onSubmit={handleSubmit}>
          {error && <div className="alert-error">{error}</div>}

          <div className="form-group">
            <label className="form-label">Email</label>
            <input
              className="form-input"
              type="email"
              value={email}
              onChange={e => setEmail(e.target.value)}
              placeholder="demo@zury.africa"
              autoComplete="email"
              required
              autoFocus
            />
          </div>

          <div className="form-group">
            <label className="form-label">Mot de passe</label>
            <input
              className="form-input"
              type="password"
              value={password}
              onChange={e => setPassword(e.target.value)}
              placeholder="••••••••"
              autoComplete="current-password"
              required
            />
          </div>

          <button
            className="btn btn--gold"
            type="submit"
            disabled={loading}
            style={{ marginTop: 8 }}
          >
            {loading ? 'Connexion…' : 'Se connecter'}
          </button>
        </form>
      </div>
    </div>
  )
}
