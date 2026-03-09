import React from 'react';
import { BrainCircuit, Target, BarChart3, Scale } from 'lucide-react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    Area, AreaChart, ResponsiveContainer, Legend,
} from 'recharts';
import colors from '../theme/colors';

export default function AIPredictionPanel({ data }) {
    if (!data) {
        return (
            <div className="panel-card fade-in">
                <div className="panel-card-header">
                    <span className="panel-card-title"><BrainCircuit size={14} /> AI Volatility Prediction</span>
                </div>
                <div className="panel-card-body">
                    <div className="empty-state">
                        <div className="empty-icon"><BrainCircuit size={32} strokeWidth={1} /></div>
                        <p>Enter a ticker and run to get AI-driven volatility forecasts and regime detection.</p>
                    </div>
                </div>
            </div>
        );
    }

    const { ensemble, individual_models } = data;
    const hmm = individual_models?.hmm;
    const regime = hmm?.current_regime || 'medium';

    // Forecast chart data
    const forecastData = ensemble?.forecast_annualized?.map((val, i) => ({
        day: i + 1,
        ensemble: (val * 100).toFixed(2),
        garch: ((individual_models?.garch?.forecast_annualized?.[i] || 0) * 100).toFixed(2),
        lstm: ((individual_models?.lstm?.forecast_annualized?.[i] || 0) * 100).toFixed(2),
        hmm_val: ((hmm?.forecast_annualized?.[i] || 0) * 100).toFixed(2),
        ci_lower: ((ensemble?.confidence_lower?.[i] || 0) * 100).toFixed(2),
        ci_upper: ((ensemble?.confidence_upper?.[i] || 0) * 100).toFixed(2),
    })) || [];

    // Regime history
    const regimeHistory = hmm?.regime_history?.map((r, i) => ({
        day: i + 1,
        regime: r,
        value: r === 'high' ? 3 : r === 'medium' ? 2 : 1,
        color: colors.regime[r],
    })) || [];

    return (
        <div className="fade-in">
            {/* Overview Stats */}
            <div className="stats-grid">
                <div className="stat-box">
                    <div className="stat-label">Current Regime</div>
                    <div style={{ display: 'flex', justifyContent: 'center', marginTop: 4 }}>
                        <span className={`regime-badge ${regime}`}>
                            <span className={`regime-dot ${regime}`} />
                            {regime} vol
                        </span>
                    </div>
                </div>
                <div className="stat-box">
                    <div className="stat-label">GARCH Vol</div>
                    <div className="stat-value cyan">
                        {((individual_models?.garch?.current_vol || 0) * 100).toFixed(1)}%
                    </div>
                    <div className="stat-sub">{individual_models?.garch?.model_type || 'GARCH'}</div>
                </div>
                <div className="stat-box">
                    <div className="stat-label">Ensemble 1D</div>
                    <div className="stat-value green">
                        {((ensemble?.forecast_annualized?.[0] || 0) * 100).toFixed(1)}%
                    </div>
                    <div className="stat-sub">annualized</div>
                </div>
                <div className="stat-box">
                    <div className="stat-label">Ensemble 10D</div>
                    <div className="stat-value purple">
                        {((ensemble?.forecast_annualized?.[Math.min(9, (ensemble?.forecast_annualized?.length || 1) - 1)] || 0) * 100).toFixed(1)}%
                    </div>
                    <div className="stat-sub">annualized</div>
                </div>
                {data.data_info?.mock_data && (
                    <div className="stat-box">
                        <div className="stat-label">Data Source</div>
                        <div className="stat-value orange" style={{ fontSize: 14 }}>Mock</div>
                        <div className="stat-sub">No API key</div>
                    </div>
                )}
            </div>

            {/* Regime Probabilities */}
            {hmm?.current_probabilities && (
                <div className="panel-card" style={{ marginBottom: 16 }}>
                    <div className="panel-card-header">
                        <span className="panel-card-title"><Target size={14} /> Regime Probabilities</span>
                    </div>
                    <div className="panel-card-body">
                        <div style={{ display: 'flex', gap: 16, flexWrap: 'wrap' }}>
                            {Object.entries(hmm.current_probabilities).map(([state, prob]) => (
                                <div key={state} style={{ flex: 1, minWidth: 120 }}>
                                    <div style={{
                                        display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                                        marginBottom: 4,
                                    }}>
                                        <span style={{ fontSize: 11, color: colors.regime[state] || 'var(--text-secondary)', textTransform: 'capitalize' }}>
                                            {state}
                                        </span>
                                        <span style={{ fontSize: 11, color: 'var(--text-secondary)' }}>
                                            {(prob * 100).toFixed(1)}%
                                        </span>
                                    </div>
                                    <div style={{
                                        height: 4, borderRadius: 2,
                                        background: 'var(--bg-tertiary)', overflow: 'hidden',
                                    }}>
                                        <div style={{
                                            height: '100%', borderRadius: 2,
                                            width: `${prob * 100}%`,
                                            background: colors.regime[state] || 'var(--accent-cyan)',
                                            boxShadow: `0 0 8px ${colors.regime[state] || 'var(--accent-cyan)'}`,
                                            transition: 'width 0.5s ease',
                                        }} />
                                    </div>
                                    {hmm.state_volatilities?.[state] && (
                                        <div style={{ fontSize: 10, color: 'var(--text-muted)', marginTop: 2 }}>
                                            σ = {(hmm.state_volatilities[state] * 100).toFixed(1)}%
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            <div className="two-col">
                {/* Ensemble Forecast Chart */}
                <div className="panel-card">
                    <div className="panel-card-header">
                        <span className="panel-card-title"><BrainCircuit size={14} /> Volatility Forecast</span>
                    </div>
                    <div className="panel-card-body">
                        <div className="chart-container tall">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={forecastData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                                    <XAxis
                                        dataKey="day"
                                        stroke="var(--text-muted)"
                                        fontSize={10}
                                        label={{ value: 'Days Ahead', position: 'bottom', fill: 'var(--text-muted)', fontSize: 10 }}
                                    />
                                    <YAxis
                                        stroke="var(--text-muted)"
                                        fontSize={10}
                                        tickFormatter={v => `${v}%`}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            background: 'var(--bg-card)',
                                            border: '1px solid var(--border-glow)',
                                            borderRadius: 6,
                                            fontFamily: 'var(--font-mono)',
                                            fontSize: 11,
                                        }}
                                        formatter={(v) => [`${v}%`]}
                                        labelFormatter={v => `Day ${v}`}
                                    />
                                    <Legend />
                                    <Area
                                        type="monotone"
                                        dataKey="ci_upper"
                                        stroke="none"
                                        fill="rgba(0, 240, 255, 0.08)"
                                        name="CI Upper"
                                    />
                                    <Area
                                        type="monotone"
                                        dataKey="ci_lower"
                                        stroke="none"
                                        fill="var(--bg-card)"
                                        name="CI Lower"
                                    />
                                    <Line type="monotone" dataKey="ensemble" stroke="#00f0ff" strokeWidth={2.5} dot={false} name="Ensemble" />
                                    <Line type="monotone" dataKey="garch" stroke="#00ff88" strokeWidth={1.5} strokeDasharray="4 4" dot={false} name="GARCH" />
                                    <Line type="monotone" dataKey="lstm" stroke="#a855f7" strokeWidth={1.5} strokeDasharray="4 4" dot={false} name="LSTM" />
                                    <Line type="monotone" dataKey="hmm_val" stroke="#ff9500" strokeWidth={1.5} strokeDasharray="4 4" dot={false} name="HMM" />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Regime History */}
                <div className="panel-card">
                    <div className="panel-card-header">
                        <span className="panel-card-title"><BarChart3 size={14} /> Regime History (60D)</span>
                    </div>
                    <div className="panel-card-body">
                        <div className="chart-container tall">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={regimeHistory}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                                    <XAxis
                                        dataKey="day"
                                        stroke="var(--text-muted)"
                                        fontSize={10}
                                    />
                                    <YAxis
                                        stroke="var(--text-muted)"
                                        fontSize={10}
                                        domain={[0, 4]}
                                        ticks={[1, 2, 3]}
                                        tickFormatter={v => v === 1 ? 'Low' : v === 2 ? 'Med' : 'High'}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            background: 'var(--bg-card)',
                                            border: '1px solid var(--border-glow)',
                                            borderRadius: 6,
                                            fontFamily: 'var(--font-mono)',
                                            fontSize: 11,
                                        }}
                                        formatter={(v, name) => [v === 1 ? 'Low' : v === 2 ? 'Medium' : 'High', 'Regime']}
                                        labelFormatter={v => `Day ${v}`}
                                    />
                                    <Area
                                        type="stepAfter"
                                        dataKey="value"
                                        stroke="#00a8b3"
                                        fill="rgba(0, 240, 255, 0.1)"
                                        strokeWidth={2}
                                        name="Regime"
                                    />
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            </div>

            {/* Model Weights */}
            {data.weights && data.weights.length > 0 && (
                <div className="panel-card">
                    <div className="panel-card-header">
                        <span className="panel-card-title"><Scale size={14} /> Ensemble Weights</span>
                    </div>
                    <div className="panel-card-body">
                        <table className="comparison-table">
                            <thead>
                                <tr>
                                    <th>Day</th>
                                    <th>GARCH</th>
                                    <th>LSTM</th>
                                    <th>HMM</th>
                                </tr>
                            </thead>
                            <tbody>
                                {data.weights.filter((_, i) => i % Math.max(1, Math.floor(data.weights.length / 5)) === 0).map((w, i) => (
                                    <tr key={i}>
                                        <td>Day {i * Math.max(1, Math.floor(data.weights.length / 5)) + 1}</td>
                                        <td style={{ color: colors.accent.green }}>{(w.garch * 100).toFixed(1)}%</td>
                                        <td style={{ color: colors.accent.purple }}>{(w.lstm * 100).toFixed(1)}%</td>
                                        <td style={{ color: colors.accent.orange }}>{(w.hmm * 100).toFixed(1)}%</td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            )}
        </div>
    );
}
