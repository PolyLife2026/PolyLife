function getToken() {
  return localStorage.getItem('token')
}

function setTokens({ token, refresh }) {
  if (token) localStorage.setItem('token', token)
  if (refresh) localStorage.setItem('refresh', refresh)
}

function clearTokens() {
  localStorage.removeItem('token')
  localStorage.removeItem('refresh')
}

async function handle(res) {
  let data = null
  try {
    data = await res.json()
  } catch (e) {
    data = null
  }
  if (!res.ok) {
    const message = (data && (data.detail || JSON.stringify(data))) || `خطای ${res.status}`
    throw new Error(message)
  }
  return data
}

export async function coreFetch(path, options = {}) {
  const res = await fetch(`/core${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(options.headers || {}),
    },
  })
  return handle(res)
}

export async function apiFetch(path, options = {}) {
  const token = getToken()
  const res = await fetch(`/api${path}`, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
      ...(options.headers || {}),
    },
  })
  return handle(res)
}

export const auth = {
  async register(username, password) {
    return coreFetch('/api/register', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
  },
  async login(username, password) {
    const data = await coreFetch('/api/login', {
      method: 'POST',
      body: JSON.stringify({ username, password }),
    })
    setTokens(data)
    return data
  },
  async logout() {
    const token = getToken()
    try {
      await coreFetch('/api/logout', {
        method: 'POST',
        headers: token ? { Authorization: `Bearer ${token}` } : {},
      })
    } catch (e) {
    }
    clearTokens()
  },
  isLoggedIn() {
    return !!getToken()
  },
}
