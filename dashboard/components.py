import os
import sys

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import networkx as nx
import plotly.graph_objects as go
import plotly.express as px
import streamlit as st
from typing import List, Dict, Any

from dashboard.utils import RISK_COLORS, THEME_COLORS, format_currency_inr


def render_metric_card(
    title: str,
    value: str,
    subtitle: str = "",
    delta: str = None,
    color: str = "#00D9FF",
    icon_type: str = "risk",
):
    """
    Renders top KPI card matching pixel-close prototype design with icon badge and dark glowing panel.
    """
    icon_svgs = {
        "risk": f"""<div style="background: rgba(255, 59, 79, 0.15); border: 1px solid #FF3B4F; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; color: #FF3B4F;">⚠️</div>""",
        "loss": f"""<div style="background: rgba(255, 138, 0, 0.15); border: 1px solid #FF8A00; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; color: #FF8A00;">📉</div>""",
        "purple": f"""<div style="background: rgba(156, 85, 255, 0.15); border: 1px solid #9C55FF; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; color: #9C55FF;">📊</div>""",
        "potential": f"""<div style="background: rgba(22, 199, 132, 0.15); border: 1px solid #16C784; border-radius: 50%; width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; font-size: 1.3rem; color: #16C784;">🛡️</div>""",
    }

    icon_html = icon_svgs.get(icon_type, icon_svgs["risk"])
    subtitle_html = f'<div style="color: #94A8C2; font-size: 0.72rem; margin-top: 2px;">{subtitle}</div>' if subtitle else ''

    card_html = f"""<div style="background: #0A1422; border: 1px solid #12365B; border-top: 2px solid {color}; border-radius: 8px; padding: 14px 16px; display: flex; align-items: center; gap: 14px; box-shadow: 0 4px 14px rgba(0, 0, 0, 0.5);">{icon_html}<div><div style="color: #94A8C2; font-size: 0.75rem; font-weight: 600; text-transform: uppercase; letter-spacing: 0.5px;">{title}</div><div style="color: {color}; font-size: 1.7rem; font-weight: 800; margin: 2px 0 0 0; font-family: monospace; letter-spacing: -0.5px;">{value}</div>{subtitle_html}</div></div>"""
    st.markdown(card_html, unsafe_allow_html=True)


