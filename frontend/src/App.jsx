
import { useEffect, useState } from 'react'
import './App.css'

const API_URL = 'http://127.0.0.1:8000'

const pages = [
  { id: 'dashboard', label: 'Dashboard', icon: '▦' },
  { id: 'sentiment', label: 'Sentiment Analysis', icon: '◉' },
  { id: 'themes', label: 'Feedback Themes', icon: '◇' },
  { id: 'insights', label: 'AI Insights', icon: '✧' },
  { id: 'actions', label: 'Action Items', icon: '☑' },
  { id: 'anomalies', label: 'Anomaly Detection', icon: '⚠' },
]

const sentimentItems = [
  { name: 'Positive', key: 'positive', color: '#22A879' },
  { name: 'Neutral', key: 'neutral', color: '#E9AD43' },
  { name: 'Negative', key: 'negative', color: '#E66F79' },
  { name: 'Mixed', key: 'mixed', color: '#8B72D6' },
]

function formatAIInsights(text) {
  if (!text) {
    return <p>No AI insights are available.</p>
  }

  return text.split(/\r?\n/).map((line, index) => {
    const trimmed = line.trim()

    if (!trimmed) {
      return <div key={index} className="ai-spacer" />
    }

    if (trimmed.startsWith('**') && trimmed.endsWith('**')) {
      return (
        <h3 key={index} className="ai-insight-heading">
          {trimmed.replace(/\*\*/g, '')}
        </h3>
      )
    }

    if (/^[*-]\s+/.test(trimmed)) {
      return (
        <p key={index} className="ai-insight-bullet">
          <span>•</span>
          {trimmed.replace(/^[*-]\s+/, '')}
        </p>
      )
    }

    return (
      <p key={index} className="ai-insight-paragraph">
        {trimmed}
      </p>
    )
  })
}

function getArray(result) {
  if (Array.isArray(result)) return result
  if (Array.isArray(result?.items)) return result.items
  if (Array.isArray(result?.results)) return result.results
  if (Array.isArray(result?.anomalies)) return result.anomalies
  if (Array.isArray(result?.action_items)) return result.action_items
  return []
}

