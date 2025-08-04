from datetime import date, timedelta
from typing import List, Optional
from ..models.compensation import (
    CompensationOffer,
    OfferProjection,
    YearlyProjection,
)
from ..services.compensation_service import CompensationService
from ..services.equity_projection_service import EquityProjectionService
from ..utils.math_helpers import months_between_dates


class ScenarioService:
    """Service for running what-if scenarios"""
    
    def __init__(self):
        self.compensation_service = CompensationService()
        self.equity_service = EquityProjectionService()
    
    def simulate_start_date_offset(
        self,
        offer: CompensationOffer,
        new_start_date: date,
        years: int
    ) -> OfferProjection:
        """
        Simulate offer with a different start date
        
        Args:
            offer: Original compensation offer
            new_start_date: New start date for the scenario
            years: Number of years to project
            
        Returns:
            OfferProjection with adjusted dates
        """
        # Create a new offer with the adjusted start date
        adjusted_offer = offer.model_copy(deep=True)
        adjusted_offer.start_date = new_start_date
        
        # Adjust all equity grant start dates by the same offset
        date_offset = (new_start_date - offer.start_date).days
        
        for grant in adjusted_offer.equity_grants:
            grant.start_date = grant.start_date + timedelta(days=date_offset)
        
        return self.compensation_service.compute_total_comp(adjusted_offer, years)
    
    def simulate_exit(
        self,
        offer: CompensationOffer,
        exit_valuation: float,
        exit_year: int,
        years: int
    ) -> OfferProjection:
        """
        Simulate offer with exit scenario
        
        Args:
            offer: Compensation offer
            exit_valuation: Exit valuation in USD
            exit_year: Year of exit
            years: Number of years to project
            
        Returns:
            OfferProjection with exit-adjusted equity values
        """
        # Get base compensation projection
        base_projection = self.compensation_service.compute_total_comp(offer, years)
        
        # Calculate exit-adjusted equity values
        exit_equity_values = self.equity_service.simulate_exit_scenario(
            offer, exit_valuation, exit_year, years
        )
        
        # Create new projection with exit-adjusted equity
        adjusted_years = []
        for i, year_projection in enumerate(base_projection.years):
            adjusted_year = YearlyProjection(
                year=year_projection.year,
                base_salary=year_projection.base_salary,
                bonus=year_projection.bonus,
                equity_value=exit_equity_values[i],
                total=year_projection.base_salary + year_projection.bonus + exit_equity_values[i]
            )
            adjusted_years.append(adjusted_year)
        
        return OfferProjection(
            offer_name=f"{offer.offer_name} (Exit Scenario)",
            years=adjusted_years
        )
    
    def simulate_growth_rate_change(
        self,
        offer: CompensationOffer,
        new_growth_rate: float,
        years: int
    ) -> OfferProjection:
        """
        Simulate offer with different equity growth rate
        
        Args:
            offer: Compensation offer
            new_growth_rate: New annual growth rate
            years: Number of years to project
            
        Returns:
            OfferProjection with adjusted growth rate
        """
        # Create a new offer with adjusted growth rates
        adjusted_offer = offer.model_copy(deep=True)
        
        for grant in adjusted_offer.equity_grants:
            grant.growth_rate = new_growth_rate
        
        return self.compensation_service.compute_total_comp(adjusted_offer, years)
    
    def simulate_refresh_rate_change(
        self,
        offer: CompensationOffer,
        new_refresh_rate: float,
        years: int
    ) -> OfferProjection:
        """
        Simulate offer with different refresh rate
        
        Args:
            offer: Compensation offer
            new_refresh_rate: New refresh rate percentage
            years: Number of years to project
            
        Returns:
            OfferProjection with adjusted refresh rate
        """
        # Create a new offer with adjusted refresh rates
        adjusted_offer = offer.model_copy(deep=True)
        
        for grant in adjusted_offer.equity_grants:
            grant.refresh_rate = new_refresh_rate
        
        return self.compensation_service.compute_total_comp(adjusted_offer, years)
    
    def compare_scenarios(
        self,
        base_offer: CompensationOffer,
        scenarios: List[dict],
        years: int
    ) -> List[OfferProjection]:
        """
        Compare multiple scenarios against a base offer
        
        Args:
            base_offer: Base compensation offer
            scenarios: List of scenario configurations
            years: Number of years to project
            
        Returns:
            List of projections for each scenario
        """
        projections = []
        
        # Add base projection
        base_projection = self.compensation_service.compute_total_comp(base_offer, years)
        projections.append(base_projection)
        
        # Generate projections for each scenario
        for i, scenario in enumerate(scenarios):
            scenario_type = scenario.get("type")
            
            if scenario_type == "start_date":
                new_start_date = scenario.get("new_start_date")
                if new_start_date:
                    projection = self.simulate_start_date_offset(
                        base_offer, new_start_date, years
                    )
                    projection.offer_name = f"Scenario {i+1}: Start Date Change"
                    projections.append(projection)
            
            elif scenario_type == "exit":
                exit_valuation = scenario.get("exit_valuation")
                exit_year = scenario.get("exit_year", 4)
                if exit_valuation:
                    projection = self.simulate_exit(
                        base_offer, exit_valuation, exit_year, years
                    )
                    projection.offer_name = f"Scenario {i+1}: Exit at ${exit_valuation/1e9:.1f}B"
                    projections.append(projection)
            
            elif scenario_type == "growth_rate":
                new_growth_rate = scenario.get("growth_rate")
                if new_growth_rate is not None:
                    projection = self.simulate_growth_rate_change(
                        base_offer, new_growth_rate, years
                    )
                    projection.offer_name = f"Scenario {i+1}: {new_growth_rate*100:.0f}% Growth"
                    projections.append(projection)
            
            elif scenario_type == "refresh_rate":
                new_refresh_rate = scenario.get("refresh_rate")
                if new_refresh_rate is not None:
                    projection = self.simulate_refresh_rate_change(
                        base_offer, new_refresh_rate, years
                    )
                    projection.offer_name = f"Scenario {i+1}: {new_refresh_rate}% Refresh"
                    projections.append(projection)
        
        return projections
    
    def calculate_scenario_impact(
        self,
        base_projection: OfferProjection,
        scenario_projection: OfferProjection
    ) -> dict:
        """
        Calculate the impact of a scenario compared to base
        
        Args:
            base_projection: Base offer projection
            scenario_projection: Scenario offer projection
            
        Returns:
            Dictionary with impact metrics
        """
        base_total = sum(year.total for year in base_projection.years)
        scenario_total = sum(year.total for year in scenario_projection.years)
        
        total_difference = scenario_total - base_total
        percentage_change = (total_difference / base_total * 100) if base_total > 0 else 0
        
        # Calculate year-by-year differences
        yearly_differences = []
        for base_year, scenario_year in zip(base_projection.years, scenario_projection.years):
            yearly_differences.append({
                "year": base_year.year,
                "difference": scenario_year.total - base_year.total,
                "percentage_change": (
                    (scenario_year.total - base_year.total) / base_year.total * 100
                ) if base_year.total > 0 else 0
            })
        
        return {
            "total_difference": total_difference,
            "percentage_change": percentage_change,
            "yearly_differences": yearly_differences,
            "scenario_name": scenario_projection.offer_name
        } 