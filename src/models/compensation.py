from datetime import date
from typing import List, Optional, Literal
from pydantic import BaseModel, Field


class VestingSchedule(BaseModel):
    """Vesting schedule configuration"""
    cliff_months: int = Field(..., ge=0, description="Cliff period in months")
    duration_months: int = Field(..., ge=1, description="Total vesting duration in months")
    frequency: Literal["monthly", "quarterly", "annually"] = Field(
        default="monthly", description="Vesting frequency"
    )


class EquityGrant(BaseModel):
    """Equity grant configuration"""
    type: Literal["RSU", "option", "ISO"] = Field(..., description="Type of equity grant")
    value: float = Field(..., ge=0, description="Total grant value in USD")
    vesting_schedule: VestingSchedule = Field(..., description="Vesting schedule")
    start_date: date = Field(..., description="Grant start date")
    refresh_rate: Optional[float] = Field(
        default=None, ge=0, description="Annual refresh rate as percentage of original grant"
    )
    growth_rate: float = Field(
        default=0.0, description="Annual growth rate for equity value"
    )


class CompensationOffer(BaseModel):
    """Complete compensation offer"""
    offer_name: str = Field(..., description="Name/identifier for the offer")
    base_salary: float = Field(..., ge=0, description="Annual base salary in USD")
    signing_bonus: float = Field(default=0.0, ge=0, description="Signing bonus in USD")
    bonus_percentage: float = Field(
        default=0.0, ge=0, le=100, description="Annual bonus as percentage of base salary"
    )
    bonus_fixed: float = Field(
        default=0.0, ge=0, description="Fixed annual bonus amount in USD"
    )
    equity_grants: List[EquityGrant] = Field(
        default_factory=list, description="List of equity grants"
    )
    start_date: date = Field(..., description="Employment start date")


class YearlyProjection(BaseModel):
    """Year-by-year compensation breakdown"""
    year: int = Field(..., ge=1, description="Year number")
    base_salary: float = Field(..., ge=0, description="Base salary for the year")
    bonus: float = Field(..., ge=0, description="Bonus for the year")
    equity_value: float = Field(..., ge=0, description="Vested equity value for the year")
    total: float = Field(..., ge=0, description="Total compensation for the year")


class OfferProjection(BaseModel):
    """Complete offer projection with yearly breakdown"""
    offer_name: str = Field(..., description="Name of the offer")
    years: List[YearlyProjection] = Field(..., description="Year-by-year breakdown")


class ComparisonRequest(BaseModel):
    """Request for comparing multiple offers"""
    offers: List[CompensationOffer] = Field(..., description="List of offers to compare")
    projection_years: int = Field(
        default=4, ge=1, le=6, description="Number of years to project"
    )


class ComparisonResponse(BaseModel):
    """Response with projections for all offers"""
    projections: List[OfferProjection] = Field(..., description="Projections for each offer")


class ScenarioRequest(BaseModel):
    """Request for scenario analysis"""
    offer: CompensationOffer = Field(..., description="Base offer")
    new_start_date: Optional[date] = Field(
        default=None, description="New start date for scenario"
    )
    exit_valuation: Optional[float] = Field(
        default=None, ge=0, description="Exit valuation for equity calculation"
    )
    projection_years: int = Field(
        default=4, ge=1, le=6, description="Number of years to project"
    )


class BenchmarkData(BaseModel):
    """Market benchmark data"""
    role: str = Field(..., description="Job role/level")
    location: str = Field(..., description="Geographic location")
    base_salary_25th: float = Field(..., description="25th percentile base salary")
    base_salary_50th: float = Field(..., description="50th percentile base salary")
    base_salary_75th: float = Field(..., description="75th percentile base salary")
    equity_25th: float = Field(..., description="25th percentile equity value")
    equity_50th: float = Field(..., description="50th percentile equity value")
    equity_75th: float = Field(..., description="75th percentile equity value")
    total_comp_25th: float = Field(..., description="25th percentile total compensation")
    total_comp_50th: float = Field(..., description="50th percentile total compensation")
    total_comp_75th: float = Field(..., description="75th percentile total compensation") 