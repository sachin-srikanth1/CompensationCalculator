import numpy as np
from datetime import date, datetime
from typing import List, Tuple


def calculate_cagr(initial_value: float, final_value: float, years: float) -> float:
    """Calculate Compound Annual Growth Rate"""
    if initial_value <= 0 or years <= 0:
        return 0.0
    return (final_value / initial_value) ** (1 / years) - 1


def calculate_future_value(initial_value: float, growth_rate: float, years: float) -> float:
    """Calculate future value with compound growth"""
    return initial_value * (1 + growth_rate) ** years


def months_between_dates(start_date: date, end_date: date) -> int:
    """Calculate number of months between two dates"""
    return (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)


def calculate_vested_amount(
    total_grant_value: float,
    grant_start_date: date,
    vesting_start_date: date,
    cliff_months: int,
    duration_months: int,
    frequency: str,
    current_date: date,
    growth_rate: float = 0.0,
) -> float:
    """
    Calculate vested equity amount based on vesting schedule
    
    Args:
        total_grant_value: Total value of the equity grant
        grant_start_date: When the grant was issued
        vesting_start_date: When vesting begins
        cliff_months: Cliff period in months
        duration_months: Total vesting duration in months
        frequency: Vesting frequency ('monthly', 'quarterly', 'annually')
        current_date: Date to calculate vesting for
        growth_rate: Annual growth rate for equity value
    
    Returns:
        Vested equity value in USD
    """
    # Calculate months since vesting started
    months_since_vesting = months_between_dates(vesting_start_date, current_date)
    
    # If before cliff, no vesting
    if months_since_vesting < cliff_months:
        return 0.0
    
    # Calculate vesting percentage
    if months_since_vesting >= duration_months:
        vesting_percentage = 1.0
    else:
        vesting_percentage = months_since_vesting / duration_months
    
    # Apply frequency adjustments
    if frequency == "monthly":
        # Monthly vesting is already handled by the percentage calculation
        pass
    elif frequency == "quarterly":
        # Quarterly vesting - round down to nearest quarter
        quarters_vested = int(vesting_percentage * (duration_months / 3))
        vesting_percentage = quarters_vested / (duration_months / 3)
    elif frequency == "annually":
        # Annual vesting - round down to nearest year
        years_vested = int(vesting_percentage * (duration_months / 12))
        vesting_percentage = years_vested / (duration_months / 12)
    
    # Calculate vested value
    vested_value = total_grant_value * vesting_percentage
    
    # Apply growth rate if specified
    if growth_rate > 0:
        years_since_grant = months_between_dates(grant_start_date, current_date) / 12
        vested_value = calculate_future_value(vested_value, growth_rate, years_since_grant)
    
    return max(0.0, vested_value)


def calculate_refresh_grant(
    original_grant_value: float,
    refresh_rate: float,
    years_since_original: float,
) -> float:
    """Calculate refresh grant value based on original grant and refresh rate"""
    if refresh_rate <= 0:
        return 0.0
    
    # Refresh grants are typically smaller than original grants
    # Common pattern: 25-50% of original grant value
    refresh_multiplier = refresh_rate / 100.0
    return original_grant_value * refresh_multiplier


def calculate_tax_estimate(
    base_salary: float,
    bonus: float,
    equity_value: float,
    state: str = "CA",
) -> float:
    """
    Calculate estimated taxes (simplified)
    
    Note: This is a simplified calculation. Real tax calculations
    are much more complex and depend on many factors.
    """
    # Federal tax brackets (simplified 2024 rates)
    federal_tax_rate = 0.24  # Assume 24% bracket for typical tech salaries
    
    # State tax rates (simplified)
    state_tax_rates = {
        "CA": 0.093,
        "NY": 0.0685,
        "TX": 0.0,
        "WA": 0.0,
        "CO": 0.044,
    }
    state_tax_rate = state_tax_rates.get(state, 0.05)
    
    # Social Security and Medicare
    fica_rate = 0.0765  # 6.2% SS + 1.45% Medicare
    
    # Calculate taxes
    federal_tax = (base_salary + bonus) * federal_tax_rate
    state_tax = (base_salary + bonus) * state_tax_rate
    fica_tax = (base_salary + bonus) * fica_rate
    
    # Equity is typically taxed as income when vested
    equity_tax = equity_value * federal_tax_rate
    
    total_tax = federal_tax + state_tax + fica_tax + equity_tax
    
    return total_tax


def round_to_nearest_thousand(value: float) -> float:
    """Round monetary values to nearest thousand for cleaner display"""
    return round(value / 1000) * 1000


def format_currency(value: float) -> str:
    """Format currency values for display"""
    if value >= 1_000_000:
        return f"${value/1_000_000:.1f}M"
    elif value >= 1_000:
        return f"${value/1_000:.0f}K"
    else:
        return f"${value:.0f}" 