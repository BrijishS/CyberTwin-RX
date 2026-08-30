# CyberTwin-RX

Continuous Cyber Risk Quantification & Security Investment Optimization Platform

## Overview
CyberTwin-RX is a continuous cyber risk quantification and security investment optimization platform designed for SIH 2026. The platform models organizational IT/OT assets using a Cyber Digital Twin, performs attack path analysis, quantifies financial cyber risk exposure, optimizes security investments using mathematical optimization, and allows interactive what-if simulation via a real-time command center.

## Project Status
**Phase 6 — Integrated Hackathon MVP (Complete)**

## Core Features Implemented
- **Continuous Cyber Risk Quantification**: Deterministic risk scoring based on CVSS, EPSS, KEV status, internet exposure, asset criticality, and security control effectiveness.
- **Cyber Digital Twin**: Graph-based topology model representing business services, assets, security controls, and network boundaries.
- **Attack Path Analysis**: Network graph traversal prioritizing multi-hop attack paths toward critical databases and high-value business assets.
- **Financial Exposure Estimation**: Financial value-at-risk modeling calculating potential financial losses in INR.
- **Security Investment Optimizer**: Mathematical optimization using Google OR-Tools (0-1 Integer Linear Programming) to maximize risk reduction under budget constraints and calculate ROSI.
- **What-If Simulator**: Zero-side-effect in-memory simulation engine for evaluating security controls and patch deployments before implementation.
- **Streamlit Command Center**: Dark cybersecurity dashboard featuring Plotly charts, Digital Twin network visualization, attack path flows, optimizer controls, and what-if simulation cards.

## Tech Stack
- **Backend**: Python, FastAPI, Uvicorn
- **Database & Data Layer**: SQLite, SQLAlchemy, Pandas, NumPy
- **Validation**: Pydantic, Pydantic-Settings
- **Graph Analysis**: NetworkX
- **Optimization**: Google OR-Tools
- **Dashboard & Visualization**: Streamlit, Plotly
- **Testing & HTTP**: Pytest, Requests, HTTPX

## Getting Started

### Prerequisites
- Python 3.10+
- Windows PowerShell

### Installation & Run

1. **Install Dependencies**:
   ```powershell
   pip install -r requirements.txt
   ```

2. **Seed Data**:
   ```powershell
   python -m backend.seed
   ```

3. **Start FastAPI Backend Server**:
   ```powershell
   python -m uvicorn backend.main:app --reload
   ```

4. **Start Streamlit Dashboard**:
   ```powershell
   streamlit run dashboard/app.py
   ```

5. **Run Automated Tests**:
   ```powershell
   python -m pytest -q
   ```

### API Endpoints
- **Root (`GET /`)**: `http://127.0.0.1:8000/`
- **Health Check (`GET /health`)**: `http://127.0.0.1:8000/health`
- **Swagger Documentation**: `http://127.0.0.1:8000/docs`
- **Risk Quantification**: `http://127.0.0.1:8000/api/risk/summary`
- **Digital Twin**: `http://127.0.0.1:8000/api/digital-twin/graph`
- **Attack Paths**: `http://127.0.0.1:8000/api/attack-paths/top`
- **Investment Optimizer**: `http://127.0.0.1:8000/api/optimizer/recommend`
- **What-If Simulator**: `http://127.0.0.1:8000/api/simulation/what-if`