def render_digital_twin_graph(graph_data: Dict[str, List[Dict[str, Any]]], height: int = 340, curated_only: bool = True) -> go.Figure:
    """
    Renders Digital Twin graph with deterministic hierarchical positioning.
    On Overview (curated_only=True), filters to a clean attack-relevant subset (8-10 nodes).
    """
    nodes = graph_data.get("nodes", [])
    edges = graph_data.get("edges", [])

    if not nodes:
        fig = go.Figure()
        fig.update_layout(title="No Graph Data Available")
        return fig

    # Filter for Overview curated view
    if curated_only:
        target_names = [
            "Internet",
            "Mobile-Banking-API-01",
            "Auth-Service-01",
            "Customer-DB-01",
            "Payment-Gateway-01",
            "Transaction-API-01",
            "Payment-DB-01",
            "Core-Banking-Service-01",
        ]
        curated_nodes = [n for n in nodes if any(t.lower() in n.get("name", "").lower() or t.lower() in n.get("id", "").lower() for t in target_names)]
        if not curated_nodes:
            curated_nodes = nodes[:8]
        curated_ids = {n["id"] for n in curated_nodes}
        curated_edges = [e for e in edges if e["source"] in curated_ids and e["target"] in curated_ids]
        nodes = curated_nodes
        edges = curated_edges

    # Build NetworkX graph
    G = nx.DiGraph()
    for n in nodes:
        G.add_node(n["id"], **n)
    for e in edges:
        G.add_edge(e["source"], e["target"], **e)

    # Deterministic Column-based Hierarchical Layout
    pos = {}
    col_counters = {0: 0, 1: 0, 2: 0, 3: 0}

    for n_id in G.nodes():
        attrs = G.nodes[n_id]
        n_type = str(attrs.get("type", "")).lower()
        n_name = str(attrs.get("name", n_id)).lower()
        is_exposed = bool(attrs.get("internet_exposed", False))
        asset_type = str(attrs.get("asset_type", "")).lower()

        if n_type == "internet" or "internet" in n_name:
            col = 0
        elif is_exposed or "gateway" in n_name or "api" in n_name:
            col = 1
        elif "db" in n_name or "database" in asset_type:
            col = 3
        else:
            col = 2

        idx = col_counters[col]
        col_counters[col] += 1
        x = col * 1.8
        y = -idx * 1.2
        pos[n_id] = (x, y)

    # Center columns vertically
    for col in range(4):
        count = col_counters[col]
        if count > 1:
            shift = (count - 1) * 0.6
            for n_id in pos:
                x, y = pos[n_id]
                col_id = int(round(x / 1.8))
                if col_id == col:
                    pos[n_id] = (x, y + shift)

    edge_x, edge_y = [], []
    for edge in G.edges():
        x0, y0 = pos[edge[0]]
        x1, y1 = pos[edge[1]]
        edge_x.extend([x0, x1, None])
        edge_y.extend([y0, y1, None])

    edge_trace = go.Scatter(
        x=edge_x,
        y=edge_y,
        line=dict(width=1.5, color="#12365B"),
        hoverinfo="none",
        mode="lines",
    )

    node_x, node_y, node_colors, node_hover, node_labels, node_sizes = [], [], [], [], [], []
    for n_id in G.nodes():
        x, y = pos[n_id]
        attrs = G.nodes[n_id]
        n_name = attrs.get("name", str(n_id))
        n_type = str(attrs.get("type", "")).lower()
        crit = str(attrs.get("criticality", "Low"))
        risk_score = attrs.get("risk_score", 0.0)

        if n_type == "internet":
            color = "#00D9FF"
            size = 28
        elif crit == "Critical":
            color = "#FF3B4F"
            size = 24
        elif crit == "High":
            color = "#FF8A00"
            size = 22
        elif crit == "Medium":
            color = "#FFC400"
            size = 20
        else:
            color = "#16C784"
            size = 18

        node_x.append(x)
        node_y.append(y)
        node_colors.append(color)
        node_sizes.append(size)
        disp_name = n_name.replace("-Service-01", "").replace("-01", "")
        node_labels.append(disp_name)
        node_hover.append(f"<b>{n_name}</b><br>Type: {n_type}<br>Criticality: {crit}<br>Risk Score: {risk_score:.1f}")

    node_trace = go.Scatter(
        x=node_x,
        y=node_y,
        mode="markers+text",
        hoverinfo="text",
        text=node_labels,
        textposition="bottom center",
        textfont=dict(color="#F3F7FF", size=9, family="sans-serif"),
        hovertext=node_hover,
        marker=dict(
            size=node_sizes,
            color=node_colors,
            line=dict(width=2, color="#07111F"),
        ),
    )

    fig = go.Figure(data=[edge_trace, node_trace])
    fig.update_layout(
        title=dict(text="<b>CYBER DIGITAL TWIN TOPOLOGY</b>", font=dict(color="#F3F7FF", size=13)),
        showlegend=False,
        hovermode="closest",
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,20,34,0.4)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        margin=dict(l=10, r=10, t=35, b=10),
        height=height,
    )
    return fig


