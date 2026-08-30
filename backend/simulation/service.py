from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.simulation.what_if import simulate_single_asset_improvement, simulate_portfolio_improvements


def run_asset_simulation(
    asset_id: int,
    control_type: str,
    effectiveness: float,
    patch_cve_id: Optional[str] = None,
    db: Session = None,
) -> Dict[str, Any]:
    return simulate_single_asset_improvement(
        asset_id=asset_id,
        control_type=control_type,
        effectiveness=effectiveness,
        patch_cve_id=patch_cve_id,
        db=db,
    )


def run_portfolio_simulation(
    simulated_controls: List[Dict[str, Any]],
    db: Session = None,
) -> Dict[str, Any]:
    return simulate_portfolio_improvements(
        simulated_controls=simulated_controls,
        db=db,
    )
