const API_BASE = 'http://localhost:8000'

export function resolveImageUrl(url) {
  if (!url) return null
  if (url.startsWith('/')) return `${API_BASE}${url}`
  return url
}

function authHeader() {
  const token = localStorage.getItem('zury_token')
  return token ? { Authorization: `Bearer ${token}` } : {}
}

async function handleRes(res) {
  if (!res.ok) {
    let msg = `Erreur ${res.status}`
    try { const d = await res.json(); msg = d.detail || msg } catch (_) {}
    throw new Error(msg)
  }
  return res.json()
}

export async function login(email, password) {
  const res = await fetch(`${API_BASE}/api/v1/sellers/login`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
    body: new URLSearchParams({ username: email, password }),
  })
  return handleRes(res)
}

export async function getMe() {
  const res = await fetch(`${API_BASE}/api/v1/sellers/me`, {
    headers: authHeader(),
  })
  return handleRes(res)
}

export async function getGarments(slug) {
  const res = await fetch(`${API_BASE}/api/v1/sellers/${slug}/garments`)
  return handleRes(res)
}

export async function createGarment(data) {
  const res = await fetch(`${API_BASE}/api/v1/sellers/me/garments`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(data),
  })
  return handleRes(res)
}

export async function uploadGarmentImage(file) {
  const form = new FormData()
  form.append('file', file)
  const res = await fetch(`${API_BASE}/api/v1/sellers/me/garments/image`, {
    method: 'POST',
    headers: authHeader(),
    body: form,
  })
  return handleRes(res)
}

export async function getGarment(slug, garmentId) {
  const res = await fetch(`${API_BASE}/api/v1/sellers/${slug}/garment/${garmentId}`)
  return handleRes(res)
}

export async function updateGarment(garmentId, data) {
  const res = await fetch(`${API_BASE}/api/v1/sellers/me/garments/${garmentId}`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json', ...authHeader() },
    body: JSON.stringify(data),
  })
  return handleRes(res)
}

export async function deleteGarment(garmentId) {
  const res = await fetch(`${API_BASE}/api/v1/sellers/me/garments/${garmentId}`, {
    method: 'DELETE',
    headers: authHeader(),
  })
  if (!res.ok) {
    let msg = `Erreur ${res.status}`
    try { const d = await res.json(); msg = d.detail || msg } catch (_) {}
    throw new Error(msg)
  }
}

export async function getAnalytics(sellerId) {
  const res = await fetch(`${API_BASE}/api/v1/analytics/seller/${sellerId}`, {
    headers: authHeader(),
  })
  return handleRes(res)
}
