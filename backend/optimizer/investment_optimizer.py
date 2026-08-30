from typing import List, Dict, Any, Optional
from ortools.linear_solver import pywraplp


def optimize_security_investments(
    candidate_controls: List[Dict[str, Any]],
    asset_map: Dict[int, Dict[str, Any]],
    total_enterprise_exposure: float,
    budget: float,
) -> Dict[str, Any]:
    """
    Solves 0-1 Knapsack / MIP optimization using Google OR-Tools.
    Maximizes Estimated Risk Reduction subject to Total Cost <= Budget.
    """
    if budget <= 0:
        raise ValueError("Budget must be greater than zero.")

    # Filter candidates with valid cost > 0 and status in (Planned, Inactive)
    valid_candidates = []
    for c in candidate_controls:
        status_str = str(c.get("status", "")).strip().title()
        if status_str not in ("Planned", "Inactive"):
            continue
        cost = float(c.get("implementation_cost", 0.0))
        eff = float(c.get("effectiveness", 0.0))

        if cost > 0 and eff > 0:
            asset_id = c.get("asset_id")
            if asset_id and asset_id in asset_map:
                asset_info = asset_map[asset_id]
                asset_exp = float(asset_info.get("estimated_financial_exposure", 0.0))
                asset_val = float(asset_info.get("financial_value", 0.0))
                # Risk reduction target
                exposure_target = max(asset_exp, asset_val * 0.15)
                risk_reduction = exposure_target * eff * 0.75
            else:
                # Global/Enterprise control
                risk_reduction = total_enterprise_exposure * eff * 0.20

            valid_candidates.append({
                "id": c["id"],
                "name": c["name"],
                "control_type": c.get("control_type", "General"),
                "asset_id": asset_id,
                "asset_name": asset_map[asset_id]["asset_name"] if (asset_id and asset_id in asset_map) else "Enterprise-wide",
                "cost": cost,
                "effectiveness": eff,
                "estimated_risk_reduction": round(max(risk_reduction, 0.0), 2),
            })

    if not valid_candidates:
        return {
            "selected_controls": [],
            "total_investment": 0.0,
            "remaining_budget": budget,
            "total_risk_reduction": 0.0,
        }

    # Build OR-Tools MIP Solver
    solver = pywraplp.Solver.CreateSolver("CBC")
    if not solver:
        solver = pywraplp.Solver.CreateSolver("SCIP")

    if not solver:
        # Fallback to deterministic greedy knapsack by risk reduction per cost ratio if MIP solver unavailable
        valid_candidates.sort(key=lambda x: (x["estimated_risk_reduction"] / x["cost"]), reverse=True)
        selected = []
        spent = 0.0
        for cand in valid_candidates:
            if spent + cand["cost"] <= budget:
                selected.append(cand)
                spent += cand["cost"]
        return {
            "selected_controls": selected,
            "total_investment": spent,
            "remaining_budget": budget - spent,
            "total_risk_reduction": sum(c["estimated_risk_reduction"] for c in selected),
        }

    # Binary variables x_i in {0, 1}
    x_vars = {}
    for i, cand in enumerate(valid_candidates):
        x_vars[i] = solver.BoolVar(f"x_{cand['id']}")

    # Constraint: sum(cost_i * x_i) <= budget
    budget_constraint = solver.Constraint(0, budget, "budget_constraint")
    for i, cand in enumerate(valid_candidates):
        budget_constraint.SetCoefficient(x_vars[i], cand["cost"])

    # Objective: maximize sum(risk_reduction_i * x_i)
    objective = solver.Objective()
    for i, cand in enumerate(valid_candidates):
        objective.SetCoefficient(x_vars[i], cand["estimated_risk_reduction"])
    objective.SetMaximization()

    status = solver.Solve()

    selected_controls = []
    total_investment = 0.0

    if status in (pywraplp.Solver.OPTIMAL, pywraplp.Solver.FEASIBLE):
        for i, cand in enumerate(valid_candidates):
            if x_vars[i].solution_value() > 0.5:
                selected_controls.append(cand)
                total_investment += cand["cost"]

    total_investment = round(total_investment, 2)
    remaining_budget = round(max(budget - total_investment, 0.0), 2)
    total_risk_reduction = round(sum(c["estimated_risk_reduction"] for c in selected_controls), 2)

    return {
        "selected_controls": selected_controls,
        "total_investment": total_investment,
        "remaining_budget": remaining_budget,
        "total_risk_reduction": total_risk_reduction,
    }
