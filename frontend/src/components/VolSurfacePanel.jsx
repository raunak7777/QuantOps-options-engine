import React, { useMemo } from 'react';
import { Layers } from 'lucide-react';
import Plot from 'react-plotly.js';

export default function VolSurfacePanel({ data }) {
    if (!data) {
        return (
            <div className="panel-card fade-in">
                <div className="panel-card-header">
                    <span className="panel-card-title"><Layers size={14} /> Volatility Surface</span>
                </div>
                <div className="panel-card-body">
                    <div className="empty-state">
                        <div className="empty-icon"><Layers size={32} strokeWidth={1} /></div>
                        <p>Run the engine to generate a volatility surface (strike × maturity → IV).</p>
                    </div>
                </div>
            </div>
        );
    }

    const { strikes, maturities, iv_matrix, spot } = data;

    const maturityLabels = maturities.map(t => {
        if (t < 1 / 12) return `${Math.round(t * 52)}W`;
        if (t < 1) return `${Math.round(t * 12)}M`;
        return `${t.toFixed(1)}Y`;
    });

    const surfaceTrace = {
        type: 'surface',
        x: strikes,
        y: maturities,
        z: iv_matrix,
        colorscale: [
            [0, '#0a0a2e'],
            [0.2, '#00217a'],
            [0.4, '#0050c8'],
            [0.6, '#00a8b3'],
            [0.8, '#00f0ff'],
            [1, '#ffffff'],
        ],
        opacity: 0.92,
        contours: {
            z: {
                show: true,
                usecolormap: true,
                highlightcolor: '#00f0ff',
                project: { z: false },
            },
        },
        hovertemplate:
            'Strike: $%{x:.1f}<br>Maturity: %{y:.3f}y<br>IV: %{z:.2%}<extra></extra>',
    };

    const layout = {
        autosize: true,
        height: 500,
        margin: { l: 0, r: 0, t: 30, b: 0 },
        paper_bgcolor: 'rgba(0,0,0,0)',
        plot_bgcolor: 'rgba(0,0,0,0)',
        font: {
            family: 'JetBrains Mono, monospace',
            color: '#9ca3af',
            size: 10,
        },
        scene: {
            xaxis: {
                title: 'Strike ($)',
                color: '#6b7280',
                gridcolor: 'rgba(255,255,255,0.06)',
                backgroundcolor: 'rgba(10,10,15,0.95)',
            },
            yaxis: {
                title: 'Maturity (yr)',
                color: '#6b7280',
                gridcolor: 'rgba(255,255,255,0.06)',
                backgroundcolor: 'rgba(10,10,15,0.95)',
            },
            zaxis: {
                title: 'Implied Vol',
                color: '#6b7280',
                gridcolor: 'rgba(255,255,255,0.06)',
                backgroundcolor: 'rgba(10,10,15,0.95)',
            },
            camera: {
                eye: { x: 1.5, y: -1.8, z: 0.8 },
            },
        },
    };

    return (
        <div className="fade-in">
            {/* Surface Stats */}
            <div className="stats-grid">
                <div className="stat-box">
                    <div className="stat-label">Spot Price</div>
                    <div className="stat-value cyan">${spot?.toFixed(2)}</div>
                </div>
                <div className="stat-box">
                    <div className="stat-label">Strike Range</div>
                    <div className="stat-value" style={{ fontSize: 14 }}>
                        ${strikes[0]?.toFixed(0)} – ${strikes[strikes.length - 1]?.toFixed(0)}
                    </div>
                </div>
                <div className="stat-box">
                    <div className="stat-label">Maturities</div>
                    <div className="stat-value" style={{ fontSize: 14 }}>
                        {maturityLabels.join(', ')}
                    </div>
                </div>
                <div className="stat-box">
                    <div className="stat-label">ATM IV</div>
                    <div className="stat-value green">
                        {(iv_matrix[Math.floor(maturities.length / 2)]?.[Math.floor(strikes.length / 2)] * 100)?.toFixed(1)}%
                    </div>
                </div>
            </div>

            {/* 3D Surface */}
            <div className="panel-card">
                <div className="panel-card-header">
                    <span className="panel-card-title"><Layers size={14} /> Volatility Surface — 3D</span>
                </div>
                <div className="panel-card-body">
                    <Plot
                        data={[surfaceTrace]}
                        layout={layout}
                        config={{
                            displayModeBar: true,
                            displaylogo: false,
                            responsive: true,
                        }}
                        style={{ width: '100%', height: 500 }}
                    />
                </div>
            </div>

            {/* Heatmap */}
            <div className="panel-card">
                <div className="panel-card-header">
                    <span className="panel-card-title"><Layers size={14} /> Volatility Heatmap</span>
                </div>
                <div className="panel-card-body">
                    <Plot
                        data={[{
                            type: 'heatmap',
                            x: strikes,
                            y: maturityLabels,
                            z: iv_matrix,
                            colorscale: [
                                [0, '#0a0a2e'],
                                [0.25, '#00217a'],
                                [0.5, '#0050c8'],
                                [0.75, '#00a8b3'],
                                [1, '#00f0ff'],
                            ],
                            hovertemplate:
                                'Strike: $%{x:.1f}<br>Maturity: %{y}<br>IV: %{z:.2%}<extra></extra>',
                            colorbar: {
                                title: 'IV',
                                titleside: 'right',
                                tickformat: '.0%',
                                outlinewidth: 0,
                                tickfont: { color: '#6b7280', size: 10 },
                                titlefont: { color: '#9ca3af', size: 11 },
                            },
                        }]}
                        layout={{
                            autosize: true,
                            height: 350,
                            margin: { l: 60, r: 80, t: 10, b: 40 },
                            paper_bgcolor: 'rgba(0,0,0,0)',
                            plot_bgcolor: 'rgba(0,0,0,0)',
                            font: {
                                family: 'JetBrains Mono, monospace',
                                color: '#9ca3af',
                                size: 10,
                            },
                            xaxis: { title: 'Strike ($)', gridcolor: 'rgba(255,255,255,0.04)' },
                            yaxis: { title: '', gridcolor: 'rgba(255,255,255,0.04)' },
                        }}
                        config={{ displayModeBar: false, responsive: true }}
                        style={{ width: '100%', height: 350 }}
                    />
                </div>
            </div>
        </div>
    );
}
