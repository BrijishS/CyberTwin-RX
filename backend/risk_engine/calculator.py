import math
from typing import List, Dict, Any

CRITICALITY_MULTIPLIER = {
    "Low": 0.25,
    "Medium": 0.50,
    "High": 0.75,
    "Critical": 1.00,
}


def get_criticality_multiplier(criticality: str) -> float:
    return CRITICALITY_MULTIPLIER.get(criticality, 0.50)


def calculate_vulnerability_likelihood(
    cvss_score: float,
    epss_score: float,
    internet_exposed: bool,
    kev_status: bool,
    patch_available: bool,
    status: str = "Open",
) -> float:
    """
    likelihood =
        0.50 * epss
      + 0.25 * severity (cvss / 10)
      + 0.15 * internet_exposure_factor
      + 0.10 * kev_factor
      + (0.05 if patch available but open)
    Clamped to 0.0 - 1.0.
    """
    severity = min(max(cvss_score / 10.0, 0.0), 1.0)
    internet_factor = 1.0 if internet_exposed else 0.0
    kev_factor = 1.0 if kev_status else 0.0
    patch_urgency = 0.05 if (patch_available and str(status).lower() == "open") else 0.0

    likelihood = (
        0.50 * epss_score
        + 0.25 * severity
        + 0.15 * internet_factor
        + 0.10 * kev_factor
        + patch_urgency
    )
    return round(min(max(likelihood, 0.0), 1.0), 4)


def calculate_vulnerability_risk_score(likelihood: float) -> float:
    return round(likelihood * 100.0, 2)


def calculate_combined_control_effectiveness(effectiveness_list: List[float]) -> float:
    """
    Combine active control effectiveness: 1 - prod(1 - effectiveness).
    Capped at 0.90. Residual risk is always at least 0.10.
    """
    if not effectiveness_list:
        return 0.0
    prod = 1.0
    for eff in effectiveness_list:
        eff_clamped = min(max(eff, 0.0), 1.0)
        prod *= (1.0 - eff_clamped)
    combined = 1.0 - prod
    return round(min(combined, 0.90), 4)


def determine_risk_level(score: float) -> str:
    if score <= 20.0:
        return "Low"
    elif score <= 40.0:
        return "Moderate"
    elif score <= 60.0:
        return "Medium"
    elif score <= 80.0:
        return "High"
    else:
        return "Critical"


def calculate_asset_risk_details(
    asset_id: int,
    asset_name: str,
    asset_type: str,
    criticality: str,
    financial_value: float,
    internet_exposed: bool,
    vulnerabilities: List[Dict[str, Any]],
    security_controls: List[Dict[str, Any]],
) -> Dict[str, Any]:
    criticality_mult = get_criticality_multiplier(criticality)

    # Filter active controls
    active_controls = [c for c in security_controls if str(c.get("status", "")).lower() == "active"]
    ctrl_eff_list = [float(c.get("effectiveness", 0.0)) for c in active_controls]
    combined_ctrl_eff = calculate_combined_control_effectiveness(ctrl_eff_list)
    residual_risk = round(1.0 - combined_ctrl_eff, 4)

    # Filter open vulnerabilities
    open_vulns = [v for v in vulnerabilities if str(v.get("status", "")).lower() == "open"]

    vuln_likelihoods = []
    has_high_cvss = False
    has_high_epss = False
    has_kev = False
    has_missing_patch = False

    for v in open_vulns:
        cvss = float(v.get("cvss_score", 0.0))
        epss = float(v.get("epss_score", 0.0))
        kev = bool(v.get("kev_status", False))
        patch = bool(v.get("patch_available", False))
        v_status = str(v.get("status", "Open"))

        if cvss >= 7.0:
            has_high_cvss = True
        if epss >= 0.2:
            has_high_epss = True
        if kev:
            has_kev = True
        if patch:
            has_missing_patch = True

        lh = calculate_vulnerability_likelihood(
            cvss_score=cvss,
            epss_score=epss,
            internet_exposed=internet_exposed,
            kev_status=kev,
            patch_available=patch,
            status=v_status,
        )
        vuln_likelihoods.append(lh)

    if vuln_likelihoods:
        max_lh = max(vuln_likelihoods)
        avg_lh = sum(vuln_likelihoods) / len(vuln_likelihoods)
        overall_likelihood = round(0.7 * max_lh + 0.3 * avg_lh, 4)
    else:
        overall_likelihood = 0.05 if internet_exposed else 0.01

    # Asset risk score formula (0 - 100)
    base_score = (
        0.55 * overall_likelihood +
        0.25 * criticality_mult +
        0.20 * (1.0 if internet_exposed else 0.0)
    ) * 100.0

    # Apply residual risk factor (min 0.10, max 1.0)
    final_score = round(min(max(base_score * (0.4 + 0.6 * residual_risk), 0.0), 100.0), 2)
    risk_level = determine_risk_level(final_score)

    # Financial Exposure:
    # estimated_exposure = financial_value * probability_of_loss * criticality_impact * residual_risk
    financial_exposure = round(
        max(financial_value * overall_likelihood * criticality_mult * residual_risk, 0.0),
        2
    )

    # Risk Drivers
    risk_drivers = []
    if internet_exposed:
        risk_drivers.append("Internet exposed")
    if criticality in ("Critical", "High"):
        risk_drivers.append("Critical business asset")
    if has_high_cvss:
        risk_drivers.append("High CVSS vulnerability")
    if has_high_epss:
        risk_drivers.append("High EPSS")
    if has_kev:
        risk_drivers.append("Known exploited vulnerability")
    if has_missing_patch:
        risk_drivers.append("Missing patch")
    if combined_ctrl_eff < 0.5:
        risk_drivers.append("Weak security control coverage")
    if len(open_vulns) > 1:
        risk_drivers.append("Multiple open vulnerabilities")

    return {
        "asset_id": asset_id,
        "asset_name": asset_name,
        "asset_type": asset_type,
        "criticality": criticality,
        "financial_value": financial_value,
        "internet_exposed": internet_exposed,
        "open_vulnerabilities_count": len(open_vulns),
        "active_controls_count": len(active_controls),
        "combined_control_effectiveness": combined_ctrl_eff,
        "residual_risk": residual_risk,
        "overall_likelihood": overall_likelihood,
        "risk_score": final_score,
        "risk_level": risk_level,
        "estimated_financial_exposure": financial_exposure,
        "risk_drivers": risk_drivers,
    }
