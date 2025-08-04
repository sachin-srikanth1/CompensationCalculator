from datetime import date
from typing import List
from ..models.compensation import (
    CompensationOffer,
    YearlyProjection,
    OfferProjection,
)
from ..services.equity_projection_service import EquityProjectionService
from ..utils.math_helpers import calculate_future_value


class CompensationService:
    """Service for calculating compensation projections"""
    
    def __init__(self):
        self.equity_service = EquityProjectionService()
    
    def compute_total_comp(
        self, offer: CompensationOffer, years: int
    ) -> OfferProjection:
        """
        Compute total compensation projection for an offer
        
        Args:
            offer: Compensation offer to analyze
            years: Number of years to project
            
        Returns:
            OfferProjection with yearly breakdown
        """
        yearly_projections = []
        
        for year in range(1, years + 1):
            projection = self._calculate_year_projection(offer, year)
            yearly_projections.append(projection)
        
        return OfferProjection(
            offer_name=offer.offer_name,
            years=yearly_projections
        )
    
    def _calculate_year_projection(
        self, offer: CompensationOffer, year: int
    ) -> YearlyProjection:
        """Calculate compensation for a specific year"""
        # Base salary (assumed to be constant for simplicity)
        base_salary = offer.base_salary
        
        # Bonus calculation
        bonus = self._calculate_bonus(offer, year)
        
        # Equity value for the year
        equity_value = self.equity_service.calculate_year_equity_value(
            offer, year
        )
        
        # Total compensation
        total = base_salary + bonus + equity_value
        
        return YearlyProjection(
            year=year,
            base_salary=base_salary,
            bonus=bonus,
            equity_value=equity_value,
            total=total
        )
    
    def _calculate_bonus(self, offer: CompensationOffer, year: int) -> float:
        """Calculate bonus for a specific year"""
        # Signing bonus only in first year
        if year == 1:
            return offer.signing_bonus + offer.bonus_fixed + (
                offer.base_salary * offer.bonus_percentage / 100
            )
        else:
            return offer.bonus_fixed + (
                offer.base_salary * offer.bonus_percentage / 100
            )
    
    def compare_offers(
        self, offers: List[CompensationOffer], years: int
    ) -> List[OfferProjection]:
        """Compare multiple offers"""
        return [self.compute_total_comp(offer, years) for offer in offers]
    
    def calculate_cagr(self, offer: CompensationOffer, years: int) -> float:
        """Calculate CAGR for an offer over specified years"""
        projection = self.compute_total_comp(offer, years)
        
        if years < 2:
            return 0.0
        
        initial_value = projection.years[0].total
        final_value = projection.years[-1].total
        
        if initial_value <= 0:
            return 0.0
        
        return (final_value / initial_value) ** (1 / (years - 1)) - 1
    
    def calculate_total_value(self, offer: CompensationOffer, years: int) -> float:
        """Calculate total compensation value over specified years"""
        projection = self.compute_total_comp(offer, years)
        return sum(year.total for year in projection.years)
    
    def calculate_breakdown_percentages(
        self, offer: CompensationOffer, years: int
    ) -> dict:
        """Calculate percentage breakdown of compensation components"""
        projection = self.compute_total_comp(offer, years)
        
        total_base = sum(year.base_salary for year in projection.years)
        total_bonus = sum(year.bonus for year in projection.years)
        total_equity = sum(year.equity_value for year in projection.years)
        total_comp = total_base + total_bonus + total_equity
        
        if total_comp == 0:
            return {"base": 0, "bonus": 0, "equity": 0}
        
        return {
            "base": (total_base / total_comp) * 100,
            "bonus": (total_bonus / total_comp) * 100,
            "equity": (total_equity / total_comp) * 100
        } 