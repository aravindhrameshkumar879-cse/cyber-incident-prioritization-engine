from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.schemas.simulation import SimulationRequest, SimulationResponse
from app.engine.simulator import simulator_engine

router = APIRouter(prefix="/simulator", tags=["Simulator"])

@router.post("", response_model=SimulationResponse)
def simulate_incident(sim_req: SimulationRequest, db: Session = Depends(get_db)):
    """
    Non-persistent what-if risk recalculation.
    Accepts scenario factors, evaluates ML & Rule scores, and estimates queue position shifts.
    """
    result = simulator_engine.simulate_scenario(sim_req.model_dump(), db=db)
    return SimulationResponse(**result)
