import networkx as nx
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from backend.digital_twin.graph_builder import build_digital_twin_graph


def find_attack_paths(db: Session) -> List[Dict[str, Any]]:
    G = build_digital_twin_graph(db)

    # Filter subgraph of Internet and Asset nodes with CONNECTS_TO and EXPOSES relationships
    asset_subgraph = nx.DiGraph()

    for n, attrs in G.nodes(data=True):
        if attrs.get("type") in ("internet", "asset"):
            asset_subgraph.add_node(n, **attrs)

    for u, v, attrs in G.edges(data=True):
        rel = attrs.get("relationship")
        if rel in ("EXPOSES", "CONNECTS_TO"):
            if asset_subgraph.has_node(u) and asset_subgraph.has_node(v):
                asset_subgraph.add_edge(u, v, **attrs)

    # Entry nodes: Internet node or internet-exposed asset nodes
    start_node = "Internet"
    if not asset_subgraph.has_node(start_node):
        return []

    # Target nodes: Databases or Critical assets that are not directly internet exposed
    targets = []
    for n, attrs in asset_subgraph.nodes(data=True):
        if n == start_node:
            continue
        asset_type = str(attrs.get("asset_type", "")).lower()
        criticality = str(attrs.get("criticality", "")).lower()
        fin_val = float(attrs.get("financial_value", 0.0))

        # Critical target assets: Databases, or Critical assets with financial value >= 20,000,000
        if "database" in asset_type or criticality == "critical" or fin_val >= 25000000.0:
            targets.append(n)

    attack_paths = []

    for target in targets:
        if not asset_subgraph.has_node(target):
            continue
        try:
            simple_paths = list(nx.all_simple_paths(asset_subgraph, source=start_node, target=target, cutoff=6))
        except (nx.NetworkXNoPath, nx.NodeNotFound):
            continue

        for p in simple_paths:
            if len(p) < 2:
                continue

            path_names = [asset_subgraph.nodes[node_id].get("name", str(node_id)) for node_id in p]
            
            # Gather metrics along path
            node_scores = []
            exposures = []
            weakest_points_set = set()

            for node_id in p:
                attrs = asset_subgraph.nodes[node_id]
                node_type = attrs.get("type")
                if node_type == "internet":
                    continue

                r_score = float(attrs.get("risk_score", 0.0))
                fin_exp = float(attrs.get("estimated_financial_exposure", 0.0))
                fin_val = float(attrs.get("financial_value", 0.0))
                drivers = attrs.get("risk_drivers", [])

                node_scores.append(r_score)
                exposures.append(max(fin_exp, fin_val * 0.1))

                # Identify weakest points
                if attrs.get("internet_exposed"):
                    weakest_points_set.add(f"Exposed entry system ({attrs.get('name')})")
                for d in drivers:
                    if d in ("High CVSS vulnerability", "High EPSS", "Known exploited vulnerability", "Missing patch", "Weak security control coverage"):
                        weakest_points_set.add(f"{d} on {attrs.get('name')}")

            if not node_scores:
                continue

            max_score = max(node_scores)
            avg_score = sum(node_scores) / len(node_scores)
            path_score = round(min(max(0.65 * max_score + 0.35 * avg_score, 0.0), 100.0), 2)

            # Exposure for path is driven by target asset's financial value plus entry risk
            target_attrs = asset_subgraph.nodes[p[-1]]
            target_financial_val = float(target_attrs.get("financial_value", 0.0))
            potential_exposure = round(max(target_financial_val * (path_score / 100.0), sum(exposures)), 2)

            weakest_list = list(weakest_points_set)
            if not weakest_list:
                weakest_list = ["Weak network segmentation", "Direct logical access route"]

            attack_paths.append({
                "path": path_names,
                "path_nodes": p,
                "path_score": path_score,
                "potential_financial_exposure": potential_exposure,
                "target_asset": target_attrs.get("name"),
                "entry_asset": path_names[1] if len(path_names) > 1 else path_names[0],
                "hop_count": len(p) - 1,
                "weakest_points": weakest_list,
            })

    # Sort attack paths so that meaningful multi-hop paths (hop_count >= 2) ending at Databases/Critical targets are prioritized
    def path_priority_key(p):
        hop_count = p.get("hop_count", 0)
        is_multi_hop = 1 if hop_count >= 2 else 0
        target_name = str(p.get("target_asset", "")).lower()
        is_database = 1 if ("db" in target_name or "database" in target_name) else 0
        return (is_multi_hop, is_database, p["path_score"], p["potential_financial_exposure"])

    attack_paths.sort(key=path_priority_key, reverse=True)
    return attack_paths



def get_top_attack_path(db: Session) -> Dict[str, Any]:
    paths = find_attack_paths(db)
    if paths:
        return paths[0]
    return {
        "path": [],
        "path_nodes": [],
        "path_score": 0.0,
        "potential_financial_exposure": 0.0,
        "target_asset": "N/A",
        "entry_asset": "N/A",
        "hop_count": 0,
        "weakest_points": ["No attack paths detected"],
    }
