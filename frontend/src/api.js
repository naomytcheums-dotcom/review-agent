export const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8080'

async function handle(res) {
  if (!res.ok) {
    let message = 'Something went wrong.'
    try {
      const data = await res.json()
      message = data.detail || message
    } catch {
      // ignore
    }
    throw new Error(message)
  }
  return res.json()
}

export async function getConfigStatus() {
  const res = await fetch(`${API_URL}/api/config-status`)
  return handle(res)
}

export async function getSettings() {
  const res = await fetch(`${API_URL}/api/settings`)
  return handle(res)
}

export async function saveSettings(settings) {
  const res = await fetch(`${API_URL}/api/settings`, {
    method: 'PUT',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(settings),
  })
  return handle(res)
}

export async function listReviews() {
  const res = await fetch(`${API_URL}/api/reviews`)
  return handle(res)
}

export async function analyzeMr(projectId, mrIid) {
  const res = await fetch(`${API_URL}/api/reviews/analyze`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ project_id: projectId, mr_iid: mrIid }),
  })
  return handle(res)
}

export async function postReview(id) {
  const res = await fetch(`${API_URL}/api/reviews/${id}/post`, { method: 'POST' })
  return handle(res)
}
