import { useEffect, useState } from 'react'
import { getConfigStatus, getSettings, saveSettings } from '../api'

function Settings() {
  const [triggerPhrase, setTriggerPhrase] = useState('')
  const [configStatus, setConfigStatus] = useState(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [error, setError] = useState(null)
  const [saved, setSaved] = useState(false)

  useEffect(() => {
    Promise.all([getSettings(), getConfigStatus()])
      .then(([settings, status]) => {
        setTriggerPhrase(settings.trigger_phrase || '/review')
        setConfigStatus(status)
      })
      .catch((err) => setError(err.message))
      .finally(() => setLoading(false))
  }, [])

  async function handleSubmit(e) {
    e.preventDefault()
    setSaving(true)
    setError(null)
    setSaved(false)
    try {
      await saveSettings({ trigger_phrase: triggerPhrase })
      setSaved(true)
    } catch (err) {
      setError(err.message)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return null

  return (
    <div>
      <div className="page-header">
        <h1>Settings</h1>
        <p>Configure the comment that triggers an automatic review on your GitLab merge requests.</p>
      </div>

      <div className="panel">
        {error && <div className="form-error">{error}</div>}
        {saved && <div className="form-success">Saved.</div>}

        <form onSubmit={handleSubmit}>
          <div className="form-field">
            <label>trigger_phrase</label>
            <input
              value={triggerPhrase}
              onChange={(e) => setTriggerPhrase(e.target.value)}
              placeholder="/review"
              required
            />
          </div>

          <button className="btn-primary" type="submit" disabled={saving}>
            {saving ? 'Saving…' : 'Save'}
          </button>
        </form>
      </div>

      {configStatus && (
        <>
          <div className="page-header" style={{ marginTop: 40 }}>
            <h1 style={{ fontSize: 16 }}>Server configuration</h1>
          </div>
          <div className="panel">
            <div className="form-field" style={{ marginBottom: 10 }}>
              <label>gitlab</label>
              <div className="mono" style={{ fontSize: 13 }}>
                {configStatus.gitlab_configured ? `configured — ${configStatus.gitlab_url}` : 'not configured'}
              </div>
            </div>
            <div className="form-field" style={{ marginBottom: 0 }}>
              <label>llm</label>
              <div className="mono" style={{ fontSize: 13 }}>
                {configStatus.llm_configured ? 'configured' : 'not configured'}
              </div>
            </div>
          </div>
        </>
      )}
    </div>
  )
}

export default Settings