function App() {
  const [activePage, setActivePage] = useState('dashboard')

  const [data, setData] = useState(null)
  const [actions, setActions] = useState([])
  const [anomalies, setAnomalies] = useState([])
  const [anomalySummary, setAnomalySummary] = useState(null)

  const [loading, setLoading] = useState(true)
  const [actionLoading, setActionLoading] = useState(true)
  const [anomalyLoading, setAnomalyLoading] = useState(true)

  const [error, setError] = useState('')
  const [actionError, setActionError] = useState('')
  const [anomalyError, setAnomalyError] = useState('')

  const [expandedAction, setExpandedAction] = useState(null)
  const [actionSources, setActionSources] = useState({})
  const [sourceLoading, setSourceLoading] = useState(false)

  useEffect(() => {
    async function fetchAnalytics() {
      try {
        const response = await fetch(
          `${API_URL}/analytics/ai-insights`
        )

        if (!response.ok) {
          throw new Error(`Analytics API failed (${response.status})`)
        }

        const result = await response.json()
        setData(result)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }

    async function fetchActions() {
      try {
        const response = await fetch(`${API_URL}/action-items/`)

        if (!response.ok) {
          throw new Error(`Action Items API failed (${response.status})`)
        }

        const result = await response.json()
        setActions(getArray(result))
      } catch (err) {
        setActionError(err.message)
      } finally {
        setActionLoading(false)
      }
    }

    async function fetchAnomalies() {
      try {
        const [listResponse, summaryResponse] = await Promise.all([
          fetch(`${API_URL}/anomalies/`),
          fetch(`${API_URL}/anomalies/summary`),
        ])

        if (!listResponse.ok) {
          throw new Error(`Anomaly API failed (${listResponse.status})`)
        }

        const listResult = await listResponse.json()
        setAnomalies(getArray(listResult))

        if (summaryResponse.ok) {
          const summaryResult = await summaryResponse.json()
          setAnomalySummary(summaryResult)
        }
      } catch (err) {
        setAnomalyError(err.message)
      } finally {
        setAnomalyLoading(false)
      }
    }

    fetchAnalytics()
    fetchActions()
    fetchAnomalies()
  }, [])

  const sentiment = data?.sentiment_percentages || {}
  const distribution = data?.sentiment_distribution || {}
  const themes = data?.theme_analytics || []

  async function toggleActionSources(actionId) {
    if (expandedAction === actionId) {
      setExpandedAction(null)
      return
    }

    setExpandedAction(actionId)

    if (actionSources[actionId]) return

    setSourceLoading(true)

    try {
      const response = await fetch(
        `${API_URL}/action-items/${encodeURIComponent(actionId)}/sources`
      )

      if (!response.ok) {
        throw new Error(`Could not load source records (${response.status})`)
      }

      const result = await response.json()
      setActionSources((previous) => ({
        ...previous,
        [actionId]: result,
      }))
    } catch (err) {
      setActionSources((previous) => ({
        ...previous,
        [actionId]: { error: err.message },
      }))
    } finally {
      setSourceLoading(false)
    }
  }

  const currentPage = pages.find((page) => page.id === activePage)

  function PageHeader({ title, description }) {
    return (
      <div className="page-header">
        <p className="eyebrow">INSIGHTPULSE AI WORKSPACE</p>
        <h2>{title}</h2>
        <p>{description}</p>
      </div>
    )
  }

  function StatCard({ title, value, detail, icon, color = 'purple' }) {
    return (
      <div className="stat-card">
        <div className="stat-top">
          <span>{title}</span>
          <span className={`stat-icon ${color}`}>{icon}</span>
        </div>
        <h2>{value}</h2>
        <p>{detail}</p>
      </div>
    )
  }

  function SentimentChart() {
    return (
      <section className="content-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">CUSTOMER EXPERIENCE</p>
            <h2>Sentiment Distribution</h2>
          </div>
          <span className="section-tag">Overall Analysis</span>
        </div>

        <div className="sentiment-bar">
          {sentimentItems.map((item) => (
            <div
              key={item.key}
              style={{
                width: `${sentiment[item.key] || 0}%`,
                backgroundColor: item.color,
              }}
            />
          ))}
        </div>

        <div className="legend">
          {sentimentItems.map((item) => (
            <span key={item.key}>
              <i
                className="dot"
                style={{ backgroundColor: item.color }}
              />
              {item.name}
              <b>{sentiment[item.key] ?? 0}%</b>
            </span>
          ))}
        </div>
      </section>
    )
  }


  function DashboardOverviewChart() {
    const total = data?.total_feedback_analyzed ?? 0

    const items = [
      { key: 'positive', name: 'Positive', color: '#36C995' },
      { key: 'neutral', name: 'Neutral', color: '#FFBD35' },
      { key: 'negative', name: 'Negative', color: '#FF5265' },
      { key: 'mixed', name: 'Mixed', color: '#9565F5' },
    ]

    let currentAngle = 0

    const segments = items.map((item) => {
      const percentage = Number(sentiment[item.key] ?? 0)
      const start = currentAngle
      currentAngle += percentage

      return {
        ...item,
        percentage,
        start,
        end: currentAngle,
        count: distribution[item.key] ?? 0,
      }
    })

    const gradient = segments
      .map((item) =>
        `${item.color} ${item.start}% ${item.end}%`
      )
      .join(', ')

    return (
      <section className="dashboard-overview-card">
        <div className="dashboard-chart-heading">
          <div className="dashboard-chart-icon">▥</div>
          <div>
            <h2>Customer Feedback Overview</h2>
            <p>Distribution of customer feedback by sentiment</p>
          </div>
        </div>

        <div className="dashboard-chart-layout">
          <div className="dashboard-donut-area">
            <div
              className="dashboard-donut"
              style={{
                background: `conic-gradient(${gradient})`,
              }}
            >
              <div className="dashboard-donut-hole">
                <strong>{total.toLocaleString()}</strong>
                <span>Total</span>
                <span>Feedback</span>
              </div>
            </div>
          </div>

          <div className="dashboard-chart-legend">
            {segments.map((item) => (
              <div className="dashboard-legend-row" key={item.key}>
                <div className="dashboard-legend-name">
                  <span
                    className="dashboard-legend-dot"
                    style={{ backgroundColor: item.color }}
                  />
                  <strong>{item.name}</strong>
                </div>

                <strong className="dashboard-legend-value">
                  {Number(item.count).toLocaleString()} ({item.percentage.toFixed(2)}%)
                </strong>
              </div>
            ))}
          </div>
        </div>
      </section>
    )
  }


  function ThemeList() {
    return (
      <section className="content-card">
        <div className="section-heading">
          <div>
            <p className="eyebrow">DISCOVER WHAT MATTERS</p>
            <h2>Customer Feedback Themes</h2>
          </div>
          <span className="section-tag">Theme Analysis</span>
        </div>

        {themes.length === 0 ? (
          <div className="empty-state">
            <p>No feedback themes are available.</p>
          </div>
        ) : (
          <div className="theme-list">
            {themes.map((theme, index) => (
              <div className="theme-row" key={theme.theme || index}>
                <div className="theme-number">
                  {String(index + 1).padStart(2, '0')}
                </div>

                <div className="theme-details">
                  <h3>{theme.theme}</h3>
                  <p>
                    {theme.feedback_count?.toLocaleString() ?? 0} records
                  </p>
                </div>

                <div className="theme-negative">
                  <strong>{theme.negative_percentage ?? 0}%</strong>
                  <span>Negative</span>
                </div>
              </div>
            ))}
          </div>
        )}
      </section>
    )
  }

  
  function DashboardPage() {
    return (
      <>
        {data && (
          <section className="stats-grid">
            <StatCard
              title="Total Feedback"
              value={data.total_feedback_analyzed?.toLocaleString() ?? 0}
              detail="Customer feedback records"
              icon="▤"
            />

            <StatCard
              title="Positive"
              value={distribution.positive?.toLocaleString() ?? 0}
              detail={`${sentiment.positive ?? 0}% of total`}
              icon="↗"
              color="green"
            />

            <StatCard
              title="Neutral"
              value={distribution.neutral?.toLocaleString() ?? 0}
              detail={`${sentiment.neutral ?? 0}% of total`}
              icon="◉"
              color="yellow"
            />

            <StatCard
              title="Negative"
              value={distribution.negative?.toLocaleString() ?? 0}
              detail={`${sentiment.negative ?? 0}% of total`}
              icon="↘"
              color="red"
            />

            <StatCard
              title="Mixed"
              value={distribution.mixed?.toLocaleString() ?? 0}
              detail={`${sentiment.mixed ?? 0}% of total`}
              icon="◈"
            />
          </section>
        )}

        {data && <DashboardOverviewChart />}
      </>
    )
  }


  function SentimentPage() {
    return (
      <>
        <PageHeader
          title="Sentiment Analysis"
          description="Understand how customers feel about your products and services."
        />

        {data && (
          <>
            <section className="stats-grid">
              {sentimentItems.map((item) => (
                <StatCard
                  key={item.key}
                  title={`${item.name} Feedback`}
                  value={`${sentiment[item.key] ?? 0}%`}
                  detail={`${distribution[item.key] ?? 0} records`}
                  icon="●"
                  color={
                    item.key === 'positive'
                      ? 'green'
                      : item.key === 'neutral'
                        ? 'yellow'
                        : item.key === 'negative'
                          ? 'red'
                          : 'purple'
                  }
                />
              ))}
            </section>

            <SentimentChart />

            <section className="content-card">
              <div className="section-heading">
                <div>
                  <p className="eyebrow">SENTIMENT SUMMARY</p>
                  <h2>Feedback Overview</h2>
                </div>
              </div>

              <p className="ai-response">
                {data.total_feedback_analyzed ?? 0} customer feedback
                records have been analyzed. The sentiment distribution
                above shows the proportion of positive, neutral, negative
                and mixed feedback.
              </p>
            </section>
          </>
        )}
      </>
    )
  }

  function ThemesPage() {
    return (
      <>
        <PageHeader
          title="Feedback Themes"
          description="Explore the main topics customers discuss in their feedback."
        />
        {data && <ThemeList />}
      </>
    )
  }

  function InsightsPage() {
    return (
      <>
        <PageHeader
          title="AI Insights Assistant"
          description="AI-generated customer feedback intelligence powered by Llama 3.2."
        />

        <section className="content-card ai-card">
          <div className="ai-heading">
            <div className="ai-icon">✧</div>
            <div>
              <p className="eyebrow">POWERED BY LLAMA 3.2</p>
              <h2>Customer Feedback Intelligence Report</h2>
            </div>
            <span className="ai-badge">AI Analysis</span>
          </div>

          {data ? (
            <div className="ai-response">
              {formatAIInsights(data.ai_insights)}
            </div>
          ) : (
            <p>AI insights are not available.</p>
          )}

          <p className="ai-note">
            Recommendations are generated from available customer feedback
            statistics and detected themes.
          </p>
        </section>
      </>
    )
  }

  function ActionsPage() {
    return (
      <>
        <PageHeader
          title="Action Items"
          description="Review AI-generated recommendations and trace them back to customer feedback."
        />

        <section className="stats-grid">
          <StatCard
            title="Total Actions"
            value={actions.length}
            detail="Available recommendations"
            icon="☑"
          />

          <StatCard
            title="Critical Priority"
            value={actions.filter((a) => a.priority?.toLowerCase() === 'critical').length}
            detail="Requires urgent attention"
            icon="!"
            color="red"
          />

          <StatCard
            title="High Priority"
            value={actions.filter((a) => a.priority?.toLowerCase() === 'high').length}
            detail="High-priority actions"
            icon="↑"
            color="yellow"
          />

          <StatCard
          title="Medium Priority"
          value={actions.filter((a) => a.priority?.toLowerCase() === 'medium').length}
          detail="Medium-priority actions"
          icon="●"
          color="yellow"
          />
        </section>

        <section className="content-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">RECOMMENDATION MANAGEMENT</p>
              <h2>Prioritized Action Items</h2>
            </div>
            <span className="section-tag">{actions.length} Actions</span>
          </div>

          {actionLoading && <p>Loading action items...</p>}

          {actionError && (
            <div className="error-card">
              <p>{actionError}</p>
            </div>
          )}

          {!actionLoading && !actionError && actions.length === 0 && (
            <div className="empty-state">
              <h3>No action items found</h3>
              <p>There are currently no recommendations to display.</p>
            </div>
          )}

          {actions.map((action) => {
            const id = action.action_id

            return (
              <div className="action-record" key={id}>
                <div className="action-record-top">
                  <div>
                    <h3>{action.action_title || 'Untitled Action'}</h3>
                    <p>
                    {id.startsWith('ACT-AUTO-')
                    ? `${action.negative_percentage}% of ${action.source_count.toLocaleString()} feedback records for ${action.action_title.replace('Automatic: Improve ', '')} are negative. This exceeds the configured threshold of ${action.threshold_percentage}%. Investigate the linked feedback records and define corrective actions.`
                    : action.description}
                    </p>
                  </div>

                  <span className={`priority-badge priority-${(action.priority || 'medium').toLowerCase()}`}>
                    {action.priority || 'Medium'}
                  </span>
                </div>

                <div className="action-meta">
                  <span>Status: {action.status || 'Open'}</span>
                  <span>Sources: {action.source_count ?? 0}</span>
                  {action.negative_percentage != null && (
                    <span>Negative: {action.negative_percentage}%</span>
                  )}
                </div>

                <button
                  className="secondary-button"
                  onClick={() => toggleActionSources(id)}
                >
                  {expandedAction === id
                    ? 'Hide source feedback'
                    : 'View source feedback'}
                </button>

                {expandedAction === id && (
                  <div className="source-panel">
                    {sourceLoading && <p>Loading source feedback...</p>}

                    {actionSources[id]?.error && (
                      <p>{actionSources[id].error}</p>
                    )}

                    {(actionSources[id]?.sources || []).map((source, index) => (
                      <div className="source-record" key={source.source_id || index}>
                        <strong>{source.source_id || 'Source record'}</strong>
                        <p>{source.text || source.feedback_text || source.message || 'Source text unavailable.'}</p>
                      </div>
                    ))}

                    {actionSources[id] &&
                      !actionSources[id].error &&
                      !(actionSources[id].sources || []).length && (
                       <p>
  No linked source records are available for this historical action.
  The source count shown above is the previously recorded count.
</p>
                      )}
                  </div>
                )}
              </div>
            )
          })}
        </section>
      </>
    )
  }

  function AnomaliesPage() {
    const summary = anomalySummary || {}

    return (
      <>
        <PageHeader
          title="Anomaly Detection"
          description="Monitor unusual feedback records and review data-quality exceptions."
        />

        <section className="stats-grid">
          <StatCard
            title="Total Anomalies"
            value={summary.total_anomalies ?? summary.total ?? anomalies.length}
            detail="Detected records"
            icon="⚠"
            color="red"
          />

          <StatCard
            title="High Severity"
            value={summary.by_severity?.High ?? 0}
            detail="High-severity records"
            icon="!"
            color="red"
          />

          <StatCard
            title="Medium Severity"
            value={summary.by_severity?.Medium ?? 0}
            detail="Medium-severity records"
            icon="◉"
            color="yellow"
          />

          <StatCard
            title="Low Severity"
            value={summary.by_severity?.Low ?? 0}
            detail="Low-severity records"
            icon="●"
            color="green"
          />
        </section>

        <section className="content-card">
          <div className="section-heading">
            <div>
              <p className="eyebrow">DATA QUALITY MONITORING</p>
              <h2>Detected Anomalies</h2>
            </div>
            <span className="section-tag">{anomalies.length} Records</span>
          </div>

          {anomalyLoading && <p>Loading anomalies...</p>}

          {anomalyError && (
            <div className="error-card">
              <p>{anomalyError}</p>
            </div>
          )}

          {!anomalyLoading && !anomalyError && anomalies.length === 0 && (
            <div className="empty-state">
              <h3>No anomalies found</h3>
              <p>There are no anomaly records to display.</p>
            </div>
          )}

          {anomalies.map((anomaly, index) => (
            <div className="anomaly-record" key={anomaly.anomaly_id || index}>
              <div className="action-record-top">
                <div>
                  <h3>{anomaly.anomaly_type || 'Detected anomaly'}</h3>
                  <p>{anomaly.description || 'No description available.'}</p>
                </div>

                <span className={`priority-badge priority-${(anomaly.severity || 'low').toLowerCase()}`}>
                  {anomaly.severity || 'Low'}
                </span>
              </div>

              <div className="action-meta">
                <span>Source: {anomaly.source_type || 'Unknown'}</span>
                <span>ID: {anomaly.source_id || 'Unavailable'}</span>
                <span>Status: {anomaly.status || 'Open'}</span>
              </div>
            </div>
          ))}
        </section>
      </>
    )
  }

  function renderPage() {
    if (loading && activePage !== 'actions' && activePage !== 'anomalies') {
      return <div className="message-card">Loading customer analytics...</div>
    }

    if (error && ['dashboard', 'sentiment', 'themes', 'insights'].includes(activePage)) {
      return (
        <div className="error-card">
          <h3>Unable to load analytics</h3>
          <p>{error}</p>
          <p>Make sure the FastAPI backend is running.</p>
        </div>
      )
    }

    switch (activePage) {
      case 'dashboard':
        return <DashboardPage />
      case 'sentiment':
        return <SentimentPage />
      case 'themes':
        return <ThemesPage />
      case 'insights':
        return <InsightsPage />
      case 'actions':
        return <ActionsPage />
      case 'anomalies':
        return <AnomaliesPage />
      default:
        return <DashboardPage />
    }
  }

  return (
    <div className="app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-icon">IP</div>
          <div>
            <h2>InsightPulse</h2>
            <span>AI Intelligence</span>
          </div>
        </div>

        <nav className="navigation">
          <p className="nav-heading">WORKSPACE</p>

          {pages.map((page) => (
            <button
              key={page.id}
              type="button"
              className={`nav-link ${activePage === page.id ? 'active' : ''}`}
              onClick={() => setActivePage(page.id)}
            >
              <span>{page.icon}</span>
              {page.label}
            </button>
          ))}
        </nav>

        <div className="sidebar-bottom">
          <div className="status-dot"></div>
          <span>InsightPulse AI Platform</span>
        </div>
      </aside>

      <main className="main-content">
        <header className="topbar">
          <div>
            <p className="breadcrumb">
              Workspace / {currentPage?.label}
            </p>
            <h1>{currentPage?.label}</h1>
          </div>

          <div className="topbar-right">
            <span className="live-indicator">● Live Analytics</span>
            <div className="avatar">AI</div>
          </div>
        </header>

        {renderPage()}

        <footer className="footer">
          InsightPulse AI · Customer Feedback Intelligence Platform
        </footer>
      </main>
    </div>
  )
}

export default App
