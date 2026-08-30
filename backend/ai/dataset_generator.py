import os
import numpy as np
import pandas as pd

DATASET_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "datasets"))
DATASET_FILE = os.path.join(DATASET_DIR, "ml_training_data.csv")


def generate_synthetic_dataset(num_samples: int = 5000, random_state: int = 42) -> pd.DataFrame:
    """
    Generates a synthetic cybersecurity vulnerability exploitation dataset for prototype validation.
    """
    np.random.seed(random_state)

    # 1. cvss_score: 0.0 to 10.0 (truncated normal distribution around 6.5)
    cvss = np.clip(np.random.normal(loc=6.5, scale=2.2, size=num_samples), 0.0, 10.0)

    # 2. epss_score: 0.0 to 1.0 (beta distribution skewed towards low probabilities)
    epss = np.clip(np.random.beta(a=0.5, b=2.5, size=num_samples), 0.0, 1.0)

    # 3. kev_status: 0 or 1 (~15% positive)
    kev = np.random.choice([0, 1], size=num_samples, p=[0.85, 0.15])

    # 4. internet_exposed: 0 or 1 (~40% positive)
    internet_exposed = np.random.choice([0, 1], size=num_samples, p=[0.60, 0.40])

    # 5. patch_available: 0 or 1 (~70% positive)
    patch_available = np.random.choice([0, 1], size=num_samples, p=[0.30, 0.70])

    # 6. asset_criticality: 0 (Low), 1 (Medium), 2 (High), 3 (Critical)
    asset_crit = np.random.choice([0, 1, 2, 3], size=num_samples, p=[0.2, 0.4, 0.3, 0.1])

    # 7. control_effectiveness: 0.0 to 1.0
    control_eff = np.clip(np.random.normal(loc=0.55, scale=0.25, size=num_samples), 0.0, 1.0)

    # 8. open_vulnerability_count: 0 to 10
    open_vulns = np.random.poisson(lam=2.5, size=num_samples)
    open_vulns = np.clip(open_vulns, 0, 12)

    # 9. high_vulnerability_count: 0 to 5
    high_vulns = np.clip(np.random.poisson(lam=1.0, size=num_samples), 0, 6)

    # 10. business_criticality: 0 (Low), 1 (Medium), 2 (High), 3 (Critical)
    biz_crit = np.random.choice([0, 1, 2, 3], size=num_samples, p=[0.15, 0.45, 0.30, 0.10])

    # Realistic Logit for Exploitation Probability
    # Higher EPSS, CVSS, KEV, Exposure, Asset Criticality increase risk
    # Strong Controls & Available Patch reduce risk
    logit = (
        0.28 * cvss +
        3.20 * epss +
        2.50 * kev +
        1.80 * internet_exposed +
        0.70 * asset_crit +
        0.40 * biz_crit +
        0.25 * open_vulns +
        0.35 * high_vulns -
        2.20 * control_eff -
        1.20 * patch_available -
        3.80  # Baseline intercept offset
    )

    # Add realistic noise/stochasticity
    noise = np.random.normal(loc=0.0, scale=0.85, size=num_samples)
    prob = 1.0 / (1.0 + np.exp(-(logit + noise)))

    # Target binary label
    exploited = (np.random.rand(num_samples) < prob).astype(int)

    df = pd.DataFrame({
        "cvss_score": np.round(cvss, 2),
        "epss_score": np.round(epss, 4),
        "kev_status": kev,
        "internet_exposed": internet_exposed,
        "patch_available": patch_available,
        "asset_criticality": asset_crit,
        "control_effectiveness": np.round(control_eff, 4),
        "open_vulnerability_count": open_vulns,
        "high_vulnerability_count": high_vulns,
        "business_criticality": biz_crit,
        "exploited": exploited,
    })

    return df


def main():
    os.makedirs(DATASET_DIR, exist_ok=True)
    df = generate_synthetic_dataset(num_samples=5000, random_state=42)
    df.to_csv(DATASET_FILE, index=False)

    pos_count = int(df["exploited"].sum())
    neg_count = len(df) - pos_count

    print("=" * 45)
    print("CYBERTWIN-RX ML DATASET")
    print("=" * 45)
    print(f"Dataset Type: Synthetic cybersecurity training dataset for prototype validation")
    print(f"Samples: {len(df)}")
    print(f"Features: {len(df.columns) - 1}")
    print(f"Positive class (exploited=1): {pos_count}")
    print(f"Negative class (exploited=0): {neg_count}")
    print(f"File Location: {DATASET_FILE}")
    print("Dataset saved successfully.")


if __name__ == "__main__":
    main()
