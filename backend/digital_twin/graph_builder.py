import networkx as nx
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.models import Asset, BusinessService, SecurityControl
from backend.risk_engine.service import get_all_assets_risk


# Known logical topological connections between demo bank assets
ASSET_TOPOLOGY_CONNECTIONS = [
    ("Internet-Banking-Web-01", "Auth-Service-01"),
    ("Mobile-Banking-API-01", "Auth-Service-01"),
    ("Auth-Service-01", "Customer-DB-01"),
    ("Payment-Gateway-01", "Transaction-API-01"),
    ("Transaction-API-01", "Payment-DB-01"),
    ("Customer-API-01", "Customer-DB-01"),
    ("Employee-Portal-01", "HR-DB-01"),
    ("SIEM-Server-01", "SOC-Monitoring-01"),
]


def build_digital_twin_graph(db: Session) -> nx.DiGraph:
    G = nx.DiGraph()

    # Calculate current risk for all assets
    asset_risks = {r["asset_id"]: r for r in get_all_assets_risk(db)}
    assets = db.query(Asset).all()
    asset_name_to_id = {a.name: a.id for a in assets}

    # 1. Root Internet Node
    G.add_node(
        "Internet",
        id="Internet",
        name="Internet",
        type="internet",
        criticality="Critical",
        risk_score=100.0,
        internet_exposed=True,
        financial_value=0.0,
    )

    # 2. Business Services
    business_services = db.query(BusinessService).all()
    for bs in business_services:
        bs_node_id = f"bs_{bs.id}"
        G.add_node(
            bs_node_id,
            id=bs_node_id,
            name=bs.name,
            type="business_service",
            criticality=bs.criticality,
            risk_score=0.0,
            internet_exposed=False,
            financial_value=bs.financial_value,
        )

    # 3. Assets
    for asset in assets:
        risk_info = asset_risks.get(asset.id, {})
        asset_node_id = f"asset_{asset.id}"
        G.add_node(
            asset_node_id,
            id=asset_node_id,
            raw_id=asset.id,
            name=asset.name,
            type="asset",
            asset_type=asset.asset_type,
            criticality=asset.criticality,
            risk_score=risk_info.get("risk_score", 0.0),
            risk_level=risk_info.get("risk_level", "Low"),
            internet_exposed=asset.internet_exposed,
            financial_value=asset.financial_value,
            estimated_financial_exposure=risk_info.get("estimated_financial_exposure", 0.0),
            risk_drivers=risk_info.get("risk_drivers", []),
            open_vulnerabilities_count=risk_info.get("open_vulnerabilities_count", 0),
            residual_risk=risk_info.get("residual_risk", 1.0),
        )

        # Connect asset to parent Business Service
        bs_node_id = f"bs_{asset.business_service_id}"
        G.add_edge(asset_node_id, bs_node_id, relationship="SUPPORTS")

        # Connect Internet to internet-exposed assets
        if asset.internet_exposed:
            G.add_edge("Internet", asset_node_id, relationship="EXPOSES")

    # 4. Logical Topological Connections between Assets
    for src_name, dst_name in ASSET_TOPOLOGY_CONNECTIONS:
        src_id = asset_name_to_id.get(src_name)
        dst_id = asset_name_to_id.get(dst_name)
        if src_id and dst_id:
            G.add_edge(f"asset_{src_id}", f"asset_{dst_id}", relationship="CONNECTS_TO")

    # 5. Security Controls
    security_controls = db.query(SecurityControl).all()
    for sc in security_controls:
        ctrl_node_id = f"ctrl_{sc.id}"
        G.add_node(
            ctrl_node_id,
            id=ctrl_node_id,
            name=sc.name,
            type="security_control",
            control_type=sc.control_type,
            criticality="N/A",
            risk_score=0.0,
            internet_exposed=False,
            financial_value=sc.implementation_cost,
            effectiveness=sc.effectiveness,
            status=sc.status,
        )

        if sc.asset_id:
            asset_node_id = f"asset_{sc.asset_id}"
            if G.has_node(asset_node_id):
                G.add_edge(ctrl_node_id, asset_node_id, relationship="PROTECTS")

    return G
