import copy
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models import Asset, Vulnerability, SecurityControl
from backend.risk_engine.service import get_asset_risk_by_id, get_all_assets_risk, get_enterprise_risk_summary
from backend.risk_engine.calculator import calculate_asset_risk_details, calculate_combined_control_effectiveness


def simulate_single_asset_improvement(
    asset_id: int,
    control_type: str,
    effectiveness: float,
    patch_cve_id: Optional[str] = None,
    db: Session = None,
) -> Dict[str, Any]:
    current_risk = get_asset_risk_by_id(asset_id, db)
    if not current_risk:
        raise ValueError(f"Asset with id {asset_id} not found.")

    asset = db.query(Asset).filter(Asset.id == asset_id).first()

    # Clone in-memory lists
    sim_vulns = [
        {
            "id": v.id,
            "cve_id": v.cve_id,
            "cvss_score": v.cvss_score,
            "epss_score": v.epss_score,
            "kev_status": v.kev_status,
            "patch_available": v.patch_available,
            "status": v.status,
        }
        for v in asset.vulnerabilities
    ]
    sim_controls = [
        {
            "id": c.id,
            "name": c.name,
            "control_type": c.control_type,
            "effectiveness": c.effectiveness,
            "implementation_cost": c.implementation_cost,
            "status": c.status,
        }
        for c in asset.security_controls
    ]

    scenario_label = control_type

    # Apply improvement in memory
    ctrl_type_lower = control_type.lower()
    if "patch" in ctrl_type_lower:
        # Patch vulnerability
        open_vulns = [v for v in sim_vulns if v["status"].lower() == "open"]
        if patch_cve_id:
            for v in sim_vulns:
                if v["cve_id"].lower() == patch_cve_id.lower():
                    v["status"] = "Patched"
                    scenario_label = f"Patched {v['cve_id']}"
        elif open_vulns:
            # Patch highest CVSS vulnerability
            highest_v = max(open_vulns, key=lambda x: x["cvss_score"])
            highest_v["status"] = "Patched"
            scenario_label = f"Patched {highest_v['cve_id']} ({highest_v.get('title', 'Vulnerability')})"
    else:
        # Add new/improved security control in memory
        eff = min(max(float(effectiveness), 0.0), 1.0)
        sim_controls.append({
            "id": -1,
            "name": f"Simulated {control_type}",
            "control_type": control_type,
            "effectiveness": eff,
            "implementation_cost": 0.0,
            "status": "Active",
        })
        scenario_label = f"Implement {control_type} (Effectiveness: {int(eff * 100)}%)"

    # Recalculate risk on cloned data
    simulated_risk = calculate_asset_risk_details(
        asset_id=asset.id,
        asset_name=asset.name,
        asset_type=asset.asset_type,
        criticality=asset.criticality,
        financial_value=asset.financial_value,
        internet_exposed=asset.internet_exposed,
        vulnerabilities=sim_vulns,
        security_controls=sim_controls,
    )

    curr_score = current_risk["risk_score"]
    sim_score = simulated_risk["risk_score"]
    score_reduction = round(max(curr_score - sim_score, 0.0), 2)

    curr_exp = current_risk["estimated_financial_exposure"]
    sim_exp = simulated_risk["estimated_financial_exposure"]
    exp_reduction = round(max(curr_exp - sim_exp, 0.0), 2)

    pct_reduction = round((score_reduction / curr_score * 100.0), 2) if curr_score > 0 else 0.0

    return {
        "asset_id": asset_id,
        "asset_name": asset.name,
        "scenario": scenario_label,
        "current_risk_score": curr_score,
        "simulated_risk_score": sim_score,
        "risk_score_reduction": score_reduction,
        "current_financial_exposure": curr_exp,
        "simulated_financial_exposure": sim_exp,
        "estimated_financial_risk_reduction": exp_reduction,
        "percentage_reduction": pct_reduction,
    }


def simulate_portfolio_improvements(
    simulated_controls: List[Dict[str, Any]],
    db: Session,
) -> Dict[str, Any]:
    summary_before = get_enterprise_risk_summary(db)
    assets = db.query(Asset).all()

    # Build initial state map
    asset_state = {}
    for asset in assets:
        asset_state[asset.id] = {
            "asset": asset,
            "vulns": [
                {
                    "id": v.id,
                    "cve_id": v.cve_id,
                    "cvss_score": v.cvss_score,
                    "epss_score": v.epss_score,
                    "kev_status": v.kev_status,
                    "patch_available": v.patch_available,
                    "status": v.status,
                }
                for v in asset.vulnerabilities
            ],
            "controls": [
                {
                    "id": c.id,
                    "name": c.name,
                    "control_type": c.control_type,
                    "effectiveness": c.effectiveness,
                    "implementation_cost": c.implementation_cost,
                    "status": c.status,
                }
                for c in asset.security_controls
            ],
        }

    # Apply portfolio control improvements in memory
    for item in simulated_controls:
        target_asset_id = item.get("asset_id")
        ctrl_type = str(item.get("control_type", item.get("name", "Security Improvement")))
        eff = float(item.get("effectiveness", 0.80))

        if target_asset_id and target_asset_id in asset_state:
            # Apply to specific asset
            if "patch" in ctrl_type.lower():
                for v in asset_state[target_asset_id]["vulns"]:
                    if v["status"].lower() == "open":
                        v["status"] = "Patched"
            else:
                asset_state[target_asset_id]["controls"].append({
                    "id": -1,
                    "name": f"Simulated {ctrl_type}",
                    "control_type": ctrl_type,
                    "effectiveness": eff,
                    "implementation_cost": 0.0,
                    "status": "Active",
                })
        else:
            # Global control: apply to all internet exposed / critical assets
            for aid, state in asset_state.items():
                if state["asset"].internet_exposed or state["asset"].criticality in ("Critical", "High"):
                    state["controls"].append({
                        "id": -1,
                        "name": f"Simulated Enterprise {ctrl_type}",
                        "control_type": ctrl_type,
                        "effectiveness": eff * 0.7,
                        "implementation_cost": 0.0,
                        "status": "Active",
                    })

    # Recalculate enterprise risk after simulation
    sim_asset_risks = []
    for aid, state in asset_state.items():
        a = state["asset"]
        r = calculate_asset_risk_details(
            asset_id=a.id,
            asset_name=a.name,
            asset_type=a.asset_type,
            criticality=a.criticality,
            financial_value=a.financial_value,
            internet_exposed=a.internet_exposed,
            vulnerabilities=state["vulns"],
            security_controls=state["controls"],
        )
        sim_asset_risks.append(r)

    total_assets = len(sim_asset_risks)
    avg_risk_before = summary_before["average_risk_score"]
    exp_before = summary_before["total_financial_exposure"]

    avg_risk_after = round(sum(r["risk_score"] for r in sim_asset_risks) / total_assets, 2) if total_assets > 0 else 0.0
    exp_after = round(sum(r["estimated_financial_exposure"] for r in sim_asset_risks), 2)
    est_reduction = round(max(exp_before - exp_after, 0.0), 2)

    return {
        "enterprise_risk_before": avg_risk_before,
        "enterprise_risk_after": avg_risk_after,
        "financial_exposure_before": exp_before,
        "financial_exposure_after": exp_after,
        "estimated_reduction": est_reduction,
    }
