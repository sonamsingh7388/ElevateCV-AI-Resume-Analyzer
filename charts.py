"""
Visualization and Chart Generator for AI Resume Analyzer.
Uses Plotly for interactive gauges, radar charts, and skill distribution plots.
"""

import plotly.graph_objects as go
import plotly.express as px
from typing import Dict, Any, List


def create_gauge_chart(score: float, title: str, color_scale: str = "indigo") -> go.Figure:
    """Creates a modern semi-circular gauge chart for scores."""
    if score >= 80:
        bar_color = "#10b981"  # Emerald
    elif score >= 65:
        bar_color = "#6366f1"  # Indigo
    elif score >= 50:
        bar_color = "#f59e0b"  # Amber
    else:
        bar_color = "#ef4444"  # Rose

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=score,
        title={'text': title, 'font': {'size': 16, 'color': '#cbd5e1'}},
        number={'suffix': "/100", 'font': {'size': 32, 'color': '#f8fafc', 'weight': 'bold'}},
        gauge={
            'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': "#475569", 'tickfont': {'color': '#94a3b8'}},
            'bar': {'color': bar_color, 'thickness': 0.75},
            'bgcolor': "rgba(30, 41, 59, 0.5)",
            'borderwidth': 0,
            'steps': [
                {'range': [0, 50], 'color': "rgba(239, 68, 68, 0.1)"},
                {'range': [50, 75], 'color': "rgba(245, 158, 11, 0.1)"},
                {'range': [75, 100], 'color': "rgba(16, 185, 129, 0.1)"}
            ],
            'threshold': {
                'line': {'color': "#ffffff", 'width': 3},
                'thickness': 0.8,
                'value': score
            }
        }
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=230,
        margin=dict(l=25, r=25, t=40, b=15),
        font=dict(family="Inter, sans-serif")
    )
    return fig


def create_radar_chart(breakdown: Dict[str, Any]) -> go.Figure:
    """Creates a 5-dimension radar chart for ATS evaluation factors."""
    categories = list(breakdown.keys())
    scores = [breakdown[cat]["score"] for cat in categories]

    # Close the radar loop
    categories_closed = categories + [categories[0]]
    scores_closed = scores + [scores[0]]

    fig = go.Figure()

    fig.add_trace(go.Scatterpolar(
        r=scores_closed,
        theta=categories_closed,
        fill='toself',
        fillcolor='rgba(99, 102, 241, 0.25)',
        line=dict(color='#818cf8', width=2),
        marker=dict(color='#6366f1', size=6),
        name="Candidate Score"
    ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color='#94a3b8', size=9),
                linecolor='rgba(255,255,255,0.1)',
                gridcolor='rgba(255,255,255,0.1)',
            ),
            angularaxis=dict(
                tickfont=dict(color='#e2e8f0', size=11),
                linecolor='rgba(255,255,255,0.1)',
                gridcolor='rgba(255,255,255,0.1)'
            ),
            bgcolor='rgba(15, 23, 42, 0.4)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False,
        height=320,
        margin=dict(l=50, r=50, t=25, b=25),
        font=dict(family="Inter, sans-serif")
    )
    return fig


def create_category_bar_chart(category_dist: Dict[str, int]) -> go.Figure:
    """Creates a horizontal bar chart displaying skill distribution across categories."""
    if not category_dist:
        return go.Figure()

    categories = list(category_dist.keys())
    counts = [category_dist[c] for c in categories]

    # Sort descending
    sorted_pairs = sorted(zip(counts, categories), reverse=False)
    counts = [p[0] for p in sorted_pairs]
    categories = [p[1] for p in sorted_pairs]

    fig = go.Figure(go.Bar(
        x=counts,
        y=categories,
        orientation='h',
        marker=dict(
            color=counts,
            colorscale=[[0, '#4f46e5'], [0.5, '#6366f1'], [1, '#38bdf8']],
            line=dict(color='rgba(255,255,255,0.1)', width=1)
        ),
        text=counts,
        textposition='outside',
        textfont=dict(color='#e2e8f0', size=11)
    ))

    fig.update_layout(
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=320,
        xaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.06)',
            tickfont=dict(color='#94a3b8'),
            zeroline=False
        ),
        yaxis=dict(
            tickfont=dict(color='#f1f5f9', size=11)
        ),
        margin=dict(l=20, r=30, t=20, b=20),
        font=dict(family="Inter, sans-serif")
    )
    return fig


def create_candidate_comparison_chart(candidates: List[Dict[str, Any]]) -> go.Figure:
    """Creates a grouped bar chart comparing multiple candidates side-by-side."""
    if not candidates:
        return go.Figure()

    names = [c["name"] for c in candidates]
    ats_scores = [c["ats_score"] for c in candidates]
    match_scores = [c["match_score"] for c in candidates]
    metrics = [c["metrics_count"] for c in candidates]

    fig = go.Figure()
    fig.add_trace(go.Bar(
        name='ATS Score',
        x=names,
        y=ats_scores,
        marker_color='#6366f1'
    ))
    fig.add_trace(go.Bar(
        name='Job Match %',
        x=names,
        y=match_scores,
        marker_color='#10b981'
    ))
    fig.add_trace(go.Bar(
        name='Metrics Count',
        x=names,
        y=metrics,
        marker_color='#38bdf8'
    ))

    fig.update_layout(
        barmode='group',
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=340,
        xaxis=dict(tickfont=dict(color='#e2e8f0')),
        yaxis=dict(
            showgrid=True,
            gridcolor='rgba(255,255,255,0.06)',
            tickfont=dict(color='#94a3b8')
        ),
        legend=dict(
            font=dict(color='#cbd5e1'),
            orientation='h',
            yanchor='bottom',
            y=1.02,
            xanchor='right',
            x=1
        ),
        margin=dict(l=20, r=20, t=30, b=20),
        font=dict(family="Inter, sans-serif")
    )
    return fig


def create_multi_radar_comparison_chart(candidates: List[Dict[str, Any]]) -> go.Figure:
    """Creates an overlaid radar chart comparing candidates across dimensions."""
    if not candidates:
        return go.Figure()

    fig = go.Figure()
    colors = ['#6366f1', '#10b981', '#f59e0b', '#ec4899', '#38bdf8']

    for i, c in enumerate(candidates[:5]):
        breakdown = c.get("breakdown", {})
        if not breakdown:
            continue
        categories = list(breakdown.keys())
        scores = [breakdown[cat]["score"] for cat in categories]

        categories_closed = categories + [categories[0]]
        scores_closed = scores + [scores[0]]
        color = colors[i % len(colors)]

        fig.add_trace(go.Scatterpolar(
            r=scores_closed,
            theta=categories_closed,
            fill='toself',
            fillcolor=f'rgba{tuple(int(color.lstrip("#")[j:j+2], 16) for j in (0, 2, 4)) + (0.15,)}',
            line=dict(color=color, width=2),
            name=c["name"]
        ))

    fig.update_layout(
        polar=dict(
            radialaxis=dict(
                visible=True,
                range=[0, 100],
                tickfont=dict(color='#94a3b8', size=9),
                gridcolor='rgba(255,255,255,0.1)'
            ),
            angularaxis=dict(
                tickfont=dict(color='#e2e8f0', size=10),
                gridcolor='rgba(255,255,255,0.1)'
            ),
            bgcolor='rgba(15, 23, 42, 0.4)'
        ),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        height=340,
        margin=dict(l=40, r=40, t=25, b=25),
        legend=dict(font=dict(color='#cbd5e1')),
        font=dict(family="Inter, sans-serif")
    )
    return fig

