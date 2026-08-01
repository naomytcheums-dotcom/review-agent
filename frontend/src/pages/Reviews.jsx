import { useEffect, useState } from 'react'
import { analyzeMr, getConfigStatus, listReviews, postReview } from '../api'

function Reviews() {
  const [configStatus, setConfigStatus] = useState(null)
  const [reviews, setReviews] = useState([])
  const [projectId, setProjectId] = useState('')
  const [mrIid, setMrIid] = useState('')
  const [analyzing, setAnalyzing] = useState(false)
  const [postingId, setPostingId] = useState(null)
  const [error, setError] = useState(null)
  const [summary, setSummary] = useState(null)
  const [showSetupInfo, setShowSetupInfo] = useState(false)

  useEffect(() => {
    refresh()
  }, [])

  async function refresh() {
    try {
      const status = await getConfigStatus()
      setConfigStatus(status)
      setReviews(await listReviews())
    } catch (err) {
      setError(err.message)
    }
  }

  async function handleAnalyze(e) {
    e.preventDefault()
    if (!configStatus.gitlab_configured) {
      setShowSetupInfo(true)
      return
    }
    setAnalyzing(true)
    setError(null)
    setSummary(null)
    try {
      const result = await analyzeMr(projectId, mrIid)
      setSummary(result)
      setReviews(await listReviews())
    } catch (err) {
      setError(err.message)
    } finally {
      setAnalyzing(false)
    }
  }

  async function handlePost(id) {
    setPostingId(id)
    setError(null)
    try {
      await postReview(id)
      setReviews(await listReviews())
    } catch (err) {
      setError(err.message)
    } finally {
      setPostingId(null)
    }
  }

  if (!configStatus) return null

  return (
    <div>
      <div className="page-header">
        <h1>Merge request review</h1>
        <p>
          Paste a project ID and MR number to analyze it now, or comment{' '}
          <code className="mono">/review</code> on a real merge request once your GitLab webhook is wired up
          (see the README).
        </p>
      </div>

      <div className="panel">
        {error && <div className="form-error">{error}</div>}
        {summary && (
          <div className="form-success">
            {summary.files_found} file{summary.files_found === 1 ? '' : 's'} changed, {summary.reviews_created} new
            review{summary.reviews_created === 1 ? '' : 's'} generated.
          </div>
        )}

        <form onSubmit={handleAnalyze}>
          <div className="form-row">
            <div className="form-field">
              <label>project_id</label>
              <input value={projectId} onChange={(e) => setProjectId(e.target.value)} placeholder="12345678" required />
            </div>
            <div className="form-field">
              <label>mr_iid</label>
              <input value={mrIid} onChange={(e) => setMrIid(e.target.value)} placeholder="42" required />
            </div>
          </div>

          <button className="btn-primary" type="submit" disabled={analyzing}>
            {analyzing ? 'Analyzing…' : 'Analyze merge request'}
          </button>
        </form>

        {showSetupInfo && (
          <div className="form-error" style={{ marginTop: 18 }}>
            This public demo doesn't have a GitLab token configured, so it can't reach any real project. To run it
            yourself: grab the code from{' '}
            <a href="https://github.com/naomytcheums-dotcom/review-agent" target="_blank" rel="noreferrer">
              GitHub
            </a>
            , create a free GitLab personal access token, and add it to your own <code>backend/.env</code> — full
            steps are in the README.
          </div>
        )}
      </div>

      {reviews.length === 0 && <div className="empty-state">No reviews yet — analyze a merge request above.</div>}

      <div className="reviews-grid">
        {reviews.map((review) => (
          <div className="review-card" key={review.id}>
            <div className="review-card-top">
              <div>
                <div className="review-file">{review.new_path || review.old_path}</div>
                <div className="review-meta">
                  !{review.mr_iid} in {review.project_id} — {review.triggered_by}
                </div>
              </div>
              <span
                className={`tag ${review.status === 'posted' ? 'tag-posted' : review.status === 'failed' ? 'tag-failed' : review.verdict === 'accept' ? 'tag-accept' : 'tag-reject'}`}
              >
                {review.status === 'posted' ? 'Posted' : review.status === 'failed' ? 'Failed' : review.verdict || 'Draft'}
              </span>
            </div>

            {review.status !== 'failed' && <div className="review-score">score: {review.score}/100</div>}
            {review.error_message && <div className="form-error">{review.error_message}</div>}

            {review.review_markdown && <div className="review-body">{review.review_markdown}</div>}

            {review.status === 'draft' && (
              <div className="review-actions">
                <button className="btn-secondary" onClick={() => handlePost(review.id)} disabled={postingId === review.id}>
                  {postingId === review.id ? 'Posting…' : 'Post to GitLab'}
                </button>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}

export default Reviews