def render_attack_path_flow(top_path: Dict[str, Any]) -> str:
    path_nodes = top_path.get("path", ["Internet Exposure", "Mobile-Banking-API-01", "Auth-Service-01", "Customer-DB-01"])
    path_score = top_path.get("path_score", 79.5)
    financial_exp = top_path.get("potential_financial_exposure", 47700000.0)
    weak_points = top_path.get("weakest_points", ["Unpatched CVE-2026-DEMO-001 on API", "Weak MFA configuration"])

    step_htmls = []
    total_hops = len(path_nodes)
    for idx, node in enumerate(path_nodes):
        node_clean = node.replace("-01", "")
        hop_num = f"Hop {idx+1}"
        if idx == 0:
            border_color = "#00D9FF"
            badge = '<span style="background: rgba(0, 217, 255, 0.2); color: #00D9FF; border: 1px solid #00D9FF; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 700;">ENTRY</span>'
        elif idx == total_hops - 1:
            border_color = "#FF3B4F"
            badge = '<span style="background: rgba(255, 59, 79, 0.2); color: #FF3B4F; border: 1px solid #FF3B4F; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 700;">TARGET DB</span>'
        else:
            border_color = "#FF8A00"
            badge = '<span style="background: rgba(255, 138, 0, 0.2); color: #FF8A00; border: 1px solid #FF8A00; padding: 2px 6px; border-radius: 4px; font-size: 0.65rem; font-weight: 700;">PIVOT</span>'

        arrow = '<div style="color: #00D9FF; text-align: center; font-size: 0.85rem; margin: 1px 0; font-weight: bold;">↓</div>' if idx < total_hops - 1 else ''
        step_htmls.append(f'<div style="background: #07111F; border: 1px solid {border_color}; border-radius: 6px; padding: 6px 10px; display: flex; justify-content: space-between; align-items: center;"><div style="display: flex; align-items: center; gap: 8px;"><span style="color: #94A8C2; font-size: 0.68rem; font-weight: 700; font-family: monospace;">[{hop_num}]</span><span style="color: #F3F7FF; font-size: 0.8rem; font-weight: 700;">{node_clean}</span></div>{badge}</div>{arrow}')

    weak_items_html = "".join([f'<li style="color: #94A8C2; font-size: 0.72rem;">{wp}</li>' for wp in weak_points[:2]])

    return f'<div style="background: #0A1422; border: 1px solid #12365B; border-radius: 8px; padding: 10px 12px;"><div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 8px;"><span style="color: #F3F7FF; font-size: 0.85rem; font-weight: 700;">TOP CRITICAL ATTACK PATH</span><span style="background: rgba(255, 59, 79, 0.2); color: #FF3B4F; border: 1px solid #FF3B4F; border-radius: 4px; padding: 2px 8px; font-size: 0.72rem; font-weight: 800;">Risk Score: {path_score:.1f}</span></div><div>{"".join(step_htmls)}</div><div style="margin-top: 8px; background: #030913; border: 1px solid #12365B; border-radius: 6px; padding: 6px 10px;"><div style="color: #FF8A00; font-size: 0.72rem; font-weight: 700;">Potential Exposure: {format_currency_inr(financial_exp)}</div><div style="color: #F3F7FF; font-size: 0.70rem; font-weight: 700; margin-top: 2px;">Key Weaknesses:</div><ul style="margin: 2px 0 0 14px; padding: 0;">{weak_items_html}</ul></div></div>'



def get_short_asset_name(name: str) -> str:
    short_map = {
        "Mobile-Banking-API-01": "Mobile API",
        "Payment-Gateway-01": "Payment GW",
        "Customer-DB-01": "Customer DB",
        "Auth-Service-01": "Auth Service",
        "SIEM-Server-01": "SIEM",
        "SOC-Monitoring-01": "SOC Monitor",
        "Core-Banking-Service-01": "Core Banking",
        "Transaction-API-01": "Transaction API",
        "Payment-DB-01": "Payment DB",
    }
    if name in short_map:
        return short_map[name]
    return name.replace("-Service-01", "").replace("-API-01", " API").replace("-DB-01", " DB").replace("-01", "")


