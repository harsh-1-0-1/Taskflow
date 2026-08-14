const BASE_URL = 'http://localhost:8000'

export async function request(path, options = {}) {
  const response = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })

  if (!response.ok) {
    let message = `Request failed with status ${response.status}`
    try {
      const body = await response.json()
      if (body && body.detail) message = body.detail
    } catch {
      // response had no JSON body; keep the generic message
    }
    throw new Error(message)
  }

  if (response.status === 204) return null
  return response.json()
}
