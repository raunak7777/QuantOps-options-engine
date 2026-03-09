import React, { useState } from 'react';
import { Activity } from 'lucide-react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    ResponsiveContainer, Legend
} from 'recharts';
import colors from '../theme/colors';

const GREEK_COLORS = {
    delta: colors.chart.line1,
    gamma: colors.chart.line2,
    theta: colors.chart.line4,
    vega: colors.chart.line3,
    rho: colors.chart.line5,
};

export default function GreeksPanel({ data }) {
    const [activeGreeks, setActiveGreeks] = useState(['delta', 'gamma']);

    if (!data) {
        return (
            <div className="panel-card fade-in">
                <div className="panel-card-header">
                    <span className="panel-card-title"><Activity size={14} /> Greeks Calculator</span>
                </div>
                <div className="panel-card-body">
                    <div className="empty-state">
                        <div className="empty-icon"><Activity size={32} strokeWidth={1} /></div>
                        <p>Run the engine to compute option sensitivities.</p>
                    </div>
                </div>
            </div>
        );
    }

    const chartData = data.chart_data
        ? data.chart_data.spot_prices.map((s, i) => ({
            spot: parseFloat(s.toFixed(2)),
            delta: data.chart_data.delta[i],
            gamma: data.chart_data.gamma[i],
            theta: data.chart_data.theta[i],
            vega: data.chart_data.vega[i],
            rho: data.chart_data.rho[i],
        }))
        : [];

    const toggleGreek = (g) => {
        setActiveGreeks(prev =>
            prev.includes(g) ? prev.filter(x => x !== g) : [...prev, g]
        );
    };

    return (
        <div className="fade-in">
            {/* Values */}
            <div className="stats-grid">
                {data.analytical && Object.entries(data.analytical).map(([key, val]) => (
                    <div className="stat-box" key={key}>
                        <div className="stat-label">{key}</div>
                        <div className="stat-value" style={{ color: GREEK_COLORS[key], fontSize: 18 }}>
                            {val.toFixed(6)}
                        </div>
                        {data.numerical && (
                            <div className="stat-sub">
                                Num: {data.numerical[key]?.toFixed(6)}
                            </div>
                        )}
                    </div>
                ))}
            </div>

            {/* Toggle buttons */}
            <div style={{ display: 'flex', gap: 6, marginBottom: 12, flexWrap: 'wrap' }}>
                {['delta', 'gamma', 'theta', 'vega', 'rho'].map(g => (
                    <button
                        key={g}
                        onClick={() => toggleGreek(g)}
                        style={{
                            padding: '4px 12px',
                            borderRadius: 4,
                            border: `1px solid ${activeGreeks.includes(g) ? GREEK_COLORS[g] : 'var(--border-subtle)'}`,
                            background: activeGreeks.includes(g) ? `${GREEK_COLORS[g]}15` : 'transparent',
                            color: activeGreeks.includes(g) ? GREEK_COLORS[g] : 'var(--text-muted)',
                            fontFamily: 'var(--font-mono)',
                            fontSize: 11,
                            cursor: 'pointer',
                            textTransform: 'capitalize',
                            transition: 'all 0.15s ease',
                        }}
                    >
                        {g}
                    </button>
                ))}
            </div>

            {/* Chart */}
            <div className="panel-card">
                <div className="panel-card-header">
                    <span className="panel-card-title"><Activity size={14} /> Greeks vs Spot Price</span>
                </div>
                <div className="panel-card-body">
                    <div className="chart-container tall">
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={chartData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                                <XAxis
                                    dataKey="spot"
                                    stroke="var(--text-muted)"
                                    fontSize={10}
                                    tickFormatter={v => `$${v}`}
                                />
                                <YAxis stroke="var(--text-muted)" fontSize={10} />
                                <Tooltip
                                    contentStyle={{
                                        background: 'var(--bg-card)',
                                        border: '1px solid var(--border-glow)',
                                        borderRadius: 6,
                                        fontFamily: 'var(--font-mono)',
                                        fontSize: 11,
                                    }}
                                    labelFormatter={v => `Spot: $${v}`}
                                />
                                <Legend />
                                {activeGreeks.map(g => (
                                    <Line
                                        key={g}
                                        type="monotone"
                                        dataKey={g}
                                        stroke={GREEK_COLORS[g]}
                                        strokeWidth={2}
                                        dot={false}
                                        name={g.charAt(0).toUpperCase() + g.slice(1)}
                                    />
                                ))}
                            </LineChart>
                        </ResponsiveContainer>
                    </div>
                </div>
            </div>
        </div>
    );
}
