import { useState, useCallback, useEffect } from 'react';
import './index.css';
import PricingPanel from './components/PricingPanel';
import GreeksPanel from './components/GreeksPanel';
import MonteCarloPanel from './components/MonteCarloPanel';
import VolSurfacePanel from './components/VolSurfacePanel';
import AIPredictionPanel from './components/AIPredictionPanel';
import { priceOption, getGreeks, getSurface, getMonteCarlo, predictVol } from './api/client';
import {
    TrendingUp, Activity, Dice5, Layers, BrainCircuit,
    Play, Loader2, ArrowRight, BarChart3, Shield, Cpu, Zap
} from 'lucide-react';

const PANEL_ICONS = {
    pricing: TrendingUp,
    greeks: Activity,
    montecarlo: Dice5,
    surface: Layers,
    ai: BrainCircuit,
};

const DEFAULT_PARAMS = {
    S: 100,
    K: 100,
    T: 1.0,
    r: 0.05,
    sigma: 0.25,
    option_type: 'call',
    ticker: 'AAPL',
};

function LandingPage({ onEnter }) {
    const [visible, setVisible] = useState(false);

    useEffect(() => {
        // Allow scrolling on the landing page
        document.documentElement.style.overflow = 'auto';
        document.body.style.overflow = 'auto';
        document.getElementById('root').style.overflow = 'auto';
        document.getElementById('root').style.height = 'auto';
        requestAnimationFrame(() => setVisible(true));
        return () => {
            document.documentElement.style.overflow = '';
            document.body.style.overflow = '';
            document.getElementById('root').style.overflow = '';
            document.getElementById('root').style.height = '';
        };
    }, []);

    // Scroll-reveal observer
    useEffect(() => {
        const observer = new IntersectionObserver(
            (entries) => {
                entries.forEach((entry) => {
                    if (entry.isIntersecting) {
                        entry.target.classList.add('revealed');
                        observer.unobserve(entry.target);
                    }
                });
            },
            { threshold: 0.15, rootMargin: '0px 0px -40px 0px' }
        );
        document.querySelectorAll('.reveal-on-scroll').forEach((el) => observer.observe(el));
        return () => observer.disconnect();
    }, [visible]);

    return (
        <div className={`landing ${visible ? 'landing--visible' : ''}`}>
            {/* ── Navigation ── */}
            <nav className="ln-nav">
                <div className="ln-nav-inner">
                    <div className="ln-brand">
                        <Zap size={18} strokeWidth={2.5} />
                        <span>QuantOps</span>
                    </div>
                    <button className="ln-nav-cta" onClick={onEnter}>
                        Open Dashboard <ArrowRight size={14} />
                    </button>
                </div>
            </nav>

            {/* ── Hero ── */}
            <section className="ln-hero">
                <div className="ln-hero-bg" />
                <div className="ln-hero-content">
                    <p className="ln-hero-eyebrow">Options Pricing & Volatility Analytics</p>
                    <h1 className="ln-hero-title">
                        Price, hedge, and forecast —<br />
                        all from one engine.
                    </h1>
                    <p className="ln-hero-desc">
                        QuantOps pairs three classical pricing models with an AI volatility
                        ensemble so you can evaluate options, visualise risk surfaces, and
                        detect regime shifts without juggling spreadsheets.
                    </p>
                    <div className="ln-hero-actions">
                        <button className="ln-cta-primary" onClick={onEnter}>
                            Launch the Engine <ArrowRight size={16} />
                        </button>
                        <a href="#capabilities" className="ln-cta-secondary">See what's inside</a>
                    </div>
                </div>
            </section>

            {/* ── Metrics Strip ── */}
            <section className="ln-metrics reveal-on-scroll">
                <div className="ln-metric">
                    <span className="ln-metric-value">3</span>
                    <span className="ln-metric-label">Pricing Models</span>
                </div>
                <div className="ln-metric-sep" />
                <div className="ln-metric">
                    <span className="ln-metric-value">5</span>
                    <span className="ln-metric-label">Greeks Computed</span>
                </div>
                <div className="ln-metric-sep" />
                <div className="ln-metric">
                    <span className="ln-metric-value">10k</span>
                    <span className="ln-metric-label">Monte Carlo Paths</span>
                </div>
                <div className="ln-metric-sep" />
                <div className="ln-metric">
                    <span className="ln-metric-value">3</span>
                    <span className="ln-metric-label">ML Models</span>
                </div>
                <div className="ln-metric-sep" />
                <div className="ln-metric">
                    <span className="ln-metric-value">32</span>
                    <span className="ln-metric-label">Unit Tests</span>
                </div>
            </section>

            {/* ── Capabilities ── */}
            <section className="ln-section" id="capabilities">
                <div className="ln-section-header reveal-on-scroll">
                    <h2>What you can do</h2>
                    <p>
                        Five panels, each designed for a different part of the options analysis workflow.
                    </p>
                </div>

                {/* Row 1 — Pricing */}
                <div className="ln-feature-row reveal-on-scroll">
                    <div className="ln-feature-text">
                        <div className="ln-feature-tag">Pricing</div>
                        <h3>Compare three models instantly</h3>
                        <p>
                            Run Black-Scholes, a 200-step Cox-Ross-Rubinstein binomial tree,
                            and a 10,000-path Monte Carlo simulation on the same parameters.
                            The comparison table highlights price differences down to the sixth
                            decimal so you can spot model risk at a glance.
                        </p>
                    </div>
                    <div className="ln-feature-visual">
                        <div className="ln-code-block">
                            <code>
                                <span className="code-muted">POST</span> /api/price<br />
                                <span className="code-key">S</span>: 100 &nbsp;
                                <span className="code-key">K</span>: 100 &nbsp;
                                <span className="code-key">T</span>: 1.0<br />
                                <br />
                                <span className="code-muted">→</span> BS: <span className="code-val">$12.3360</span><br />
                                <span className="code-muted">→</span> BT: <span className="code-val">$12.3236</span><br />
                                <span className="code-muted">→</span> MC: <span className="code-val">$12.4380</span>
                            </code>
                        </div>
                    </div>
                </div>

                {/* Row 2 — Greeks (reversed) */}
                <div className="ln-feature-row ln-feature-row--reverse reveal-on-scroll">
                    <div className="ln-feature-text">
                        <div className="ln-feature-tag">Greeks</div>
                        <h3>Map every sensitivity</h3>
                        <p>
                            Analytical Greeks are computed from the Black-Scholes closed-form
                            solution; numerical Greeks use finite-difference bumps. Both are
                            displayed side-by-side with an interactive chart that sweeps the
                            underlying price from 50&thinsp;% to 150&thinsp;% of spot.
                        </p>
                        <ul className="ln-feature-list">
                            <li>Delta, Gamma, Theta, Vega, Rho</li>
                            <li>Toggle individual Greeks on the chart</li>
                            <li>Analytical vs. numerical cross-check</li>
                        </ul>
                    </div>
                    <div className="ln-feature-visual">
                        <div className="ln-greeks-demo">
                            <div className="ln-greek"><span>Δ</span><span className="code-val">0.6274</span></div>
                            <div className="ln-greek"><span>Γ</span><span className="code-val">0.0151</span></div>
                            <div className="ln-greek"><span>Θ</span><span className="code-val">−0.0198</span></div>
                            <div className="ln-greek"><span>ν</span><span className="code-val">0.3781</span></div>
                            <div className="ln-greek"><span>ρ</span><span className="code-val">0.5040</span></div>
                        </div>
                    </div>
                </div>

                {/* Row 3 — Monte Carlo */}
                <div className="ln-feature-row reveal-on-scroll">
                    <div className="ln-feature-text">
                        <div className="ln-feature-tag">Monte Carlo</div>
                        <h3>Simulate 10,000 price paths</h3>
                        <p>
                            Geometric Brownian Motion drives each path. Antithetic variates
                            and control variates reduce standard error, and you get a payoff
                            histogram alongside the 95&thinsp;% confidence interval for the option
                            price. Every path is vizualised as a spaghetti plot.
                        </p>
                    </div>
                    <div className="ln-feature-visual">
                        <div className="ln-mc-visual">
                            {Array.from({ length: 8 }).map((_, i) => (
                                <div key={i} className="ln-mc-path" style={{
                                    animationDelay: `${i * 0.15}s`,
                                    '--end-y': `${-20 + Math.sin(i * 1.3) * 30}px`,
                                }} />
                            ))}
                        </div>
                    </div>
                </div>

                {/* Row 4 — Vol Surface (reversed) */}
                <div className="ln-feature-row ln-feature-row--reverse reveal-on-scroll">
                    <div className="ln-feature-text">
                        <div className="ln-feature-tag">Volatility Surface</div>
                        <h3>Explore the smile in 3-D</h3>
                        <p>
                            A synthetic implied-volatility surface spans 20 strikes
                            (70&thinsp;%–130&thinsp;% of spot) across eight maturities from one week to
                            one year. The skew, smile, and term-structure are modelled
                            parametrically — rendered as a Plotly 3-D surface and a heatmap.
                        </p>
                    </div>
                    <div className="ln-feature-visual">
                        <div className="ln-surface-demo">
                            <div className="ln-surface-grid">
                                {Array.from({ length: 40 }).map((_, i) => {
                                    const row = Math.floor(i / 8);
                                    const col = i % 8;
                                    const val = 0.3 + Math.abs(row - 2.5) * 0.06 - col * 0.01;
                                    return (
                                        <div key={i} className="ln-surface-cell" style={{
                                            opacity: 0.3 + val,
                                        }} />
                                    );
                                })}
                            </div>
                            <span className="ln-surface-label">Strike × Maturity → IV</span>
                        </div>
                    </div>
                </div>

                {/* Row 5 — AI Prediction */}
                <div className="ln-feature-row reveal-on-scroll">
                    <div className="ln-feature-text">
                        <div className="ln-feature-tag">AI Prediction</div>
                        <h3>Forecast volatility with an ML ensemble</h3>
                        <p>
                            GARCH(1,1) handles the near-term, an LSTM neural network
                            captures longer patterns, and a Hidden Markov Model identifies
                            whether the market is in a low-, medium-, or high-volatility regime.
                            Adaptive weights blend the three forecasts with confidence bands.
                        </p>
                        <ul className="ln-feature-list">
                            <li>GARCH — short-term conditional volatility</li>
                            <li>LSTM — sequence-modelled deep forecast</li>
                            <li>HMM — regime detection (Low / Med / High)</li>
                        </ul>
                    </div>
                    <div className="ln-feature-visual">
                        <div className="ln-regime-demo">
                            <div className="ln-regime-bar">
                                <div className="ln-regime-seg ln-regime-low" style={{ width: '55%' }} />
                                <div className="ln-regime-seg ln-regime-med" style={{ width: '30%' }} />
                                <div className="ln-regime-seg ln-regime-high" style={{ width: '15%' }} />
                            </div>
                            <div className="ln-regime-labels">
                                <span style={{ color: 'var(--accent-green)' }}>Low 55%</span>
                                <span style={{ color: 'var(--accent-yellow)' }}>Med 30%</span>
                                <span style={{ color: 'var(--accent-red)' }}>High 15%</span>
                            </div>
                        </div>
                    </div>
                </div>
            </section>

            {/* ── How It Works ── */}
            <section className="ln-section ln-section--alt reveal-on-scroll">
                <div className="ln-section-header">
                    <h2>How it works</h2>
                    <p>Two servers, one proxy — up and running in under a minute.</p>
                </div>
                <div className="ln-pipeline">
                    <div className="ln-pipe-step">
                        <span className="ln-pipe-num">1</span>
                        <h4>Parameters</h4>
                        <p>Enter spot, strike, expiry, volatility, and rate in the top bar.</p>
                    </div>
                    <div className="ln-pipe-arrow">→</div>
                    <div className="ln-pipe-step">
                        <span className="ln-pipe-num">2</span>
                        <h4>FastAPI Backend</h4>
                        <p>Python computes prices, Greeks, surfaces, and ML forecasts.</p>
                    </div>
                    <div className="ln-pipe-arrow">→</div>
                    <div className="ln-pipe-step">
                        <span className="ln-pipe-num">3</span>
                        <h4>React Dashboard</h4>
                        <p>Results render as cards, tables, and interactive Plotly/Recharts.</p>
                    </div>
                </div>
            </section>

            {/* ── Tech Stack ── */}
            <section className="ln-section reveal-on-scroll">
                <div className="ln-section-header">
                    <h2>Built with</h2>
                </div>
                <div className="ln-tech-grid">
                    <div className="ln-tech-col">
                        <h4>Backend</h4>
                        <ul>
                            <li>Python 3.12 — FastAPI + Uvicorn</li>
                            <li>NumPy · SciPy · Pandas</li>
                            <li>PyTorch (LSTM)</li>
                            <li>arch (GARCH) · hmmlearn (HMM)</li>
                            <li>Pydantic request validation</li>
                        </ul>
                    </div>
                    <div className="ln-tech-col">
                        <h4>Frontend</h4>
                        <ul>
                            <li>React 19 — Vite dev server</li>
                            <li>Recharts (2-D line / bar charts)</li>
                            <li>Plotly.js (3-D vol surface)</li>
                            <li>Lucide React (SVG icons)</li>
                            <li>Axios HTTP client</li>
                        </ul>
                    </div>
                    <div className="ln-tech-col">
                        <h4>Testing & Quality</h4>
                        <ul>
                            <li>pytest — 32 unit tests</li>
                            <li>httpx async API tests</li>
                            <li>SafeJSONResponse (NaN handling)</li>
                            <li>Vite proxy (CORS-free dev)</li>
                        </ul>
                    </div>
                </div>
            </section>

            {/* ── Footer CTA ── */}
            <footer className="ln-footer reveal-on-scroll">
                <h2>Ready to explore?</h2>
                <button className="ln-cta-primary" onClick={onEnter}>
                    Open the Dashboard <ArrowRight size={16} />
                </button>
                <p className="ln-footer-note">
                    Both servers run locally — nothing leaves your machine.
                </p>
            </footer>
        </div>
    );
}

