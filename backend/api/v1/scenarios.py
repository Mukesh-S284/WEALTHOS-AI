"""Life-Event Scenario and Simulation API routes."""

from typing import List, Dict, Any
from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.orm import Session

from backend.core.database import get_db
from backend.services.scenario_service import ScenarioService
from backend.schemas.scenario import (
    LifeEventScenarioRequest,
    LifeEventScenarioResponse
)
from backend.api.deps import get_current_user
from backend.models.user import User

router = APIRouter(prefix="/scenarios", tags=["Financial Life-Event Planner"])


@router.post("/life-event", response_model=LifeEventScenarioResponse)
def evaluate_life_event(
    payload: LifeEventScenarioRequest,
    save: bool = Query(True, description="Whether to persist scenario in user history"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Simulate financial scenarios for life events (job loss, income drop, education, vehicle, unexpected medical).
    Calculates monthly trajectory, net wealth impact, and emergency buffer sustainability.
    """
    service = ScenarioService(db)
    return service.evaluate_life_event(current_user, payload, save_scenario=save)


@router.get("/", response_model=List[Dict[str, Any]])
def list_saved_scenarios(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """List user's previously simulated financial scenarios."""
    service = ScenarioService(db)
    scenarios = service.list_saved_scenarios(current_user)
    return [
        {
            "id": s.id,
            "title": s.title,
            "scenario_type": s.scenario_type,
            "description": s.description,
            "input_parameters": s.input_parameters,
            "output_results": s.output_results,
            "created_at": s.created_at
        }
        for s in scenarios
    ]
