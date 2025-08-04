from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ..models.compensation import (
    ScenarioRequest,
    OfferProjection,
    CompensationOffer,
)
from ..services.scenario_service import ScenarioService

router = APIRouter(prefix="/scenario", tags=["scenarios"])

scenario_service = ScenarioService()


@router.post("/", response_model=OfferProjection)
async def run_scenario(request: ScenarioRequest) -> OfferProjection:
    """
    Run a what-if scenario on a compensation offer
    
    Args:
        request: ScenarioRequest with offer and scenario parameters
        
    Returns:
        OfferProjection with scenario-adjusted values
    """
    try:
        if request.new_start_date:
            return scenario_service.simulate_start_date_offset(
                request.offer, request.new_start_date, request.projection_years
            )
        
        elif request.exit_valuation:
            # Default to year 4 for exit scenario
            return scenario_service.simulate_exit(
                request.offer, request.exit_valuation, 4, request.projection_years
            )
        
        else:
            # Return base projection if no scenario parameters
            from ..services.compensation_service import CompensationService
            comp_service = CompensationService()
            return comp_service.compute_total_comp(request.offer, request.projection_years)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running scenario: {str(e)}")


@router.post("/exit", response_model=OfferProjection)
async def simulate_exit_scenario(
    offer: CompensationOffer,
    exit_valuation: float,
    exit_year: int = 4,
    projection_years: int = 4
) -> OfferProjection:
    """
    Simulate exit scenario with specific parameters
    
    Args:
        offer: Compensation offer
        exit_valuation: Exit valuation in USD
        exit_year: Year of exit (default: 4)
        projection_years: Number of years to project (default: 4)
        
    Returns:
        OfferProjection with exit-adjusted values
    """
    try:
        return scenario_service.simulate_exit(
            offer, exit_valuation, exit_year, projection_years
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating exit: {str(e)}")


@router.post("/growth-rate", response_model=OfferProjection)
async def simulate_growth_rate_change(
    offer: CompensationOffer,
    growth_rate: float,
    projection_years: int = 4
) -> OfferProjection:
    """
    Simulate different equity growth rate
    
    Args:
        offer: Compensation offer
        growth_rate: New annual growth rate (e.g., 0.15 for 15%)
        projection_years: Number of years to project (default: 4)
        
    Returns:
        OfferProjection with adjusted growth rate
    """
    try:
        return scenario_service.simulate_growth_rate_change(
            offer, growth_rate, projection_years
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating growth rate: {str(e)}")


@router.post("/refresh-rate", response_model=OfferProjection)
async def simulate_refresh_rate_change(
    offer: CompensationOffer,
    refresh_rate: float,
    projection_years: int = 4
) -> OfferProjection:
    """
    Simulate different refresh rate
    
    Args:
        offer: Compensation offer
        refresh_rate: New refresh rate percentage (e.g., 25 for 25%)
        projection_years: Number of years to project (default: 4)
        
    Returns:
        OfferProjection with adjusted refresh rate
    """
    try:
        return scenario_service.simulate_refresh_rate_change(
            offer, refresh_rate, projection_years
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error simulating refresh rate: {str(e)}")


@router.post("/multiple", response_model=List[OfferProjection])
async def run_multiple_scenarios(
    base_offer: CompensationOffer,
    scenarios: List[dict],
    projection_years: int = 4
) -> List[OfferProjection]:
    """
    Run multiple scenarios against a base offer
    
    Args:
        base_offer: Base compensation offer
        scenarios: List of scenario configurations
        projection_years: Number of years to project (default: 4)
        
    Returns:
        List of projections for each scenario
    """
    try:
        return scenario_service.compare_scenarios(
            base_offer, scenarios, projection_years
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error running scenarios: {str(e)}") 