from typing import Dict, Any, List, Optional
from sqlalchemy.orm import Session, joinedload

from backend.models.vulnerability import Vulnerability
from backend.ai.feature_extractor import extract_features_from_vulnerability
from backend.ai.predictor import predictor
from backend.risk_engine.calculator import (
    calculate_vulnerability_likelihood,
    calculate_vulnerability_risk_score,
)


def get_ai_status() -> Dict[str, Any]:
    """Returns AI model loading status and evaluation metrics."""
    return predictor.get_status()


def predict_vulnerability_exploitation(vuln_id: int, db: Session) -> Optional[Dict[str, Any]]:
    """
    Extracts features for a specific DB vulnerability and predicts exploitation probability.
    Also calculates optional AI-Assisted Priority Score.
    """
    vuln = (
        db.query(Vulnerability)
        .options(joinedload(Vulnerability.asset))
        .filter(Vulnerability.id == vuln_id)
        .first()
    )

    if not vuln:
        return None

    # Extract Features & Predict
    features = extract_features_from_vulnerability(vuln, db)
    pred_res = predictor.predict(features)

    # Calculate Deterministic Vulnerability Likelihood & Risk Score for hybrid priority signal
    lh = calculate_vulnerability_likelihood(
        cvss_score=vuln.cvss_score,
        epss_score=vuln.epss_score,
        internet_exposed=vuln.asset.internet_exposed if vuln.asset else False,
        kev_status=vuln.kev_status,
        patch_available=vuln.patch_available,
        status=vuln.status or "Open",
    )
    det_risk = calculate_vulnerability_risk_score(lh)

    # Hybrid AI-Assisted Priority Score: 70% Deterministic Risk + 30% ML Exploitation Percentage
    exploit_pct = pred_res["percentage"]
    ai_priority = round(min(max(0.70 * det_risk + 0.30 * exploit_pct, 0.0), 100.0), 1)

    asset_name = vuln.asset.name if vuln.asset else "Unknown Asset"

    return {
        "vulnerability_id": vuln.id,
        "cve_id": vuln.cve_id,
        "title": vuln.title,
        "asset": asset_name,
        "cvss_score": vuln.cvss_score,
        "epss_score": vuln.epss_score,
        "exploitation_probability": pred_res["exploitation_probability"],
        "percentage": pred_res["percentage"],
        "risk_level": pred_res["risk_level"],
        "confidence": pred_res["confidence"],
        "top_contributing_features": pred_res["top_contributing_features"],
        "deterministic_risk_score": round(det_risk, 1),
        "ai_assisted_priority_score": ai_priority,
    }


def get_top_ml_threats(db: Session, limit: int = 5) -> List[Dict[str, Any]]:
    """
    Returns top N vulnerabilities sorted by ML exploitation probability descending.
    """
    vulnerabilities = (
        db.query(Vulnerability)
        .options(joinedload(Vulnerability.asset))
        .all()
    )

    results = []
    for vuln in vulnerabilities:
        res = predict_vulnerability_exploitation(vuln.id, db)
        if res:
            results.append(res)

    # Sort descending by ML exploitation probability
    results.sort(key=lambda x: x["exploitation_probability"], reverse=True)
    return results[:limit]
