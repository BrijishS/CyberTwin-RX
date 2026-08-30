import csv
import os
from datetime import datetime
from sqlalchemy.orm import Session

from backend.database import engine, init_db, SessionLocal
from backend.models import BusinessService, Asset, Vulnerability, SecurityControl

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATASETS_DIR = os.path.join(BASE_DIR, "datasets")


def parse_bool(val: str) -> bool:
    if isinstance(val, bool):
        return val
    return str(val).strip().lower() in ("true", "1", "t", "yes")


def parse_datetime(val: str):
    if not val or not str(val).strip():
        return None
    try:
        return datetime.strptime(str(val).strip(), "%Y-%m-%d %H:%M:%S")
    except ValueError:
        return None


def seed_data():
    init_db()
    db: Session = SessionLocal()

    bs_created = 0
    assets_created = 0
    vulns_created = 0
    controls_created = 0

    try:
        # 1. Seed Business Services
        bs_csv_path = os.path.join(DATASETS_DIR, "business_services.csv")
        bs_map = {}

        if os.path.exists(bs_csv_path):
            with open(bs_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row["name"].strip()
                    existing = db.query(BusinessService).filter(BusinessService.name == name).first()
                    if not existing:
                        service = BusinessService(
                            name=name,
                            description=row["description"],
                            criticality=row["criticality"],
                            financial_value=float(row["financial_value"]),
                            department=row["department"],
                            is_active=parse_bool(row["is_active"]),
                        )
                        db.add(service)
                        db.commit()
                        db.refresh(service)
                        bs_map[name] = service.id
                        bs_created += 1
                    else:
                        bs_map[name] = existing.id

        # 2. Seed Assets
        assets_csv_path = os.path.join(DATASETS_DIR, "assets.csv")
        asset_map = {}

        if os.path.exists(assets_csv_path):
            with open(assets_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    name = row["name"].strip()
                    bs_name = row["business_service_name"].strip()
                    bs_id = bs_map.get(bs_name)

                    if not bs_id:
                        print(f"Warning: Business Service '{bs_name}' not found for asset '{name}'")
                        continue

                    existing = db.query(Asset).filter(Asset.name == name).first()
                    if not existing:
                        asset = Asset(
                            name=name,
                            asset_type=row["asset_type"],
                            hostname=row["hostname"] if row["hostname"] else None,
                            ip_address=row["ip_address"] if row["ip_address"] else None,
                            business_service_id=bs_id,
                            criticality=row["criticality"],
                            financial_value=float(row["financial_value"]),
                            internet_exposed=parse_bool(row["internet_exposed"]),
                            environment=row["environment"] if row["environment"] else None,
                            owner_department=row["owner_department"] if row["owner_department"] else None,
                            is_active=parse_bool(row["is_active"]),
                        )
                        db.add(asset)
                        db.commit()
                        db.refresh(asset)
                        asset_map[name] = asset.id
                        assets_created += 1
                    else:
                        asset_map[name] = existing.id

        # 3. Seed Vulnerabilities
        vuln_csv_path = os.path.join(DATASETS_DIR, "vulnerabilities.csv")

        if os.path.exists(vuln_csv_path):
            with open(vuln_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    asset_name = row["asset_name"].strip()
                    cve_id = row["cve_id"].strip()
                    asset_id = asset_map.get(asset_name)

                    if not asset_id:
                        print(f"Warning: Asset '{asset_name}' not found for vulnerability '{cve_id}'")
                        continue

                    existing = (
                        db.query(Vulnerability)
                        .filter(Vulnerability.asset_id == asset_id, Vulnerability.cve_id == cve_id)
                        .first()
                    )
                    if not existing:
                        vuln = Vulnerability(
                            asset_id=asset_id,
                            cve_id=cve_id,
                            title=row["title"],
                            description=row["description"],
                            cvss_score=float(row["cvss_score"]),
                            epss_score=float(row["epss_score"]),
                            kev_status=parse_bool(row["kev_status"]),
                            patch_available=parse_bool(row["patch_available"]),
                            status=row["status"],
                        )
                        db.add(vuln)
                        vulns_created += 1
                db.commit()

        # 4. Seed Security Controls
        sc_csv_path = os.path.join(DATASETS_DIR, "security_controls.csv")

        if os.path.exists(sc_csv_path):
            with open(sc_csv_path, mode="r", encoding="utf-8") as f:
                reader = csv.DictReader(f)
                for row in reader:
                    ctrl_name = row["name"].strip()
                    asset_name = row["asset_name"].strip() if row.get("asset_name") else None
                    asset_id = asset_map.get(asset_name) if asset_name else None

                    existing = (
                        db.query(SecurityControl)
                        .filter(
                            SecurityControl.name == ctrl_name,
                            SecurityControl.asset_id == asset_id,
                        )
                        .first()
                    )
                    if not existing:
                        sc = SecurityControl(
                            asset_id=asset_id,
                            name=ctrl_name,
                            control_type=row["control_type"],
                            description=row["description"],
                            effectiveness=float(row["effectiveness"]),
                            implementation_cost=float(row["implementation_cost"]),
                            status=row["status"],
                            implemented_at=parse_datetime(row["implemented_at"]),
                        )
                        db.add(sc)
                        controls_created += 1
                db.commit()

        # Print Seed Report
        total_bs = db.query(BusinessService).count()
        total_assets = db.query(Asset).count()
        total_vulns = db.query(Vulnerability).count()
        total_controls = db.query(SecurityControl).count()

        print("========================================")
        print("CYBERTWIN-RX DEMO DATA SEEDING")
        print("========================================")
        if bs_created == 0 and assets_created == 0 and vulns_created == 0 and controls_created == 0:
            print("\nDemo dataset already exists.")
            print("No duplicate records created.\n")
        else:
            print(f"\nBusiness Services: {total_bs}")
            print(f"Assets: {total_assets}")
            print(f"Vulnerabilities: {total_vulns}")
            print(f"Security Controls: {total_controls}")
            print("\nDemo dataset created successfully.\n")

        print("Organization:")
        print("CyberTwin Demo Bank")
        print("========================================")

    except Exception as e:
        db.rollback()
        print(f"Error seeding database: {e}")
        raise e
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
