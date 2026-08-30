import os
import json
import joblib
import pandas as pd
from datetime import datetime, timezone

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix

from backend.ai.dataset_generator import DATASET_FILE, generate_synthetic_dataset

MODELS_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "models"))
MODEL_FILE = os.path.join(MODELS_DIR, "exploit_prediction_model.pkl")
METADATA_FILE = os.path.join(MODELS_DIR, "model_metadata.json")

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
TARGET_COLUMN = "exploited"


def train_and_save_model() -> dict:
    os.makedirs(MODELS_DIR, exist_ok=True)

    # 1. Load or Generate Dataset
    if os.path.exists(DATASET_FILE):
        df = pd.read_csv(DATASET_FILE)
    else:
        df = generate_synthetic_dataset(num_samples=5000, random_state=42)
        os.makedirs(os.path.dirname(DATASET_FILE), exist_ok=True)
        df.to_csv(DATASET_FILE, index=False)

    X = df[FEATURE_COLUMNS]
    y = df[TARGET_COLUMN]

    # 2. Train / Test Split (80% Train, 20% Test, Stratified)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y
    )

    # 3. Train Random Forest Classifier
    clf = RandomForestClassifier(
        n_estimators=200,
        max_depth=12,
        min_samples_split=4,
        min_samples_leaf=2,
        class_weight="balanced",
        random_state=42,
        n_jobs=-1,
    )
    clf.fit(X_train, y_train)

    # 4. Model Evaluation
    y_pred = clf.predict(X_test)
    y_proba = clf.predict_proba(X_test)[:, 1]

    acc = float(accuracy_score(y_test, y_pred))
    prec = float(precision_score(y_test, y_pred))
    rec = float(recall_score(y_test, y_pred))
    f1 = float(f1_score(y_test, y_pred))
    roc_auc = float(roc_auc_score(y_test, y_proba))
    conf_matrix = confusion_matrix(y_test, y_pred).tolist()

    # 5. Extract Feature Importances
    importances = clf.feature_importances_
    feat_imp_dict = {
        feat: float(imp)
        for feat, imp in sorted(zip(FEATURE_COLUMNS, importances), key=lambda x: x[1], reverse=True)
    }

    # 6. Save Trained Model
    joblib.dump(clf, MODEL_FILE)

    # 7. Prepare Metadata
    metadata = {
        "model_name": "RandomForestClassifier",
        "training_date": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC"),

        "training_samples": len(df),
        "test_samples": len(X_test),
        "dataset_type": "Synthetic cybersecurity training dataset for prototype validation",
        "features": FEATURE_COLUMNS,
        "metrics": {
            "accuracy": round(acc, 4),
            "precision": round(prec, 4),
            "recall": round(rec, 4),
            "f1": round(f1, 4),
            "roc_auc": round(roc_auc, 4),
            "confusion_matrix": conf_matrix,
        },
        "feature_importances": {k: round(v, 4) for k, v in feat_imp_dict.items()},
    }

    with open(METADATA_FILE, "w") as f:
        json.dump(metadata, f, indent=2)

    return metadata


def main():
    metadata = train_and_save_model()
    metrics = metadata["metrics"]
    importances = metadata["feature_importances"]

    print("=" * 50)
    print("CYBERTWIN-RX ML MODEL TRAINING COMPLETE")
    print("=" * 50)
    print(f"Model: {metadata['model_name']}")
    print(f"Dataset Type: {metadata['dataset_type']}")
    print(f"Training Samples: {metadata['training_samples']}")
    print("-" * 50)
    print(f"Accuracy:  {metrics['accuracy']:.4f}")
    print(f"Precision: {metrics['precision']:.4f}")
    print(f"Recall:    {metrics['recall']:.4f}")
    print(f"F1 Score:  {metrics['f1']:.4f}")
    print(f"ROC-AUC:   {metrics['roc_auc']:.4f}")
    print("-" * 50)
    print("Top Feature Importances:")
    for idx, (feat, score) in enumerate(list(importances.items())[:5], 1):
        print(f"  {idx}. {feat}: {score:.4f}")
    print("-" * 50)
    print(f"Model saved to: {MODEL_FILE}")
    print(f"Metadata saved to: {METADATA_FILE}")


if __name__ == "__main__":
    main()
