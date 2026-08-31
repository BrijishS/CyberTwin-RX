import os
import sys

# Ensure project root is in sys.path when running via 'streamlit run dashboard/app.py'
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import streamlit as st
import pandas as pd
import plotly.express as px

from dashboard.api_client import APIClient
from dashboard.utils import format_currency_inr, get_risk_badge, RISK_COLORS, THEME_COLORS
from dashboard.components import (
    render_metric_card,
    render_risk_bar_chart,
    render_digital_twin_graph,
    render_attack_path_flow,
    render_risk_heatmap,
    generate_deterministic_alerts,
    render_attack_path_diagram,
    render_optimizer_donut,
    render_what_if_chart,
    render_exploit_probability_chart,
    render_feature_importance_chart,
)

# Page Configuration for 1920x1080 Command Center Fit
st.set_page_config(
    page_title="CyberTwin-RX",
    page_icon="🛡️",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS for Custom HTML/CSS Command Center Layout matching Reference Image
st.markdown("""<style>
    /* Hide Default Streamlit Decorations */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }
    header[data-testid="stHeader"] { height: 0px !important; visibility: hidden; }

    html, body, .stApp, .main, .block-container {
        max-width: 100% !important;
        overflow-x: hidden !important;
        box-sizing: border-box;
    }

    /* Dark Palette & Global Typography */
    .main, .stApp {
        background-color: #030913 !important;
        color: #94A8C2 !important;
        font-family: Inter, "Segoe UI", Roboto, Arial, sans-serif !important;
    }

    /* Compact Screen Spacing for 1920x1080 Single Screen Fit */
    .block-container {
        padding-top: 0.4rem !important;
        padding-bottom: 0.4rem !important;
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 100% !important;
    }

    /* Header Banner matching Prototype */
    .command-header-banner {
        background: #0A1422;
        border: 1px solid #12365B;
        border-radius: 8px;
        padding: 6px 14px;
        margin-bottom: 8px;
        display: flex;
        align-items: center;
        justify-content: space-between;
        gap: 10px;
        flex-wrap: wrap;
        min-width: 0;
    }
    .header-brand-group {
        display: flex;
        align-items: center;
        gap: 10px;
        min-width: 0;
        flex-wrap: wrap;
    }
    .shield-badge-logo {
        background: linear-gradient(135deg, #00D9FF 0%, #3C82FF 100%);
        color: #FFFFFF;
        width: 32px;
        height: 32px;
        border-radius: 6px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 1.05rem;
        font-weight: 800;
        box-shadow: 0 0 10px rgba(0, 217, 255, 0.4);
        flex-shrink: 0;
    }
    .brand-title-text {
        font-size: clamp(0.95rem, 1.4vw, 1.2rem);
        font-weight: 800;
        color: #F3F7FF;
        line-height: 1.1;
    }
    .brand-sub-text {
        font-size: 0.72rem;
        color: #00D9FF;
        font-weight: 600;
    }
    .header-title-group {
        text-align: center;
        flex: 1 1 220px;
        min-width: 0;
    }
    .main-title-heading {
        font-size: clamp(0.9rem, 1.6vw, 1.2rem);
        font-weight: 800;
        color: #F3F7FF;
        letter-spacing: 0.5px;
        text-transform: uppercase;
        line-height: 1.2;
    }
    .sub-title-heading {
        font-size: 0.72rem;
        color: #00D9FF;
        font-weight: 600;
        margin-top: 1px;
    }
    .header-status-group {
        display: flex;
        align-items: center;
        justify-content: flex-end;
        gap: 8px;
        flex-wrap: wrap;
        min-width: 0;
    }
    .badge-status-green {
        background: rgba(22, 199, 132, 0.15);
        color: #16C784;
        border: 1px solid #16C784;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 600;
    }
    .badge-status-cyan {
        background: rgba(0, 217, 255, 0.15);
        color: #00D9FF;
        border: 1px solid #00D9FF;
        padding: 2px 8px;
        border-radius: 10px;
        font-size: 0.7rem;
        font-weight: 600;
    }

    /* Sidebar Styling */
    section[data-testid="stSidebar"] {
        background-color: #07111F !important;
        border-right: 1px solid #12365B !important;
    }

    /* Streamlit Custom Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #3C82FF 0%, #00D9FF 100%) !important;
        color: #FFFFFF !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 6px !important;
        padding: 5px 12px !important;
        font-size: 0.78rem !important;
        text-transform: uppercase !important;
        min-height: 40px !important;
    }
    .stButton > button:hover {
        box-shadow: 0 0 12px rgba(0, 217, 255, 0.5) !important;
    }

    /* Streamlit Tables & Dataframes */
    .dataframe {
        font-size: 0.76rem !important;
        background-color: #0A1422 !important;
    }
    div[data-testid="stDataFrame"], div[data-testid="stDataFrameContainer"] {
        width: 100% !important;
        max-width: 100% !important;
        overflow-x: auto !important;
    }
    .stPlotlyChart, .stPlotlyChart > div {
        width: 100% !important;
        max-width: 100% !important;
    }

    /* Bottom Status Footer */
    .bottom-status-footer {
        background: #0A1422;
        border: 1px solid #12365B;
        border-radius: 6px;
        padding: 6px 14px;
        margin-top: 8px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        font-size: 0.74rem;
        color: #94A8C2;
        flex-wrap: wrap;
        gap: 8px;
    }

    @media (max-width: 1100px) {
        .command-header-banner { justify-content: center; }
        .header-brand-group, .header-title-group, .header-status-group {
            width: 100%;
            justify-content: center;
            text-align: center;
        }
        .header-status-group {
            justify-content: center;
        }
    }

    @media (max-width: 768px) {
        .block-container {
            padding-left: 0.5rem !important;
            padding-right: 0.5rem !important;
            padding-top: 0.5rem !important;
        }
        .command-header-banner {
            padding: 8px 10px;
        }
        div[data-testid="stHorizontalBlock"] {
            display: grid !important;
            grid-template-columns: 1fr !important;
            gap: 0.5rem;
            width: 100% !important;
        }
        div[data-testid="stHorizontalBlock"] > div {
            width: 100% !important;
            max-width: 100% !important;
        }
        .main-title-heading {
            font-size: clamp(0.95rem, 4vw, 1.15rem);
        }
        .badge-status-green, .badge-status-cyan {
            font-size: 0.68rem;
            white-space: normal;
        }
        section[data-testid="stSidebar"] {
            min-width: min(80vw, 280px) !important;
        }
    }

    @media (max-width: 480px) {
        .brand-title-text { font-size: 1rem; }
        .header-brand-group { gap: 6px; }
        .shield-badge-logo { width: 28px; height: 28px; }
        .bottom-status-footer { font-size: 0.68rem; }
        .stButton > button { width: 100% !important; }
    }
</style>""", unsafe_allow_html=True)

# Initialize API Client
client = APIClient()
backend_online = client.check_health()

# Fetch Real Live API Data
summary = client.get_risk_summary()
asset_risks = client.get_assets_risk()
opt_res = client.optimize_investment(5000000.0)
ai_status = client.get_ai_status()

# Top Command Center Header
ml_badge_html = '<span class="badge-status-cyan">🤖 ML Model: Active</span>' if ai_status.get("loaded") else ''
health_label = "🟢 System Health: Healthy" if backend_online else "🔴 System Health: Unavailable"
status_badge = '<span class="badge-status-green">{}</span>'.format(health_label) if backend_online else '<span class="badge-status-cyan">Backend API temporarily unavailable.</span>'
st.markdown(f'<div class="command-header-banner"><div class="header-brand-group"><div class="shield-badge-logo">🛡️</div><div><div class="brand-title-text">CyberTwin-RX</div><div class="brand-sub-text">by Hackhives</div></div></div><div class="header-title-group"><div class="main-title-heading">CYBER RISK COMMAND CENTER</div></div><div class="header-status-group">{status_badge}{ml_badge_html}<span class="badge-status-cyan">Synthetic Demo Environment</span></div></div>', unsafe_allow_html=True)

if not backend_online:
    st.warning("Backend API temporarily unavailable.")
    st.caption(f"Using API base URL: {client.base_url}")

# Compact Left Sidebar Navigation
st.sidebar.markdown("### 🎛️ Navigation")
page = st.sidebar.radio(
    "Select Module",
    [
        "Overview",
        "Digital Twin",
        "Attack Paths",
        "Risk Analysis",
        "Investment Optimizer",
        "What-If Simulator",
        "🤖 ML Exploit Intelligence",
        "Assets & Vulnerabilities",
        "Alerts",
    ]
)

st.sidebar.markdown('---')
st.sidebar.markdown('<div style="background: #0A1422; border: 1px solid #12365B; border-radius: 6px; padding: 12px; text-align: center;"><div style="color: #00D9FF; font-size: 1.05rem; font-weight: 800;">CyberTwin-RX</div><div style="color: #94A8C2; font-size: 0.72rem; margin-top: 2px;">by Hackhives</div></div>', unsafe_allow_html=True)



# Fetch Real Live API Data
summary = client.get_risk_summary()
asset_risks = client.get_assets_risk()
opt_res = client.optimize_investment(5000000.0)

# ==============================================================================
# 1. OVERVIEW PROTOTYPE COMMAND CENTER VIEW
# ==============================================================================
if page == "Overview":
    # TOP KPI ROW (4 Prominent Cards)
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        render_metric_card(
            title="TOTAL CYBER RISK",
            value=f"{summary.get('average_risk_score', 39.4):.1f} / 100",
            subtitle="Enterprise Cyber Risk Index",
            color="#FF3B4F",
            icon_type="risk"
        )
    with k2:
        render_metric_card(
            title="FINANCIAL EXPOSURE",
            value=format_currency_inr(summary.get("total_financial_exposure", 0)),
            subtitle="Expected Value at Risk",
            color="#FF8A00",
            icon_type="loss"
        )
    with k3:
        render_metric_card(
            title="CRITICAL / HIGH ASSETS",
            value=f"{summary.get('critical_assets', 1)} / {summary.get('high_risk_assets', 1)}",
            subtitle="Immediate Mitigation Required",
            color="#9C55FF",
            icon_type="purple"
        )
    with k4:
        render_metric_card(
            title="RISK REDUCTION POTENTIAL",
            value=format_currency_inr(opt_res.get("estimated_risk_reduction", 0)),
            subtitle="Optimized Portfolio Savings",
            color="#16C784",
            icon_type="potential"
        )

    st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)

    # MAIN DASHBOARD GRID (ROW 1: Digital Twin | Attack Path | Risk Heatmap)
    g1, g2, g3 = st.columns([1.25, 1.0, 1.0])

    with g1:
        st.markdown("""<div style="background: #0A1422; border: 1px solid #12365B; border-radius: 8px; padding: 8px 12px 4px 12px;">""", unsafe_allow_html=True)
        graph_data = client.get_digital_twin_graph()
        fig_dt = render_digital_twin_graph(graph_data, height=310, curated_only=True)
        st.plotly_chart(fig_dt, use_container_width=True)
        
        # Prototype Legend Bar
        st.markdown('<div style="background: #030913; border: 1px solid #12365B; border-radius: 4px; padding: 4px 8px; font-size: 0.7rem; color: #94A8C2; display: flex; justify-content: space-around; margin-bottom: 4px;"><span><span style="color: #FF3B4F;">●</span> Critical</span><span><span style="color: #FF8A00;">●</span> High</span><span><span style="color: #FFC400;">●</span> Medium</span><span><span style="color: #16C784;">●</span> Low</span><span><span style="color: #00D9FF;">●</span> External</span></div></div>', unsafe_allow_html=True)


    with g2:
        top_path = client.get_top_attack_path()
        path_flow_html = render_attack_path_flow(top_path)
        st.markdown(path_flow_html, unsafe_allow_html=True)

    with g3:
        st.markdown("""<div style="background: #0A1422; border: 1px solid #12365B; border-radius: 8px; padding: 8px 12px 4px 12px;">""", unsafe_allow_html=True)
        fig_hm = render_risk_heatmap(asset_risks, height=335)
        st.plotly_chart(fig_hm, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='margin-top: 4px;'></div>", unsafe_allow_html=True)

    # SECOND DASHBOARD ROW (ROW 2: Investment Optimizer | What-If Simulator | Alerts)
    r2_1, r2_2, r2_3 = st.columns([1.25, 1.0, 1.0])

    with r2_1:
        st.markdown("""<div style="background: #0A1422; border: 1px solid #12365B; border-radius: 8px; padding: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="color: #F3F7FF; font-size: 0.85rem; font-weight: 700;">INVESTMENT OPTIMIZER</span>
                <span style="color: #00D9FF; font-size: 0.72rem; font-weight: 600;">Available Budget: ₹50.00 Lakh</span>
            </div>""", unsafe_allow_html=True)

        opt_c1, opt_c2 = st.columns([1.4, 1.0])
        with opt_c1:
            selected_ctrls = opt_res.get("selected_controls", [])
            if selected_ctrls:
                df_opt = pd.DataFrame([
                    {
                        "Control": c["name"],
                        "Scope": c["asset"],
                        "Cost": format_currency_inr(c["cost"]),
                        "Risk Red.": format_currency_inr(c["estimated_risk_reduction"]),
                        "ROSI": f"{c['rosi']:.1f}%",
                    }
                    for c in selected_ctrls
                ])
                st.dataframe(df_opt, width="stretch", height=125)
            else:
                st.info("No candidates selected")

        with opt_c2:
            fig_don = render_optimizer_donut(opt_res)
            st.plotly_chart(fig_don, use_container_width=True)
            st.button("OPTIMIZE ALLOCATION", key="btn_ov_opt_main_2")

        st.markdown("</div>", unsafe_allow_html=True)

    with r2_2:
        st.markdown("""<div style="background: #0A1422; border: 1px solid #12365B; border-radius: 8px; padding: 10px;">
            <div style="color: #F3F7FF; font-size: 0.85rem; font-weight: 700; margin-bottom: 6px;">WHAT-IF SIMULATOR</div>""", unsafe_allow_html=True)

        assets_list = client.get_assets()
        asset_map_sim = {a["name"]: a["id"] for a in assets_list}
        
        sim_col1, sim_col2 = st.columns(2)
        with sim_col1:
            target_asset_name = st.selectbox("Target Asset", list(asset_map_sim.keys()), key="sim_asset_ov_2")
        with sim_col2:
            target_ctrl_type = st.selectbox("Control Scenario", ["MFA", "EDR", "Network Segmentation", "Database Encryption", "Patch vulnerability"], key="sim_ctrl_ov_2")

        sim_res = client.simulate_what_if(
            asset_id=asset_map_sim.get(target_asset_name, 1),
            control_type=target_ctrl_type,
            effectiveness=0.85
        )

        if sim_res:
            st.markdown(f'<div style="display: flex; gap: 8px; margin-top: 2px;"><div style="flex: 1; background: rgba(255, 59, 79, 0.1); border: 1px solid #FF3B4F; border-radius: 4px; padding: 4px; text-align: center;"><div style="color: #FF3B4F; font-size: 0.65rem; font-weight: 700;">CURRENT STATE</div><div style="color: #F3F7FF; font-size: 1.0rem; font-weight: 800;">{sim_res["current_risk_score"]:.1f}/100</div><div style="color: #94A8C2; font-size: 0.62rem;">{format_currency_inr(sim_res["current_financial_exposure"])}</div></div><div style="flex: 1; background: rgba(22, 199, 132, 0.1); border: 1px solid #16C784; border-radius: 4px; padding: 4px; text-align: center;"><div style="color: #16C784; font-size: 0.65rem; font-weight: 700;">SIMULATED OUTCOME</div><div style="color: #F3F7FF; font-size: 1.0rem; font-weight: 800;">{sim_res["simulated_risk_score"]:.1f}/100</div><div style="color: #94A8C2; font-size: 0.62rem;">{format_currency_inr(sim_res["simulated_financial_exposure"])}</div></div></div>', unsafe_allow_html=True)

        fig_sim_chart = render_what_if_chart(sim_res)
        st.plotly_chart(fig_sim_chart, use_container_width=True)
        st.markdown("</div>", unsafe_allow_html=True)

    with r2_3:
        st.markdown("""<div style="background: #0A1422; border: 1px solid #12365B; border-radius: 8px; padding: 10px;">
            <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 6px;">
                <span style="color: #F3F7FF; font-size: 0.85rem; font-weight: 700;">ALERTS</span>
                <span style="color: #00D9FF; font-size: 0.72rem; font-weight: 600;">Deterministic</span>
            </div>""", unsafe_allow_html=True)

        alerts = generate_deterministic_alerts(asset_risks)
        alert_items_html = []
        for alt in alerts:
            alert_items_html.append(f"""<div style="background: #07111F; border: 1px solid {alt['color']}44; border-left: 3px solid {alt['color']}; padding: 5px 8px; border-radius: 4px; margin-bottom: 4px;"><div style="display: flex; justify-content: space-between; font-size: 0.72rem; font-weight: 700; color: {alt['color']};"><span>[{alt['level']}] {alt['title']}</span></div><div style="color: #94A8C2; font-size: 0.66rem; margin-top: 1px;">{alt['detail']}</div></div>""")

        st.markdown(f"""<div>{"".join(alert_items_html)}</div></div>""", unsafe_allow_html=True)

    # BOTTOM STATUS BAR matching Prototype
    ml_footer_status = "🟢 Active" if ai_status.get("loaded") else "🔴 Unavailable"
    st.markdown(f'<div class="bottom-status-footer"><span>🛡️ System Health: <b style="color:#16C784;">🟢 Healthy</b></span><span>ML Model: <b style="color:#00D9FF;">Random Forest ({ml_footer_status})</b></span><span>Assets Monitored: <b style="color:#F3F7FF;">{summary.get("total_assets", 12)}</b></span><span>Vulnerabilities: <b style="color:#FFC400;">{summary.get("total_vulnerabilities", 20)}</b></span><span>Critical Assets: <b style="color:#FF3B4F;">{summary.get("critical_assets", 1)}</b></span><span>Financial Exposure: <b style="color:#FF8A00;">{format_currency_inr(summary.get("total_financial_exposure", 0))}</b></span><span>Powered by: <b>CyberTwin-RX</b> | Team: <b>Hackhives</b></span></div>', unsafe_allow_html=True)


# ==============================================================================
# 2. DIGITAL TWIN SUBPAGE
# ==============================================================================
elif page == "Digital Twin":
    st.title("Cyber Digital Twin Graph")
    st.caption("Complete graph representation of demo organization assets, services, controls, and internet connections.")

    graph_data = client.get_digital_twin_graph()
    fig_dt = render_digital_twin_graph(graph_data, height=520, curated_only=False)
    st.plotly_chart(fig_dt, use_container_width=True)

    with st.expander("🔍 View Digital Twin Topology Node Details"):
        nodes = graph_data.get("nodes", [])
        if nodes:
            df_nodes = pd.DataFrame(nodes)
            st.dataframe(df_nodes, use_container_width=True)

# ==============================================================================
# 3. ATTACK PATHS SUBPAGE
# ==============================================================================
elif page == "Attack Paths":
    st.title("Attack Path Analysis")
    st.caption("Deterministic graph traversal from Internet entry points to critical databases and core assets.")

    top_path = client.get_top_attack_path()
    all_paths = client.get_attack_paths()

    if top_path and top_path.get("path"):
        st.markdown("### 🎯 Top Critical Attack Path")
        fig_path = render_attack_path_diagram(top_path)
        st.plotly_chart(fig_path, use_container_width=True)

        col_p1, col_p2 = st.columns(2)
        with col_p1:
            st.markdown(f"**Path Risk Score:** `{top_path.get('path_score', 0):.1f} / 100`")
            st.markdown(f"**Potential Financial Exposure:** `{format_currency_inr(top_path.get('potential_financial_exposure', 0))}`")
            st.markdown(f"**Target Asset:** `{top_path.get('target_asset')}`")
        with col_p2:
            st.markdown("**Weakest Vulnerable Points Along Path:**")
            for wp in top_path.get("weakest_points", []):
                st.markdown(f"- ⚠️ {wp}")

    st.markdown("---")
    st.markdown("### 📋 All Detected Attack Paths")
    if all_paths:
        path_table_data = []
        for p in all_paths:
            path_table_data.append({
                "Risk Score": f"{p['path_score']:.1f}",
                "Path Flow": " → ".join(p["path"]),
                "Target Asset": p["target_asset"],
                "Financial Exposure": format_currency_inr(p["potential_financial_exposure"]),
                "Weak Points Count": len(p["weakest_points"]),
            })
        st.dataframe(pd.DataFrame(path_table_data), use_container_width=True)

# ==============================================================================
# 4. RISK ANALYSIS SUBPAGE
# ==============================================================================
elif "Risk" in page:
    st.title("Asset Risk Heatmap & Detailed Analysis")
    
    fig_hm_full = render_risk_heatmap(asset_risks, height=450)
    st.plotly_chart(fig_hm_full, use_container_width=True)

    fig_bar = render_risk_bar_chart(asset_risks)
    st.plotly_chart(fig_bar, use_container_width=True)

    st.markdown("### 🛡️ Asset Risk Breakdown Table")
    risk_df_data = []
    for a in asset_risks:
        risk_df_data.append({
            "Asset ID": a["asset_id"],
            "Asset Name": a["asset_name"],
            "Type": a["asset_type"],
            "Criticality": a["criticality"],
            "Internet Exposed": "Yes" if a["internet_exposed"] else "No",
            "Risk Score": a["risk_score"],
            "Risk Level": a["risk_level"],
            "Financial Exposure": format_currency_inr(a["estimated_financial_exposure"]),
            "Control Coverage": f"{int(a['combined_control_effectiveness'] * 100)}%",
            "Risk Drivers": ", ".join(a["risk_drivers"]),
        })
    st.dataframe(pd.DataFrame(risk_df_data), use_container_width=True)

    st.markdown("---")
    st.markdown("### 🤖 ML Exploit Intelligence")
    st.caption("Machine learning model (RandomForestClassifier) trained on synthetic cybersecurity data for prototype demonstration. Predicts vulnerability exploitation likelihood.")

    top_ml_threats = client.get_top_ml_threats(limit=5)
    if top_ml_threats:
        ml_table_data = []
        for t in top_ml_threats:
            ml_table_data.append({
                "CVE ID": t["cve_id"],
                "Asset Name": t["asset"],
                "CVSS Score": f"{t['cvss_score']:.1f}",
                "EPSS Score": f"{t['epss_score']:.4f}",
                "ML Exploitation Prob": f"{t['percentage']:.1f}%",
                "ML Risk Level": t["risk_level"],
                "Confidence": t["confidence"],
                "Top Contributing Features": ", ".join(t.get("top_contributing_features", [])),
                "AI Priority Score": f"{t.get('ai_assisted_priority_score', 0):.1f}/100",
            })
        st.dataframe(pd.DataFrame(ml_table_data), use_container_width=True)


# ==============================================================================
# 5. INVESTMENT OPTIMIZER SUBPAGE
# ==============================================================================
elif page == "Investment Optimizer":
    st.title("Security Investment Optimizer")
    st.markdown("##### *Answer: 'If I have ₹X budget, where should I spend it to maximize risk reduction?'*")
    st.caption("Powered by Google OR-Tools (0-1 Integer Linear Programming). Deterministic & Explainable.")

    # Budget Input UI
    st.markdown("#### Select Available Cybersecurity Budget")
    col_b1, col_b2, col_b3, col_b4 = st.columns(4)
    budget_preset = None
    with col_b1:
        if st.button("₹10 Lakh (₹10L)", key="b10"):
            budget_preset = 1000000.0
    with col_b2:
        if st.button("₹25 Lakh (₹25L)", key="b25"):
            budget_preset = 2500000.0
    with col_b3:
        if st.button("₹50 Lakh (₹50L)", key="b50"):
            budget_preset = 5000000.0
    with col_b4:
        if st.button("₹1 Crore (₹1Cr)", key="b100"):
            budget_preset = 10000000.0

    current_budget = budget_preset if budget_preset else 5000000.0
    user_budget = st.number_input(
        "Enter Custom Budget (in INR ₹)",
        min_value=100000.0,
        max_value=100000000.0,
        value=current_budget,
        step=500000.0,
        format="%.0f",
        key="opt_custom_budget_page"
    )

    if st.button("🚀 OPTIMIZE SECURITY PORTFOLIO", key="btn_page_opt"):
        opt_res_page = client.optimize_investment(user_budget)
        if opt_res_page:
            st.success("Optimization Solved Successfully!")

            # Summary Metrics Cards
            col_m1, col_m2, col_m3, col_m4, col_m5 = st.columns(5)
            with col_m1:
                render_metric_card("Available Budget", format_currency_inr(opt_res_page["available_budget"]), color="#00D9FF")
            with col_m2:
                render_metric_card("Total Investment", format_currency_inr(opt_res_page["total_investment"]), color="#FFC400")
            with col_m3:
                render_metric_card("Remaining Budget", format_currency_inr(opt_res_page["remaining_budget"]), color="#16C784")
            with col_m4:
                render_metric_card("Risk Score Change", f"{opt_res_page['risk_before']:.1f} → {opt_res_page['estimated_risk_after']:.1f}", color="#FF8A00")
            with col_m5:
                render_metric_card("Portfolio ROSI", f"{opt_res_page['portfolio_rosi']:.1f}%", subtitle=f"Red: {format_currency_inr(opt_res_page['estimated_risk_reduction'])}", color="#00D9FF")

            # Selected Controls Table
            st.markdown("### 📋 Recommended Security Controls Portfolio")
            selected = opt_res_page.get("selected_controls", [])
            if selected:
                ctrl_df_data = []
                for sc in selected:
                    ctrl_df_data.append({
                        "Control Name": sc["name"],
                        "Target Asset": sc["asset"],
                        "Cost (INR)": format_currency_inr(sc["cost"]),
                        "Effectiveness": f"{int(sc['effectiveness'] * 100)}%",
                        "Estimated Risk Reduction": format_currency_inr(sc["estimated_risk_reduction"]),
                        "ROSI (%)": f"{sc['rosi']:.1f}%",
                    })
                st.dataframe(pd.DataFrame(ctrl_df_data), use_container_width=True)
            else:
                st.warning("No security control fits within the specified budget.")

# ==============================================================================
# 6. WHAT-IF SIMULATOR SUBPAGE
# ==============================================================================
elif page == "What-If Simulator":
    st.title("What-If Security Improvement Simulator")
    st.caption("Simulate security enhancements BEFORE implementing them. Zero database side effects.")

    assets = client.get_assets()
    asset_options = {a["name"]: a["id"] for a in assets}

    c_sim1, c_sim2, c_sim3 = st.columns(3)
    with c_sim1:
        sel_asset_name = st.selectbox("Select Target Asset", list(asset_options.keys()), key="pg_sim_asset_sub")
        sel_asset_id = asset_options.get(sel_asset_name)
    with c_sim2:
        sel_control_type = st.selectbox(
            "Select Security Control / Scenario",
            [
                "Multi-Factor Authentication (MFA)",
                "Endpoint Detection and Response (EDR)",
                "Network Segmentation",
                "Firewall Improvement",
                "Database Encryption",
                "Backup Improvement",
                "Privileged Access Management (PAM)",
                "Patch vulnerability",
            ],
            key="pg_sim_ctrl_sub"
        )
    with c_sim3:
        sel_eff = st.slider("Control Effectiveness", min_value=0.50, max_value=0.95, value=0.85, step=0.05, key="pg_sim_eff_sub")

    if st.button("🧪 SIMULATE IMPROVEMENT", key="btn_pg_sim_sub"):
        sim_res = client.simulate_what_if(
            asset_id=sel_asset_id,
            control_type=sel_control_type,
            effectiveness=sel_eff,
        )

        if sim_res:
            st.markdown("---")
            st.markdown(f"### 📊 Simulation Results: {sim_res['scenario']}")

            card_c1, card_c2 = st.columns(2)
            with card_c1:
                st.markdown(f"""<div style="background: rgba(255, 59, 79, 0.1); border: 1px solid #FF3B4F; border-radius: 6px; padding: 20px; text-align: center;">
                    <h4 style="color: #FF3B4F; margin: 0;">🔴 CURRENT STATE</h4>
                    <div style="font-size: 2.2rem; font-weight: 700; color: #F3F7FF; margin: 10px 0;">
                        Score: {sim_res['current_risk_score']:.1f}/100
                    </div>
                    <div style="color: #94A8C2;">Exposure: <b>{format_currency_inr(sim_res['current_financial_exposure'])}</b></div>
                </div>""", unsafe_allow_html=True)

            with card_c2:
                st.markdown(f"""<div style="background: rgba(22, 199, 132, 0.1); border: 1px solid #16C784; border-radius: 6px; padding: 20px; text-align: center;">
                    <h4 style="color: #16C784; margin: 0;">🟢 SIMULATED OUTCOME</h4>
                    <div style="font-size: 2.2rem; font-weight: 700; color: #F3F7FF; margin: 10px 0;">
                        Score: {sim_res['simulated_risk_score']:.1f}/100
                    </div>
                    <div style="color: #94A8C2;">Exposure: <b>{format_currency_inr(sim_res['simulated_financial_exposure'])}</b></div>
                </div>""", unsafe_allow_html=True)

            st.markdown("#### Impact Summary")
            st.info(f"✨ **Risk Score Reduction:** `{sim_res['risk_score_reduction']:.1f} pts` | 💰 **Financial Risk Savings:** `{format_currency_inr(sim_res['estimated_financial_risk_reduction'])}` | 📉 **Relative Risk Reduction:** `{sim_res['percentage_reduction']:.1f}%`")

# ==============================================================================
# 7. ML EXPLOIT INTELLIGENCE SUBPAGE
# ==============================================================================
elif "ML" in page or page == "🤖 ML Exploit Intelligence":
    st.title("🤖 ML Exploit Intelligence")
    st.markdown("##### *Machine-learning based vulnerability exploitation probability*")
    st.caption("ℹ️ Synthetic cybersecurity training dataset for prototype validation.")

    # 1. MODEL STATUS METRIC CARDS
    st.markdown("#### Model Status & Metadata")
    is_active = ai_status.get("loaded", False)
    status_str = "Active" if is_active else "Unavailable"
    status_color = "#16C784" if is_active else "#FF3B4F"

    m_samples = ai_status.get("training_samples", 5000)
    metrics = ai_status.get("metrics", {})
    roc_val = metrics.get("roc_auc", 0.8188)
    acc_val = metrics.get("accuracy", 0.7370)

    mc1, mc2, mc3, mc4, mc5 = st.columns(5)
    with mc1:
        render_metric_card("MODEL", "Random Forest", subtitle="scikit-learn", color="#00D9FF", icon_type="purple")
    with mc2:
        render_metric_card("STATUS", status_str, subtitle="Exploit Predictor", color=status_color, icon_type="potential")
    with mc3:
        render_metric_card("TRAINING SAMPLES", f"{m_samples:,}", subtitle="Synthetic Dataset", color="#FFC400", icon_type="purple")
    with mc4:
        render_metric_card("ROC-AUC SCORE", f"{roc_val:.4f}", subtitle="Model Discrimination", color="#00D9FF", icon_type="potential")
    with mc5:
        render_metric_card("ACCURACY", f"{acc_val * 100:.1f}%", subtitle="Test Set Accuracy", color="#16C784", icon_type="potential")

    st.markdown("<div style='margin-top: 10px;'></div>", unsafe_allow_html=True)
    st.info("💡 **ML exploitation probability** estimates likelihood of exploitation, while **CyberTwin-RX risk scoring** evaluates broader business and financial impact.")

    st.markdown("---")

    # 2. TOP PREDICTED THREATS & EXPLOIT PROBABILITY CHART
    st.markdown("### 🎯 Top Predicted Exploitation Threats")
    top_threats = client.get_top_ml_threats(limit=5)

    if top_threats:
        chart_col, table_col = st.columns([1.15, 1.0])
        with chart_col:
            fig_ml_prob = render_exploit_probability_chart(top_threats, height=350)
            st.plotly_chart(fig_ml_prob, use_container_width=True)

        with table_col:
            st.markdown("##### Detailed Threat Breakdown")
            threat_rows = []
            for rank, t in enumerate(top_threats, 1):
                threat_rows.append({
                    "Rank": f"#{rank}",
                    "CVE ID": t.get("cve_id"),
                    "Asset": t.get("asset"),
                    "CVSS": f"{t.get('cvss_score'):.1f}",
                    "EPSS": f"{t.get('epss_score'):.4f}",
                    "Exploit Prob": f"{t.get('percentage'):.1f}%",
                    "Risk Level": t.get("risk_level"),
                    "Confidence": t.get("confidence"),
                })
            st.dataframe(pd.DataFrame(threat_rows), use_container_width=True)
    else:
        st.warning("⚠️ ML Top Threats prediction service unavailable.")

    st.markdown("---")

    # 3. FEATURE IMPORTANCE & INDIVIDUAL PREDICTION
    f_col, p_col = st.columns([1.0, 1.1])

    with f_col:
        st.markdown("### 📊 Model Feature Importance")
        importances = ai_status.get("feature_importances", {})
        fig_feat_imp = render_feature_importance_chart(importances, height=310)
        st.plotly_chart(fig_feat_imp, use_container_width=True)
        st.caption("Feature importance shows which inputs influence the Random Forest model most strongly overall.")

    with p_col:
        st.markdown("### 🔍 Individual Vulnerability Prediction")
        all_vulns = client.get_vulnerabilities()
        if all_vulns:
            vuln_map = {f"{v['cve_id']} - {v.get('title', 'Vuln')[:30]} (ID: {v['id']})": v['id'] for v in all_vulns}
            selected_vuln_label = st.selectbox("Select Vulnerability to Analyze", list(vuln_map.keys()), key="ml_select_vuln")
            sel_id = vuln_map[selected_vuln_label]

            pred_res = client.get_ml_prediction(sel_id)
            if pred_res:
                pct = pred_res.get("percentage", 0.0)
                level = pred_res.get("risk_level", "Low")
                conf = pred_res.get("confidence", "Medium")
                top_feats = pred_res.get("top_contributing_features", [])

                level_colors = {"Low": "#16C784", "Moderate": "#FFC400", "High": "#FF8A00", "Critical": "#FF3B4F"}
                lvl_color = level_colors.get(level, "#00D9FF")

                st.markdown(f"""<div style="background: #0A1422; border: 1px solid #12365B; border-top: 3px solid {lvl_color}; border-radius: 8px; padding: 14px; margin-top: 6px;">
                    <div style="display: flex; justify-content: space-between; align-items: center;">
                        <span style="color: #94A8C2; font-size: 0.8rem; font-weight: 700;">PREDICTED EXPLOITATION PROBABILITY</span>
                        <span style="background: rgba(0,217,255,0.15); color: #00D9FF; border: 1px solid #00D9FF; padding: 2px 8px; border-radius: 4px; font-size: 0.72rem;">Confidence: {conf}</span>
                    </div>
                    <div style="color: {lvl_color}; font-size: 2.2rem; font-weight: 800; font-family: monospace; margin: 6px 0;">
                        {pct:.1f}%
                    </div>
                    <div style="color: #F3F7FF; font-size: 0.85rem;">
                        ML Risk Level: <b style="color: {lvl_color};">{level}</b> | AI Priority Score: <b>{pred_res.get('ai_assisted_priority_score', 0):.1f}/100</b>
                    </div>
                </div>""", unsafe_allow_html=True)

                if top_feats:
                    st.markdown("##### Primary Risk Signals")
                    for tf in top_feats:
                        st.markdown(f"- ⚡ **{tf}**")
        else:
            st.info("No vulnerabilities available in database.")

    st.markdown("---")

    # 4. EXPANDABLE MODEL EXPLANATION
    with st.expander("📖 How the Machine Learning Model Works"):
        st.markdown("""
        1. **CyberTwin-RX collects vulnerability and asset features:** Includes CVSS, EPSS, KEV status, internet exposure, asset criticality, and security-control effectiveness.
        2. **Features are passed to a trained Random Forest classifier:** Uses `scikit-learn` `RandomForestClassifier` trained on synthetic cybersecurity validation data.
        3. **Estimates exploitation probability:** Computes `predict_proba()` to estimate the probability that the vulnerability belongs to the likely-to-be-exploited class.
        4. **Risk Categorization & Confidence:** Categorizes into Low, Moderate, High, or Critical, and computes confidence scores based on decision boundary distance.
        5. **Hybrid Prioritization:** CyberTwin-RX uses this ML prediction as an additional prioritization signal alongside its deterministic risk and financial-risk engine.
        """)

# ==============================================================================
# 7. ASSETS & VULNERABILITIES SUBPAGE
# ==============================================================================
elif page == "Assets & Vulnerabilities":
    st.title("CyberTwin Inventory & Data Explorer")

    tab_bs, tab_as, tab_vul, tab_ctrl = st.tabs(["Business Services", "Assets", "Vulnerabilities", "Security Controls"])

    with tab_bs:
        bs_data = client.get_business_services()
        st.dataframe(pd.DataFrame(bs_data), use_container_width=True)

    with tab_as:
        as_data = client.get_assets()
        st.dataframe(pd.DataFrame(as_data), use_container_width=True)

    with tab_vul:
        vul_data = client.get_vulnerabilities()
        st.dataframe(pd.DataFrame(vul_data), use_container_width=True)

    with tab_ctrl:
        ctrl_data = client.get_security_controls()
        st.dataframe(pd.DataFrame(ctrl_data), use_container_width=True)

# ==============================================================================
# 8. ALERTS SUBPAGE
# ==============================================================================
elif page == "Alerts":
    st.title("Deterministic Cyber Risk Alerts")
    alerts_all = generate_deterministic_alerts(asset_risks)
    for alt in alerts_all:
        st.markdown(f"""<div style="background: #0A1422; border: 1px solid {alt['color']}55; border-left: 4px solid {alt['color']}; padding: 12px 16px; border-radius: 6px; margin-bottom: 10px;"><div style="display: flex; justify-content: space-between; font-weight: 700; color: {alt['color']}; font-size: 0.95rem;"><span>{alt['title']}</span><span>[{alt['level']}]</span></div><div style="color: #94A8C2; font-size: 0.82rem; margin-top: 4px;">{alt['detail']}</div></div>""", unsafe_allow_html=True)
