from datetime import date, timedelta
from typing import List, Optional
from ..models.compensation import CompensationOffer, EquityGrant
from ..utils.math_helpers import (
    calculate_vested_amount,
    calculate_refresh_grant,
    calculate_future_value,
    months_between_dates,
)


class EquityProjectionService:
    """Service for calculating equity projections and vesting schedules"""
    
    def calculate_year_equity_value(
        self, offer: CompensationOffer, year: int
    ) -> float:
        """
        Calculate total equity value for a specific year
        
        Args:
            offer: Compensation offer
            year: Year number (1-based)
            
        Returns:
            Total equity value for the year
        """
        # Calculate the date for this year
        year_date = self._get_year_date(offer.start_date, year)
        
        total_equity_value = 0.0
        
        # Calculate equity from each grant
        for grant in offer.equity_grants:
            grant_value = self._calculate_grant_value_for_year(grant, year_date, year)
            total_equity_value += grant_value
        
        return total_equity_value
    
    def _calculate_grant_value_for_year(
        self, grant: EquityGrant, year_date: date, year: int
    ) -> float:
        """Calculate equity value for a specific grant in a given year"""
        # Calculate vested amount for this grant
        vested_value = calculate_vested_amount(
            total_grant_value=grant.value,
            grant_start_date=grant.start_date,
            vesting_start_date=grant.start_date,
            cliff_months=grant.vesting_schedule.cliff_months,
            duration_months=grant.vesting_schedule.duration_months,
            frequency=grant.vesting_schedule.frequency,
            current_date=year_date,
            growth_rate=grant.growth_rate
        )
        
        # Calculate refresh grants if applicable
        refresh_value = self._calculate_refresh_grants(grant, year_date, year)
        
        return vested_value + refresh_value
    
    def _calculate_refresh_grants(
        self, grant: EquityGrant, year_date: date, year: int
    ) -> float:
        """Calculate refresh grant values for a given year"""
        if not grant.refresh_rate or grant.refresh_rate <= 0:
            return 0.0
        
        # Refresh grants typically start after year 1
        if year <= 1:
            return 0.0
        
        # Calculate years since original grant
        years_since_grant = months_between_dates(grant.start_date, year_date) / 12
        
        # Refresh grants are typically annual
        refresh_value = calculate_refresh_grant(
            original_grant_value=grant.value,
            refresh_rate=grant.refresh_rate,
            years_since_original=years_since_grant
        )
        
        # Apply growth rate to refresh grants
        if grant.growth_rate > 0:
            refresh_value = calculate_future_value(
                refresh_value, grant.growth_rate, years_since_grant
            )
        
        return refresh_value
    
    def _get_year_date(self, start_date: date, year: int) -> date:
        """Get the date for a specific year relative to start date"""
        return start_date.replace(year=start_date.year + year - 1)
    
    def model_equity_growth(
        self,
        grant: EquityGrant,
        growth_rate: float,
        years: int,
        exit_valuation: Optional[float] = None
    ) -> List[float]:
        """
        Model equity growth over time
        
        Args:
            grant: Equity grant to model
            growth_rate: Annual growth rate
            years: Number of years to project
            exit_valuation: Optional exit valuation override
            
        Returns:
            List of equity values for each year
        """
        yearly_values = []
        
        for year in range(1, years + 1):
            year_date = self._get_year_date(grant.start_date, year)
            
            # Calculate base vested value
            vested_value = calculate_vested_amount(
                total_grant_value=grant.value,
                grant_start_date=grant.start_date,
                vesting_start_date=grant.start_date,
                cliff_months=grant.vesting_schedule.cliff_months,
                duration_months=grant.vesting_schedule.duration_months,
                frequency=grant.vesting_schedule.frequency,
                current_date=year_date,
                growth_rate=growth_rate
            )
            
            # Apply exit valuation if provided
            if exit_valuation:
                # Assume exit valuation affects the final equity value
                # This is a simplified model
                if year == years:  # Last year
                    vested_value *= (exit_valuation / 1000000000)  # Normalize to $1B valuation
            
            yearly_values.append(vested_value)
        
        return yearly_values
    
    def calculate_vesting_schedule(
        self, grant: EquityGrant, years: int
    ) -> List[dict]:
        """
        Calculate detailed vesting schedule
        
        Args:
            grant: Equity grant
            years: Number of years to project
            
        Returns:
            List of vesting details for each year
        """
        schedule = []
        
        for year in range(1, years + 1):
            year_date = self._get_year_date(grant.start_date, year)
            
            # Calculate vesting percentage
            months_since_vesting = months_between_dates(grant.start_date, year_date)
            
            if months_since_vesting < grant.vesting_schedule.cliff_months:
                vesting_percentage = 0.0
            elif months_since_vesting >= grant.vesting_schedule.duration_months:
                vesting_percentage = 1.0
            else:
                vesting_percentage = months_since_vesting / grant.vesting_schedule.duration_months
            
            # Apply frequency adjustments
            if grant.vesting_schedule.frequency == "quarterly":
                quarters_vested = int(vesting_percentage * (grant.vesting_schedule.duration_months / 3))
                vesting_percentage = quarters_vested / (grant.vesting_schedule.duration_months / 3)
            elif grant.vesting_schedule.frequency == "annually":
                years_vested = int(vesting_percentage * (grant.vesting_schedule.duration_months / 12))
                vesting_percentage = years_vested / (grant.vesting_schedule.duration_months / 12)
            
            schedule.append({
                "year": year,
                "date": year_date,
                "vesting_percentage": vesting_percentage,
                "vested_value": grant.value * vesting_percentage,
                "months_since_grant": months_since_vesting
            })
        
        return schedule
    
    def simulate_exit_scenario(
        self,
        offer: CompensationOffer,
        exit_valuation: float,
        exit_year: int,
        years: int
    ) -> List[float]:
        """
        Simulate equity value with exit scenario
        
        Args:
            offer: Compensation offer
            exit_valuation: Exit valuation in USD
            exit_year: Year of exit
            years: Total years to project
            
        Returns:
            List of equity values for each year
        """
        yearly_equity = []
        
        for year in range(1, years + 1):
            year_date = self._get_year_date(offer.start_date, year)
            
            total_equity = 0.0
            
            for grant in offer.equity_grants:
                # Calculate base vested value
                vested_value = calculate_vested_amount(
                    total_grant_value=grant.value,
                    grant_start_date=grant.start_date,
                    vesting_start_date=grant.start_date,
                    cliff_months=grant.vesting_schedule.cliff_months,
                    duration_months=grant.vesting_schedule.duration_months,
                    frequency=grant.vesting_schedule.frequency,
                    current_date=year_date,
                    growth_rate=grant.growth_rate
                )
                
                # Apply exit multiplier if we're at or after exit year
                if year >= exit_year:
                    # Simplified exit calculation
                    # In reality, this would depend on the specific terms of the equity
                    exit_multiplier = exit_valuation / 1000000000  # Normalize to $1B
                    vested_value *= exit_multiplier
                
                total_equity += vested_value
            
            yearly_equity.append(total_equity)
        
        return yearly_equity 