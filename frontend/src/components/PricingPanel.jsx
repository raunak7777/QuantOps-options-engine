import React from 'react';
import { TrendingUp, ClipboardList } from 'lucide-react';

export default function PricingPanel({ data }) {
    if (!data) {
        return (
            <div className="panel-card fade-in">
                <div className="panel-card-header">
                    <span className="panel-card-title"><TrendingUp size={14} /> Pricing Comparison</span>
                </div>
                <div className="panel-card-body">
                    <div className="empty-state">
                        <div className="empty-icon"><TrendingUp size={32} strokeWidth={1} /></div>
                        <p>Configure parameters and click <strong>Run</strong> to price the option across all models.</p>
                    </div>
                </div>
            </div>
        );
    }

    const models = [];
    if (data.black_scholes) models.push({ key: 'bs', label: 'Black-Scholes', badge: 'bs', ...data.black_scholes });
    if (data.binomial) models.push({ key: 'bt', label: 'Binomial Tree', badge: 'bt', ...data.binomial });
    if (data.monte_carlo) models.push({ key: 'mc', label: 'Monte Carlo', badge: 'mc', ...data.monte_carlo });

    const bsPrice = data.black_scholes?.price;

    return (
        <div className="fade-in">
            {/* Price Cards */}
            <div className="stats-grid">
                {models.map(m => (
                    <div className="stat-box" key={m.key}>
                        <div className="stat-label">
                            <span className={`model-badge ${m.badge}`}>{m.label}</span>
                        </div>
                        <div className={`stat-value ${m.badge === 'bs' ? 'cyan' : m.badge === 'bt' ? 'green' : 'purple'}`}>
                            ${m.price.toFixed(4)}
                        </div>
                        {bsPrice && m.key !== 'bs' && (
                            <div className="stat-sub">
                                Δ {((m.price - bsPrice) / bsPrice * 100).toFixed(3)}% from BS
                            </div>
                        )}
                        {m.std_error && (
                            <div className="stat-sub">SE: ±{m.std_error.toFixed(4)}</div>
                        )}
                    </div>
                ))}
            </div>

            {/* Comparison Table */}
            <div className="panel-card">
                <div className="panel-card-header">
                    <span className="panel-card-title"><TrendingUp size={14} /> Model Comparison</span>
                </div>
                <div className="panel-card-body">
                    <table className="comparison-table">
                        <thead>
                            <tr>
                                <th>Model</th>
                                <th>Price</th>
                                <th>Difference</th>
                                <th>Details</th>
                            </tr>
                        </thead>
                        <tbody>
                            {models.map(m => (
                                <tr key={m.key}>
                                    <td><span className={`model-badge ${m.badge}`}>{m.label}</span></td>
                                    <td style={{ fontWeight: 600 }}>${m.price.toFixed(6)}</td>
                                    <td>
                                        {bsPrice && m.key !== 'bs'
                                            ? `${(m.price - bsPrice) >= 0 ? '+' : ''}${(m.price - bsPrice).toFixed(6)}`
                                            : '—'}
                                    </td>
                                    <td style={{ color: 'var(--text-muted)', fontSize: 11 }}>
                                        {m.key === 'bt' && `${m.steps || 200} steps${m.american ? ', American' : ''}`}
                                        {m.key === 'mc' && `${(m.n_paths || 10000).toLocaleString()} paths`}
                                        {m.key === 'bs' && 'Analytical'}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
            </div>

            {/* Parameters */}
            <div className="panel-card">
                <div className="panel-card-header">
                    <span className="panel-card-title"><ClipboardList size={14} /> Parameters</span>
                </div>
                <div className="panel-card-body">
                    {data.parameters && (
                        <div className="stats-grid">
                            {Object.entries(data.parameters).map(([k, v]) => (
                                <div className="stat-box" key={k}>
                                    <div className="stat-label">{k}</div>
                                    <div className="stat-value" style={{ fontSize: 16 }}>
                                        {typeof v === 'number' ? v.toFixed(4) : v}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            </div>
        </div>
    );
}
