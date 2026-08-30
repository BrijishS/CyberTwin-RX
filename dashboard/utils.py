from typing import Union

RISK_COLORS = {
    "Low": "#16C784",        # Green
    "Moderate": "#AEEA00",   # Lime
    "Medium": "#FFC400",     # Yellow
    "High": "#FF8A00",       # Orange
    "Critical": "#FF3B4F",   # Red
}

THEME_COLORS = {
    "bg_main": "#030913",
    "bg_secondary": "#07111F",
    "bg_panel": "#0A1422",
    "bg_panel_inner": "#0C1828",
    "border_primary": "#12365B",
    "border_cyan": "#009CFF",
    "cyan_accent": "#00D9FF",
    "blue_accent": "#3C82FF",
    "critical": "#FF3B4F",
    "high": "#FF8A00",
    "medium": "#FFC400",
    "low": "#16C784",
    "positive": "#42D66B",
    "purple": "#9C55FF",
    "text_primary": "#F3F7FF",
    "text_secondary": "#94A8C2",
}


def format_currency_inr(value: Union[int, float]) -> str:
    if value is None:
        return "₹0"
    val = float(value)
    if val < 0:
        return f"-₹{format_currency_inr(abs(val))[1:]}"

    if val >= 10000000.0:  # 1 Crore = 10,000,000
        crores = val / 10000000.0
        return f"₹{crores:.2f} Cr"
    elif val >= 100000.0:   # 1 Lakh = 100,000
        lakhs = val / 100000.0
        return f"₹{lakhs:.2f} Lakh"
    else:
        return f"₹{val:,.0f}"


def get_risk_badge(level: str) -> str:
    color = RISK_COLORS.get(level, "#94A8C2")
    return f"""<span style="background-color: {color}22; color: {color}; border: 1px solid {color}; padding: 2px 8px; border-radius: 4px; font-weight: 600; font-size: 0.75rem;">{level}</span>"""


def get_risk_level_from_score(score: float) -> str:
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
