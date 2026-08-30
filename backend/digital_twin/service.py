from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.digital_twin.graph_builder import build_digital_twin_graph


def get_digital_twin_data(db: Session) -> Dict[str, List[Dict[str, Any]]]:
    G = build_digital_twin_graph(db)

    nodes = []
    for n, attrs in G.nodes(data=True):
        node_dict = {
            "id": str(n),
            "name": attrs.get("name", str(n)),
            "type": attrs.get("type", "unknown"),
            "criticality": attrs.get("criticality", "N/A"),
            "risk_score": attrs.get("risk_score", 0.0),
            "internet_exposed": attrs.get("internet_exposed", False),
            "financial_value": attrs.get("financial_value", 0.0),
        }
        # Include extra fields if present
        if "asset_type" in attrs:
            node_dict["asset_type"] = attrs["asset_type"]
        if "risk_level" in attrs:
            node_dict["risk_level"] = attrs["risk_level"]
        if "estimated_financial_exposure" in attrs:
            node_dict["estimated_financial_exposure"] = attrs["estimated_financial_exposure"]

        nodes.append(node_dict)

    edges = []
    for u, v, attrs in G.edges(data=True):
        edges.append({
            "source": str(u),
            "target": str(v),
            "relationship": attrs.get("relationship", "CONNECTED_TO"),
        })

    return {
        "nodes": nodes,
        "edges": edges,
    }