def render_risk_heatmap(asset_risks: List[Dict[str, Any]], height: int = 340) -> go.Figure:
    heatmap_z = [
        [10, 20, 40, 60, 80],
        [20, 35, 55, 75, 90],
        [30, 50, 70, 85, 95],
        [40, 65, 80, 90, 98],
        [50, 75, 90, 96, 100]
    ]

    axis_categories = ['Very Low', 'Low', 'Medium', 'High', 'Very High']

    fig = go.Figure()
    fig.add_trace(go.Heatmap(
        z=heatmap_z,
        x=axis_categories,
        y=axis_categories,
        colorscale=[
            [0.0, 'rgba(22, 199, 132, 0.35)'],
            [0.35, 'rgba(255, 196, 0, 0.40)'],
            [0.65, 'rgba(255, 138, 0, 0.50)'],
            [1.0, 'rgba(255, 59, 79, 0.65)']
        ],
        showscale=False,
        hoverinfo='none',
    ))

    # Identify top 5 priority assets to show text labels on graph to avoid clutter
    priority_sorted = sorted(
        asset_risks,
        key=lambda x: (
            1 if str(x.get("criticality")).lower() == "critical" else 0,
            x.get("estimated_financial_exposure", 0.0),
            x.get("risk_score", 0.0)
        ),
        reverse=True
    )
    labeled_asset_ids = {a.get("asset_id") for a in priority_sorted[:5]}

    # Overlay Asset Scatter Points
    x_pts, y_pts, hover_texts, sizes, text_labels = [], [], [], [], []
    for a in asset_risks:
        lh = a.get("overall_likelihood", 0.3)
        crit_str = str(a.get("criticality", "Low")).lower()

        if crit_str == "critical":
            imp_idx = 4
        elif crit_str == "high":
            imp_idx = 3
        elif crit_str in ("medium", "moderate"):
            imp_idx = 2
        else:
            imp_idx = 1

        lh_idx = min(max(int(lh * 5), 0), 4)

        x_pts.append(lh_idx)
        y_pts.append(imp_idx)

        exp_val = a.get("estimated_financial_exposure", 0.0)
        # Clamped bubble size (12px min to 28px max)
        size = min(max(int(exp_val / 350000.0) + 12, 12), 28)
        sizes.append(size)

        # Show label only for top priority assets to prevent label overlap
        if a.get("asset_id") in labeled_asset_ids:
            text_labels.append(get_short_asset_name(a["asset_name"]))
        else:
            text_labels.append("")

        # Detailed Hover Tooltip
        hover_text = (
            f"<b>{a['asset_name']}</b><br>"
            f"Risk Score: <b>{a.get('risk_score', 0.0):.1f} / 100</b> ({a.get('risk_level', 'Low')})<br>"
            f"Business Impact: {a.get('criticality', 'Low')}<br>"
            f"Likelihood: {a.get('overall_likelihood', 0.0):.2f}<br>"
            f"Financial Exposure: <b>{format_currency_inr(exp_val)}</b>"
        )
        hover_texts.append(hover_text)

    fig.add_trace(go.Scatter(
        x=x_pts,
        y=y_pts,
        mode='markers+text',
        text=text_labels,
        textposition='top center',
        textfont=dict(color='#F3F7FF', size=10, family='sans-serif'),
        hovertext=hover_texts,
        hoverinfo='text',
        marker=dict(
            size=sizes,
            color='#00D9FF',
            line=dict(color='#07111F', width=1.5),
            opacity=0.9,
        )
    ))

    fig.update_layout(
        title=dict(text="<b>ENTERPRISE RISK HEATMAP</b>", font=dict(color="#F3F7FF", size=13)),
        xaxis=dict(title=dict(text="Likelihood", font=dict(color="#94A8C2", size=10)), tickfont=dict(color="#94A8C2")),
        yaxis=dict(title=dict(text="Business Impact", font=dict(color="#94A8C2", size=10)), tickfont=dict(color="#94A8C2")),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        margin=dict(l=35, r=15, t=35, b=35),
        height=height,
        showlegend=False,
    )
    return fig



def render_optimizer_donut(opt_res: Dict[str, Any]) -> go.Figure:
    invested = opt_res.get("total_investment", 4200000.0)
    remaining = opt_res.get("remaining_budget", 800000.0)

    fig = go.Figure(data=[go.Pie(
        labels=["Allocated", "Unallocated"],
        values=[invested, remaining],
        hole=0.6,
        marker=dict(colors=["#00D9FF", "#12365B"], line=dict(color="#0A1422", width=2)),
        textinfo="none",
        hoverinfo="label+value",
    )])

    fig.update_layout(
        showlegend=False,
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(0,0,0,0)",
        margin=dict(l=10, r=10, t=10, b=10),
        height=130,
        annotations=[dict(text="₹50L Budget", x=0.5, y=0.5, font=dict(color="#F3F7FF", size=10, weight="bold"), showarrow=False)]
    )
    return fig


