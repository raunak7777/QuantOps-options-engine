import React, { useMemo } from 'react';
import { Dice5, BarChart3 } from 'lucide-react';
import {
    LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip,
    BarChart, Bar, ResponsiveContainer, Cell,
} from 'recharts';
import colors from '../theme/colors';

export default function MonteCarloPanel({ data }) {
    if (!data) {
        return (
            <div className="panel-card fade-in">
                <div className="panel-card-header">
                    <span className="panel-card-title"><Dice5 size={14} /> Monte Carlo Simulation</span>
                </div>
                <div className="panel-card-body">
                    <div className="empty-state">
                        <div className="empty-icon"><Dice5 size={32} strokeWidth={1} /></div>
                        <p>Run the engine to simulate price paths and payoff distributions.</p>
                    </div>
                </div>
            </div>
        );
    }

    const pathsData = useMemo(() => {
        if (!data.paths || data.paths.length === 0) return [];
        const numSteps = data.paths[0].length;
        const step = Math.max(1, Math.floor(numSteps / 100));
        const indices = [];
        for (let i = 0; i < numSteps; i += step) indices.push(i);
        if (indices[indices.length - 1] !== numSteps - 1) indices.push(numSteps - 1);

        return indices.map(idx => {
            const point = { step: idx };
            const maxPaths = Math.min(50, data.paths.length);
            for (let p = 0; p < maxPaths; p++) {
                point[`p${p}`] = data.paths[p][idx];
            }
            return point;
        });
    }, [data.paths]);

    const histData = useMemo(() => {
        if (!data.payoff_distribution?.histogram) return [];
        const { counts, bin_edges } = data.payoff_distribution.histogram;
        const maxCount = Math.max(...counts);
        return counts.map((c, i) => ({
            range: `$${bin_edges[i].toFixed(1)}`,
            count: c,
            intensity: c / maxCount,
        }));
    }, [data.payoff_distribution]);

    const numVizPaths = Math.min(50, data.paths?.length || 0);

    return (
        <div className="fade-in">
            {/* Stats */}
            <div className="stats-grid">
                <div className="stat-box">
                    <div className="stat-label">MC Price</div>
                    <div className="stat-value purple">${data.price?.toFixed(4)}</div>
                    <div className="stat-sub">SE: ±{data.std_error?.toFixed(4)}</div>
                </div>
                <div className="stat-box">
                    <div className="stat-label">95% CI</div>
                    <div className="stat-value" style={{ fontSize: 14 }}>
                        [{data.confidence_interval_95?.[0]?.toFixed(3)}, {data.confidence_interval_95?.[1]?.toFixed(3)}]
                    </div>
                </div>
                <div className="stat-box">
                    <div className="stat-label">Paths</div>
                    <div className="stat-value cyan">{(data.n_paths || 0).toLocaleString()}</div>
                </div>
                <div className="stat-box">
                    <div className="stat-label">Mean Payoff</div>
                    <div className="stat-value green">${data.payoff_distribution?.mean?.toFixed(4)}</div>
                </div>
                <div className="stat-box">
                    <div className="stat-label">Median</div>
                    <div className="stat-value orange">${data.payoff_distribution?.percentiles?.['50']?.toFixed(4)}</div>
                </div>
                <div className="stat-box">
                    <div className="stat-label">95th Pctl</div>
                    <div className="stat-value red">${data.payoff_distribution?.percentiles?.['95']?.toFixed(4)}</div>
                </div>
            </div>

            <div className="two-col">
                {/* Price Paths */}
                <div className="panel-card">
                    <div className="panel-card-header">
                        <span className="panel-card-title"><Dice5 size={14} /> Simulated Price Paths</span>
                        <span style={{ fontSize: 10, color: 'var(--text-muted)' }}>{numVizPaths} paths shown</span>
                    </div>
                    <div className="panel-card-body">
                        <div className="chart-container tall">
                            <ResponsiveContainer width="100%" height="100%">
                                <LineChart data={pathsData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                                    <XAxis
                                        dataKey="step"
                                        stroke="var(--text-muted)"
                                        fontSize={10}
                                        label={{ value: 'Time Step', position: 'bottom', fill: 'var(--text-muted)', fontSize: 10 }}
                                    />
                                    <YAxis
                                        stroke="var(--text-muted)"
                                        fontSize={10}
                                        tickFormatter={v => `$${v.toFixed(0)}`}
                                    />
                                    <Tooltip
                                        contentStyle={{
                                            background: 'var(--bg-card)',
                                            border: '1px solid var(--border-glow)',
                                            borderRadius: 6,
                                            fontFamily: 'var(--font-mono)',
                                            fontSize: 11,
                                        }}
                                    />
                                    {Array.from({ length: numVizPaths }, (_, i) => (
                                        <Line
                                            key={`p${i}`}
                                            type="monotone"
                                            dataKey={`p${i}`}
                                            stroke={`hsla(${180 + (i * 3.6)}, 80%, 60%, 0.35)`}
                                            strokeWidth={1}
                                            dot={false}
                                            isAnimationActive={false}
                                        />
                                    ))}
                                </LineChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Payoff Histogram */}
                <div className="panel-card">
                    <div className="panel-card-header">
                        <span className="panel-card-title"><BarChart3 size={14} /> Payoff Distribution</span>
                    </div>
                    <div className="panel-card-body">
                        <div className="chart-container tall">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={histData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
                                    <XAxis
                                        dataKey="range"
                                        stroke="var(--text-muted)"
                                        fontSize={9}
                                        interval="preserveStartEnd"
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
                                    />
                                    <Bar dataKey="count" radius={[2, 2, 0, 0]}>
                                        {histData.map((entry, i) => (
                                            <Cell
                                                key={i}
                                                fill={`rgba(168, 85, 247, ${0.3 + entry.intensity * 0.7})`}
                                            />
                                        ))}
                                    </Bar>
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
}
