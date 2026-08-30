from typing import Dict, Any, List
import pandas as pd
from sqlalchemy.orm import Session

from backend.models.vulnerability import Vulnerability
from backend.models.asset import Asset
from backend.models.business_service import BusinessService
from backend.models.security_control import SecurityControl

CRITICALITY_MAP = {
    "low": 0,
    "moderate": 1,
    "medium": 1,
    "high": 2,
    "critical": 3,
}

FEATURE_COLUMNS = [
    "cvss_score",
    "epss_score",
    "kev_status",
    "internet_exposed",
    "patch_available",
    "asset_criticality",
    "control_effectiveness",
    "open_vulnerability_count",
    "high_vulnerability_count",
    "business_criticality",
]


def extract_features_from_vulnerability(vuln: Vulnerability, db: Session = None) -> Dict[str, Any]:
    """
    Extracts numerical features for ML prediction from a database Vulnerability object.
    Matches the exact 10 features used during model training.
    """
    asset: Asset = vuln.asset

    # 1. CVSS score
    cvss_score = float(vuln.cvss_score) if vuln.cvss_score is not None else 5.0

    # 2. EPSS score
    epss_score = float(vuln.epss_score) if vuln.epss_score is not None else 0.0

    # 3. KEV status
    kev_status = 1 if vuln.kev_status else 0

    # 4. Internet exposed
    internet_exposed = 1 if (asset and asset.internet_exposed) else 0

    # 5. Patch available
    patch_available = 1 if vuln.patch_available else 0

    # 6. Asset criticality
    asset_crit_str = asset.criticality.lower() if (asset and asset.criticality) else "medium"
    asset_criticality = CRITICALITY_MAP.get(asset_crit_str, 1)

    # 7. Combined Control Effectiveness (Active controls on asset)
    control_eff = 0.0
    if asset and asset.security_controls:
        active_controls = [c for c in asset.security_controls if str(c.status).lower() == "active"]
        if active_controls:
            rem_risk = 1.0
            for c in active_controls:
                eff = float(c.effectiveness)
                rem_risk *= (1.0 - eff)
            control_eff = round(1.0 - rem_risk, 4)

    # 8. Open vulnerability count & 9. High vulnerability count on asset
    open_vuln_count = 0
    high_vuln_count = 0
    if asset and asset.vulnerabilities:
        for v in asset.vulnerabilities:
            if str(v.status).lower() == "open":
                open_vuln_count += 1
                if float(v.cvss_score) >= 7.0:
                    high_vuln_count += 1
    else:
        open_vuln_count = 1
        if cvss_score >= 7.0:
            high_vuln_count = 1

    # 10. Business criticality
    biz_crit_str = "medium"
    if asset and asset.business_service and asset.business_service.criticality:
        biz_crit_str = asset.business_service.criticality.lower()
    business_criticality = CRITICALITY_MAP.get(biz_crit_str, 1)

    features = {
        "cvss_score": cvss_score,
        "epss_score": epss_score,
        "kev_status": kev_status,
        "internet_exposed": internet_exposed,
        "patch_available": patch_available,
        "asset_criticality": asset_criticality,
        "control_effectiveness": control_eff,
        "open_vulnerability_count": open_vuln_count,
        "high_vulnerability_count": high_vuln_count,
        "business_criticality": business_criticality,
    }

    return features


def features_to_dataframe(features: Dict[str, Any]) -> pd.DataFrame:
    """
    Converts feature dictionary to single-row DataFrame with exact training column order.
    """
    return pd.DataFrame([features])[FEATURE_COLUMNS]
