from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from backend.models import Asset, Vulnerability, SecurityControl
from backend.risk_engine.calculator import calculate_asset_risk_details


def _format_asset_for_calc(asset: Asset) -> Dict[str, Any]:
    vulns = [
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
    controls = [
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
    return calculate_asset_risk_details(
        asset_id=asset.id,
        asset_name=asset.name,
        asset_type=asset.asset_type,
        criticality=asset.criticality,
        financial_value=asset.financial_value,
        internet_exposed=asset.internet_exposed,
        vulnerabilities=vulns,
        security_controls=controls,
    )


def get_all_assets_risk(db: Session) -> List[Dict[str, Any]]:
    assets = db.query(Asset).all()
    results = [_format_asset_for_calc(a) for a in assets]
    results.sort(key=lambda x: x["risk_score"], reverse=True)
    return results


def get_asset_risk_by_id(asset_id: int, db: Session) -> Optional[Dict[str, Any]]:
    asset = db.query(Asset).filter(Asset.id == asset_id).first()
    if not asset:
        return None
    return _format_asset_for_calc(asset)


def get_top_risky_assets(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
    all_risks = get_all_assets_risk(db)
    return all_risks[:limit]


def get_enterprise_risk_summary(db: Session) -> Dict[str, Any]:
    all_risks = get_all_assets_risk(db)
    total_assets = len(all_risks)
    total_vulnerabilities = db.query(Vulnerability).count()
    
    critical_assets = sum(1 for a in all_risks if a["risk_level"] == "Critical")
    high_risk_assets = sum(1 for a in all_risks if a["risk_level"] in ("High", "Critical"))
    
    total_exposure = sum(a["estimated_financial_exposure"] for a in all_risks)
    avg_score = (sum(a["risk_score"] for a in all_risks) / total_assets) if total_assets > 0 else 0.0

    return {
        "total_assets": total_assets,
        "total_vulnerabilities": total_vulnerabilities,
        "critical_assets": critical_assets,
        "high_risk_assets": high_risk_assets,
        "average_risk_score": round(avg_score, 2),
        "total_financial_exposure": round(total_exposure, 2),
    }