export default function App() {
    const [showLanding, setShowLanding] = useState(true);
    const [transitioning, setTransitioning] = useState(false);
    const [activePanel, setActivePanel] = useState('pricing');
    const [params, setParams] = useState(DEFAULT_PARAMS);
    const [loading, setLoading] = useState(false);
    const [panelKey, setPanelKey] = useState(0);
    const [results, setResults] = useState({
        pricing: null,
        greeks: null,
        montecarlo: null,
        surface: null,
        ai: null,
    });

    const panels = [
        { id: 'pricing', label: 'Pricing' },
        { id: 'greeks', label: 'Greeks' },
        { id: 'montecarlo', label: 'Monte Carlo' },
        { id: 'surface', label: 'Vol Surface' },
        { id: 'ai', label: 'AI Predict' },
    ];

    const handleEnter = () => {
        setTransitioning(true);
        setTimeout(() => {
            setShowLanding(false);
            setTransitioning(false);
        }, 600);
    };

    const handlePanelChange = (id) => {
        if (id === activePanel) return;
        setActivePanel(id);
        setPanelKey(k => k + 1);
    };

    const handleChange = (field, value) => {
        setParams(prev => ({ ...prev, [field]: value }));
    };

    const handleRun = useCallback(async () => {
        setLoading(true);
        try {
            switch (activePanel) {
                case 'pricing': {
                    const data = await priceOption({ ...params, model: 'all' });
                    setResults(prev => ({ ...prev, pricing: data }));
                    break;
                }
                case 'greeks': {
                    const data = await getGreeks(params);
                    setResults(prev => ({ ...prev, greeks: data }));
                    break;
                }
                case 'montecarlo': {
                    const data = await getMonteCarlo({ ...params, n_paths: 10000, n_steps: 252 });
                    setResults(prev => ({ ...prev, montecarlo: data }));
                    break;
                }
                case 'surface': {
                    const data = await getSurface({ S: params.S, r: params.r, base_sigma: params.sigma });
                    setResults(prev => ({ ...prev, surface: data }));
                    break;
                }
                case 'ai': {
                    const data = await predictVol({ ticker: params.ticker, horizon: 10 });
                    setResults(prev => ({ ...prev, ai: data }));
                    break;
                }
            }
        } catch (err) {
            console.error('API Error:', err);
        } finally {
            setLoading(false);
        }
    }, [activePanel, params]);

    const showTicker = activePanel === 'ai';
    const showOptionParams = !showTicker;

    const renderPanel = () => {
        switch (activePanel) {
            case 'pricing': return <PricingPanel data={results.pricing} />;
            case 'greeks': return <GreeksPanel data={results.greeks} />;
            case 'montecarlo': return <MonteCarloPanel data={results.montecarlo} />;
            case 'surface': return <VolSurfacePanel data={results.surface} />;
            case 'ai': return <AIPredictionPanel data={results.ai} />;
            default: return null;
        }
    };

    if (showLanding) {
        return (
            <div className={transitioning ? 'app-exit' : ''}>
                <LandingPage onEnter={handleEnter} />
            </div>
        );
    }

    return (
        <div className="app app-enter">
            {/* Sidebar */}
            <aside className="sidebar">
                <div className="sidebar-header">
                    <div className="sidebar-logo">
                        <span className="logo-icon"><Zap size={14} /></span>
                        QuantOps
                    </div>
                    <div className="sidebar-subtitle">Options Engine</div>
                </div>

                <nav className="sidebar-nav">
                    {panels.map(p => {
                        const Icon = PANEL_ICONS[p.id];
                        return (
                            <div
                                key={p.id}
                                className={`nav-item ${activePanel === p.id ? 'active' : ''}`}
                                onClick={() => handlePanelChange(p.id)}
                            >
                                <span className="nav-icon"><Icon size={16} strokeWidth={1.8} /></span>
                                {p.label}
                            </div>
                        );
                    })}
                </nav>

                <div className="sidebar-footer">
                    <span className="status-dot" /> Engine Online
                </div>
            </aside>

            {/* Main */}
            <div className="main-content">
                {/* Top Bar */}
                <div className="top-bar">
                    {showTicker && (
                        <div className="input-group">
                            <label>Ticker</label>
                            <input
                                value={params.ticker}
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
                                <input type="number" value={params.S} onChange={e => handleChange('S', parseFloat(e.target.value) || 0)} />
                            </div>
                            <div className="input-group">
                                <label>Strike</label>
                                <input type="number" value={params.K} onChange={e => handleChange('K', parseFloat(e.target.value) || 0)} />
                            </div>
                            <div className="input-group">
                                <label>T (yrs)</label>
                                <input type="number" step="0.01" value={params.T} onChange={e => handleChange('T', parseFloat(e.target.value) || 0)} className="narrow" />
                            </div>
                            <div className="input-group">
                                <label>σ</label>
                                <input type="number" step="0.01" value={params.sigma} onChange={e => handleChange('sigma', parseFloat(e.target.value) || 0)} className="narrow" />
                            </div>
                            <div className="input-group">
                                <label>r</label>
                                <input type="number" step="0.01" value={params.r} onChange={e => handleChange('r', parseFloat(e.target.value) || 0)} className="narrow" />
                            </div>
                            <div className="input-group">
                                <label>Type</label>
                                <select value={params.option_type} onChange={e => handleChange('option_type', e.target.value)}>
                                    <option value="call">Call</option>
                                    <option value="put">Put</option>
                                </select>
                            </div>
                        </>
                    )}

                    <button className={`btn-run ${loading ? 'loading' : ''}`} onClick={handleRun} disabled={loading}>
                        {loading
                            ? <><Loader2 size={14} className="spin-icon" /> Computing...</>
                            : <><Play size={14} /> Run</>
                        }
                    </button>
                </div>

                {/* Panel Content */}
                <div className="panel-area">
                    <div className="panel-transition" key={panelKey}>
                        {renderPanel()}
                    </div>
                </div>
            </div>
        </div>
    );
}