def render_what_if_chart(sim_res: Dict[str, Any]) -> go.Figure:
    curr_score = sim_res.get("current_risk_score", 68.0) if sim_res else 68.0
    sim_score = sim_res.get("simulated_risk_score", 32.0) if sim_res else 32.0

    steps = ["Current", "MFA Implemented", "EDR Deployed", "Patch Applied", "Simulated Target"]
    scores = [curr_score, curr_score - 10, curr_score - 20, curr_score - 28, sim_score]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=steps,
        y=scores,
        mode="lines+markers",
        line=dict(color="#00D9FF", width=2.5, shape="spline"),
        marker=dict(size=7, color=["#FF3B4F", "#FF8A00", "#FFC400", "#16C784", "#16C784"]),
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,20,34,0.4)",
        xaxis=dict(showgrid=False, tickfont=dict(color="#94A8C2", size=8)),
        yaxis=dict(showgrid=True, gridcolor="#12365B", range=[0, 100], tickfont=dict(color="#94A8C2", size=8)),
        margin=dict(l=20, r=15, t=15, b=25),
        height=115,
    )
    return fig


def generate_deterministic_alerts(asset_risks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    alerts = []
    for a in asset_risks:
        if a.get("risk_score", 0) >= 60.0:
            alerts.append({
                "level": "CRITICAL",
                "color": "#FF3B4F",
                "title": f"High Exposure Asset: {a['asset_name']}",
                "detail": f"Risk score {a['risk_score']:.1f} / 100 with financial exposure of {format_currency_inr(a['estimated_financial_exposure'])}"
            })
        elif a.get("internet_exposed") and a.get("risk_score", 0) >= 40.0:
            alerts.append({
                "level": "HIGH",
                "color": "#FF8A00",
                "title": f"Exposed Pivot Target: {a['asset_name']}",
                "detail": "Directly exposed to public internet with active vulnerabilities."
            })
    if not alerts:
        alerts.append({
            "level": "INFO",
            "color": "#00D9FF",
            "title": "All Monitored Assets Stable",
            "detail": "No immediate critical alerts triggered."
        })
    return alerts[:3]


def render_attack_path_diagram(top_path: Dict[str, Any]) -> go.Figure:
    path_nodes = top_path.get("path", ["Internet", "Mobile-Banking-API-01", "Auth-Service-01", "Customer-DB-01"])
    n_count = len(path_nodes)

    x_vals = [i * 2.0 for i in range(n_count)]
    y_vals = [0] * n_count

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="lines",
        line=dict(color="#FF3B4F", width=3, dash="dash"),
        hoverinfo="none",
    ))

    node_colors = ["#00D9FF"] + ["#FF8A00"] * (n_count - 2) + ["#FF3B4F"]
    fig.add_trace(go.Scatter(
        x=x_vals,
        y=y_vals,
        mode="markers+text",
        text=path_nodes,
        textposition="top center",
        textfont=dict(color="#F3F7FF", size=10, family="sans-serif"),
        marker=dict(size=22, color=node_colors, line=dict(color="#0A1422", width=2)),
        hoverinfo="text",
        hovertext=[f"Step {i+1}: {name}" for i, name in enumerate(path_nodes)],
    ))

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor="rgba(10,20,34,0.4)",
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-0.5, 0.8]),
        margin=dict(l=20, r=20, t=30, b=10),
        height=180,
    )
    return fig


def render_risk_bar_chart(asset_risks: List[Dict[str, Any]]) -> go.Figure:
    sorted_assets = sorted(asset_risks, key=lambda x: x["estimated_financial_exposure"], reverse=True)
    names = [a["asset_name"] for a in sorted_assets]
    exposures = [a["estimated_financial_exposure"] for a in sorted_assets]
    colors = [RISK_COLORS.get(a["risk_level"], "#00D9FF") for a in sorted_assets]

    fig = go.Figure(data=[go.Bar(
        x=names,
        y=exposures,
        marker=dict(color=colors, line=dict(color='#07111F', width=1)),
        hovertemplate='<b>%{x}</b><br>Exposure: ₹%{y:,.0f}<extra></extra>'
    )])

    fig.update_layout(
        title=dict(text="<b>Top Financial Exposure by Asset</b>", font=dict(color="#F3F7FF", size=14)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10,20,34,0.6)',
        xaxis=dict(tickfont=dict(color='#F3F7FF', size=10), tickangle=-30),
        yaxis=dict(title="Exposure (INR)", gridcolor='#12365B', tickfont=dict(color='#94A8C2')),
        margin=dict(l=20, r=20, t=35, b=50),
        height=380,
    )
    return fig


