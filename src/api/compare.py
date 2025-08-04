from fastapi import APIRouter, HTTPException
from typing import List
from ..models.compensation import (
    ComparisonRequest,
    ComparisonResponse,
    OfferProjection,
)
from ..services.compensation_service import CompensationService

router = APIRouter(prefix="/compare", tags=["comparison"])

compensation_service = CompensationService()


@router.post("/", response_model=ComparisonResponse)
async def compare_offers(request: ComparisonRequest) -> ComparisonResponse:
    """
    Compare multiple compensation offers
    
    Args:
        request: ComparisonRequest with offers and projection years
        
    Returns:
        ComparisonResponse with projections for all offers
    """
    try:
        if not request.offers:
            raise HTTPException(
                status_code=400, detail="At least one offer must be provided"
            )
        
        if len(request.offers) > 10:
            raise HTTPException(
                status_code=400, detail="Maximum 10 offers can be compared at once"
            )
        
        # Generate projections for all offers
        projections = compensation_service.compare_offers(
            request.offers, request.projection_years
        )
        
        return ComparisonResponse(projections=projections)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error comparing offers: {str(e)}")


@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "compensation-comparison"} 