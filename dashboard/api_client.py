import os
import requests
from typing import Dict, Any, List, Optional

DEFAULT_URL = "https://cyber-twin-rx.vercel.app"
API_BASE_URL = os.getenv("CYBERTWIN_API_URL", DEFAULT_URL).rstrip("/")
BASE_URL = API_BASE_URL


class APIClient:
    def __init__(self, base_url: str = None):
        if base_url:
            self.base_url = base_url.rstrip("/")
        else:
            self.base_url = os.getenv("CYBERTWIN_API_URL", DEFAULT_URL).rstrip("/")

    def check_health(self) -> bool:
        try:
            r = requests.get(f"{self.base_url}/health", timeout=15)
            return r.status_code == 200
        except Exception:
            return False

    def get_business_services(self) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"{self.base_url}/api/business-services", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching business services: {e}")
            return []

    def get_assets(self) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"{self.base_url}/api/assets", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching assets: {e}")
            return []

    def get_vulnerabilities(self) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"{self.base_url}/api/vulnerabilities", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching vulnerabilities: {e}")
            return []

    def get_security_controls(self) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"{self.base_url}/api/security-controls", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching security controls: {e}")
            return []

    def get_risk_summary(self) -> Dict[str, Any]:
        try:
            r = requests.get(f"{self.base_url}/api/risk/summary", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching risk summary: {e}")
            return {}

    def get_assets_risk(self) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"{self.base_url}/api/risk/assets", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching assets risk: {e}")
            return []

    def get_top_assets_risk(self, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"{self.base_url}/api/risk/top-assets?limit={limit}", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching top assets risk: {e}")
            return []

    def get_digital_twin_graph(self) -> Dict[str, List[Dict[str, Any]]]:
        try:
            r = requests.get(f"{self.base_url}/api/digital-twin/graph", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching digital twin graph: {e}")
            return {"nodes": [], "edges": []}

    def get_attack_paths(self) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"{self.base_url}/api/attack-paths", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching attack paths: {e}")
            return []

    def get_top_attack_path(self) -> Dict[str, Any]:
        try:
            r = requests.get(f"{self.base_url}/api/attack-paths/top", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching top attack path: {e}")
            return {}

    def optimize_investment(self, budget: float) -> Dict[str, Any]:
        try:
            r = requests.post(f"{self.base_url}/api/optimizer/recommend", json={"budget": budget}, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error in investment optimization: {e}")
            return {}

    def simulate_what_if(
        self, asset_id: int, control_type: str, effectiveness: float = 0.80, patch_cve_id: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            payload = {
                "asset_id": asset_id,
                "control_type": control_type,
                "effectiveness": effectiveness,
            }
            if patch_cve_id:
                payload["patch_cve_id"] = patch_cve_id
            r = requests.post(f"{self.base_url}/api/simulation/what-if", json=payload, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error running what-if simulation: {e}")
            return {}

    def simulate_portfolio(self, controls: List[Dict[str, Any]]) -> Dict[str, Any]:
        try:
            r = requests.post(f"{self.base_url}/api/simulation/portfolio", json={"controls": controls}, timeout=30)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error running portfolio simulation: {e}")
            return {}

    def get_ai_status(self) -> Dict[str, Any]:
        try:
            r = requests.get(f"{self.base_url}/api/ai/status", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching AI status: {e}")
            return {"loaded": False}

    def get_ml_status(self) -> Dict[str, Any]:
        return self.get_ai_status()

    def get_top_ml_threats(self, limit: int = 5) -> List[Dict[str, Any]]:
        try:
            r = requests.get(f"{self.base_url}/api/ai/top-threats?limit={limit}", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching top ML threats: {e}")
            return []

    def get_ml_prediction(self, vulnerability_id: int) -> Dict[str, Any]:
        try:
            r = requests.get(f"{self.base_url}/api/ai/vulnerabilities/{vulnerability_id}", timeout=15)
            r.raise_for_status()
            return r.json()
        except Exception as e:
            print(f"Error fetching ML prediction for vuln {vulnerability_id}: {e}")
            return {}