def render_exploit_probability_chart(threats: List[Dict[str, Any]], height: int = 340) -> go.Figure:
    """
    Renders a Plotly horizontal bar chart of top ML predicted exploit probabilities.
    Maps probabilities to Green (0-25%), Yellow (25-50%), Orange (50-75%), and Red (75-100%).
    """
    if not threats:
        fig = go.Figure()
        fig.update_layout(title="No Threat Predictions Available")
        return fig

    # Reverse list so highest probability is at the top of horizontal bar chart
    sorted_threats = sorted(threats, key=lambda x: x.get("exploitation_probability", 0.0))

    labels = [f"{t.get('cve_id')} ({t.get('asset', 'Unknown').replace('-Service-01', '').replace('-01', '')})" for t in sorted_threats]
    pcts = [t.get("percentage", round(t.get("exploitation_probability", 0.0) * 100, 1)) for t in sorted_threats]

    colors = []
    for p in pcts:
        if p <= 25.0:
            colors.append("#16C784")  # Green
        elif p <= 50.0:
            colors.append("#FFC400")  # Yellow
        elif p <= 75.0:
            colors.append("#FF8A00")  # Orange
        else:
            colors.append("#FF3B4F")  # Red

    fig = go.Figure(go.Bar(
        x=pcts,
        y=labels,
        orientation='h',
        marker=dict(color=colors, line=dict(color='#07111F', width=1.5)),
        text=[f"{p:.1f}%" for p in pcts],
        textposition='outside',
        textfont=dict(color='#F3F7FF', size=11, family='monospace'),
        hoverinfo='x+y',
    ))

    fig.update_layout(
        title=dict(text="<b>ML PREDICTED EXPLOITATION PROBABILITY BY CVE</b>", font=dict(color="#F3F7FF", size=13)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10,20,34,0.5)',
        xaxis=dict(title=dict(text="Exploitation Probability (%)", font=dict(color="#94A8C2", size=10)), range=[0, 110], gridcolor='#12365B', tickfont=dict(color="#94A8C2")),
        yaxis=dict(tickfont=dict(color="#F3F7FF", size=11)),
        margin=dict(l=20, r=30, t=35, b=30),
        height=height,
    )
    return fig


def render_feature_importance_chart(importances: Dict[str, float], height: int = 280) -> go.Figure:
    """
    Renders Plotly bar chart displaying Random Forest feature importances.
    """
    if not importances:
        fig = go.Figure()
        return fig

    friendly_names = {
        "epss_score": "EPSS Score",
        "cvss_score": "CVSS Score",
        "control_effectiveness": "Control Effectiveness",
        "internet_exposed": "Internet Exposure",
        "kev_status": "KEV Status",
        "asset_criticality": "Asset Criticality",
        "open_vulnerability_count": "Open Vuln Count",
        "high_vulnerability_count": "High Vuln Density",
        "business_criticality": "Business Criticality",
        "patch_available": "Patch Availability",
    }

    top_items = sorted(importances.items(), key=lambda x: x[1], reverse=False)[:7]
    labels = [friendly_names.get(k, k) for k, v in top_items]
    vals = [round(v * 100, 1) for k, v in top_items]

    fig = go.Figure(go.Bar(
        x=vals,
        y=labels,
        orientation='h',
        marker=dict(color='#00D9FF', line=dict(color='#07111F', width=1)),
        text=[f"{v:.1f}%" for v in vals],
        textposition='outside',
        textfont=dict(color='#F3F7FF', size=10),
    ))

    fig.update_layout(
        title=dict(text="<b>MODEL FEATURE IMPORTANCE (%)</b>", font=dict(color="#F3F7FF", size=12)),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(10,20,34,0.5)',
        xaxis=dict(title=dict(text="Importance Weight (%)", font=dict(color="#94A8C2", size=9)), range=[0, max(vals + [25]) * 1.2], gridcolor='#12365B', tickfont=dict(color="#94A8C2")),
        yaxis=dict(tickfont=dict(color="#F3F7FF", size=10)),
        margin=dict(l=20, r=30, t=30, b=30),
        height=height,
    )
    return fig
