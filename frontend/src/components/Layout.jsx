import React from 'react';

export default function Layout({ activePanel, setActivePanel, params, setParams, onRun, loading }) {
    const panels = [
        { id: 'pricing', icon: '⚡', label: 'Pricing' },
        { id: 'greeks', icon: '∂', label: 'Greeks' },
        { id: 'montecarlo', icon: '◈', label: 'Monte Carlo' },
        { id: 'surface', icon: '◆', label: 'Vol Surface' },
        { id: 'ai', icon: '◎', label: 'AI Predict' },
    ];

    return (
        <div className="app">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <div className="sidebar-logo">
                        <span className="logo-icon">Σ</span>
                        QuantOps
                    </div>
                    <div className="sidebar-subtitle">Options Engine</div>
                </div>

                <nav className="sidebar-nav">
                    {panels.map(p => (
                        <div
                            key={p.id}
                            className={`nav-item ${activePanel === p.id ? 'active' : ''}`}
                            onClick={() => setActivePanel(p.id)}
                        >
                            <span className="nav-icon">{p.icon}</span>
                            {p.label}
                        </div>
                    ))}
                </nav>

                <div className="sidebar-footer">
                    <span className="status-dot" /> Engine Online
                </div>
            </aside>

            {/* Top Bar + Panel */}
            <div className="main-content">
                <TopBar params={params} setParams={setParams} onRun={onRun} loading={loading} activePanel={activePanel} />
                <div className="panel-area">
                    {/* Children rendered by App.jsx */}
                </div>
            </div>
        </div>
    );
}

function TopBar({ params, setParams, onRun, loading, activePanel }) {
    const handleChange = (field, value) => {
        setParams(prev => ({ ...prev, [field]: value }));
    };

    const showTicker = activePanel === 'ai';
    const showOptionParams = !showTicker;

    return (
        <div className="top-bar">
            {showTicker && (
                <div className="input-group">
                    <label>Ticker</label>
                    <input
                        value={params.ticker || 'AAPL'}
                        onChange={e => handleChange('ticker', e.target.value.toUpperCase())}
                        className="wide"
                        placeholder="AAPL"
                    />
                </div>
            )}

            {showOptionParams && (
                <>
                    <div className="input-group">
                        <label>Spot</label>
                        <input
                            type="number"
                            value={params.S}
                            onChange={e => handleChange('S', parseFloat(e.target.value) || 0)}
                        />
                    </div>
                    <div className="input-group">
                        <label>Strike</label>
                        <input
                            type="number"
                            value={params.K}
                            onChange={e => handleChange('K', parseFloat(e.target.value) || 0)}
                        />
                    </div>
                    <div className="input-group">
                        <label>T (yrs)</label>
                        <input
                            type="number"
                            step="0.01"
                            value={params.T}
                            onChange={e => handleChange('T', parseFloat(e.target.value) || 0)}
                            className="narrow"
                        />
                    </div>
                    <div className="input-group">
                        <label>σ</label>
                        <input
                            type="number"
                            step="0.01"
                            value={params.sigma}
                            onChange={e => handleChange('sigma', parseFloat(e.target.value) || 0)}
                            className="narrow"
                        />
                    </div>
                    <div className="input-group">
                        <label>r</label>
                        <input
                            type="number"
                            step="0.01"
                            value={params.r}
                            onChange={e => handleChange('r', parseFloat(e.target.value) || 0)}
                            className="narrow"
                        />
                    </div>
                    <div className="input-group">
                        <label>Type</label>
                        <select
                            value={params.option_type}
                            onChange={e => handleChange('option_type', e.target.value)}
                        >
                            <option value="call">Call</option>
                            <option value="put">Put</option>
                        </select>
                    </div>
                </>
            )}

            <button
                className={`btn-run ${loading ? 'loading' : ''}`}
                onClick={onRun}
                disabled={loading}
            >
                {loading ? '⟳ Computing...' : '▶ Run'}
            </button>
        </div>
    );
}
