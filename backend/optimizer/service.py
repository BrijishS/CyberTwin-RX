from typing import Dict, Any, List
from sqlalchemy.orm import Session

from backend.models import SecurityControl, Asset
from backend.risk_engine.service import get_all_assets_risk, get_enterprise_risk_summary
from backend.optimizer.investment_optimizer import optimize_security_investments


def recommend_security_investments(db: Session, budget: float) -> Dict[str, Any]:
    if budget <= 0:
        raise ValueError("Budget must be greater than zero.")

    # Fetch enterprise risk baseline
    summary_before = get_enterprise_risk_summary(db)
    asset_risks = get_all_assets_risk(db)
    asset_map = {a["asset_id"]: a for a in asset_risks}
    total_exposure = summary_before["total_financial_exposure"]

    # Fetch candidate security controls (only Planned or Inactive controls are eligible for investment)
    all_controls = db.query(SecurityControl).all()
    candidates = [
        {
            "id": c.id,
            "name": c.name,
            "control_type": c.control_type,
            "asset_id": c.asset_id,
            "effectiveness": c.effectiveness,
            "implementation_cost": c.implementation_cost,
            "status": c.status,
        }
        for c in all_controls
        if str(c.status).strip().title() in ("Planned", "Inactive")
    ]


    opt_result = optimize_security_investments(
        candidate_controls=candidates,
        asset_map=asset_map,
        total_enterprise_exposure=total_exposure,
        budget=budget,
    )

    selected_raw = opt_result["selected_controls"]
    total_investment = opt_result["total_investment"]
    remaining_budget = opt_result["remaining_budget"]

    # Format each selected control and calculate ROSI
    selected_controls = []
    total_risk_reduction = 0.0

    for item in selected_raw:
        cost = item["cost"]
        rr = item["estimated_risk_reduction"]
        rosi = round(((rr - cost) / cost) * 100.0, 2) if cost > 0 else 0.0

        selected_controls.append({
            "id": item["id"],
            "name": item["name"],
            "control_type": item["control_type"],
            "asset": item["asset_name"],
            "asset_id": item["asset_id"],
            "cost": cost,
            "effectiveness": item["effectiveness"],
            "estimated_risk_reduction": rr,
            "rosi": rosi,
        })
        total_risk_reduction += rr

    total_risk_reduction = round(total_risk_reduction, 2)

    # Compute Portfolio ROSI
    if total_investment > 0:
        portfolio_rosi = round(((total_risk_reduction - total_investment) / total_investment) * 100.0, 2)
    else:
        portfolio_rosi = 0.0

    risk_before = summary_before["average_risk_score"]
    
    # Calculate estimated risk score after investment
    # Reduction proportion based on financial exposure reduction
    if total_exposure > 0:
        reduction_ratio = min(total_risk_reduction / total_exposure, 0.85)
    else:
        reduction_ratio = 0.0

    estimated_risk_after = round(max(risk_before * (1.0 - 0.7 * reduction_ratio), 5.0), 2)

    return {
        "available_budget": round(budget, 2),
        "selected_controls": selected_controls,
        "total_investment": total_investment,
        "remaining_budget": remaining_budget,
        "estimated_risk_reduction": total_risk_reduction,
        "risk_before": risk_before,
        "estimated_risk_after": estimated_risk_after,
        "portfolio_rosi": portfolio_rosi,
    }
