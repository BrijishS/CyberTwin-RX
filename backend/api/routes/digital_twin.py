from typing import Dict, Any, List
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.digital_twin.service import get_digital_twin_data
from backend.attack_graph.analyzer import find_attack_paths, get_top_attack_path

router = APIRouter(tags=["Digital Twin & Attack Paths"])


@router.get("/api/digital-twin/graph", response_model=Dict[str, List[Dict[str, Any]]])
def read_digital_twin_graph(db: Session = Depends(get_db)):
    return get_digital_twin_data(db)


@router.get("/api/attack-paths", response_model=List[Dict[str, Any]])
def read_attack_paths(db: Session = Depends(get_db)):
    return find_attack_paths(db)


@router.get("/api/attack-paths/top", response_model=Dict[str, Any])
def read_top_attack_path(db: Session = Depends(get_db)):
    return get_top_attack_path(db)
