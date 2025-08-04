import json
import os
from fastapi import APIRouter, HTTPException
from typing import List, Optional
from ..models.compensation import BenchmarkData

router = APIRouter(prefix="/benchmarks", tags=["benchmarks"])


def load_benchmark_data() -> List[dict]:
    """Load benchmark data from JSON file"""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        data_file = os.path.join(current_dir, "..", "data", "benchmarks.json")
        
        with open(data_file, "r") as f:
            data = json.load(f)
            return data.get("benchmarks", [])
    
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error loading benchmark data: {str(e)}"
        )


@router.get("/", response_model=List[BenchmarkData])
async def get_benchmarks(
    role: Optional[str] = None,
    level: Optional[str] = None,
    location: Optional[str] = None
) -> List[BenchmarkData]:
    """
    Get market benchmark data
    
    Args:
        role: Filter by job role (e.g., "Software Engineer")
        level: Filter by level (e.g., "L4")
        location: Filter by location (e.g., "San Francisco")
        
    Returns:
        List of benchmark data matching the filters
    """
    try:
        benchmarks = load_benchmark_data()
        
        # Apply filters
        if role:
            benchmarks = [b for b in benchmarks if b.get("role") == role]
        
        if level:
            benchmarks = [b for b in benchmarks if b.get("level") == level]
        
        if location:
            benchmarks = [b for b in benchmarks if b.get("location") == location]
        
        return [BenchmarkData(**benchmark) for benchmark in benchmarks]
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving benchmarks: {str(e)}")


@router.get("/roles")
async def get_available_roles() -> List[str]:
    """Get list of available job roles"""
    try:
        benchmarks = load_benchmark_data()
        roles = list(set(benchmark.get("role") for benchmark in benchmarks))
        return sorted(roles)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving roles: {str(e)}")


@router.get("/levels")
async def get_available_levels() -> List[str]:
    """Get list of available job levels"""
    try:
        benchmarks = load_benchmark_data()
        levels = list(set(benchmark.get("level") for benchmark in benchmarks))
        return sorted(levels)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving levels: {str(e)}")


@router.get("/locations")
async def get_available_locations() -> List[str]:
    """Get list of available locations"""
    try:
        benchmarks = load_benchmark_data()
        locations = list(set(benchmark.get("location") for benchmark in benchmarks))
        return sorted(locations)
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving locations: {str(e)}")


@router.get("/summary")
async def get_benchmark_summary() -> dict:
    """Get summary statistics of benchmark data"""
    try:
        benchmarks = load_benchmark_data()
        
        if not benchmarks:
            return {"message": "No benchmark data available"}
        
        # Calculate summary statistics
        total_benchmarks = len(benchmarks)
        roles = list(set(benchmark.get("role") for benchmark in benchmarks))
        levels = list(set(benchmark.get("level") for benchmark in benchmarks))
        locations = list(set(benchmark.get("location") for benchmark in benchmarks))
        
        # Calculate average compensation ranges
        avg_base_50th = sum(b.get("base_salary_50th", 0) for b in benchmarks) / len(benchmarks)
        avg_equity_50th = sum(b.get("equity_50th", 0) for b in benchmarks) / len(benchmarks)
        avg_total_50th = sum(b.get("total_comp_50th", 0) for b in benchmarks) / len(benchmarks)
        
        return {
            "total_benchmarks": total_benchmarks,
            "available_roles": len(roles),
            "available_levels": len(levels),
            "available_locations": len(locations),
            "average_base_salary_50th": round(avg_base_50th),
            "average_equity_50th": round(avg_equity_50th),
            "average_total_comp_50th": round(avg_total_50th),
            "roles": roles,
            "levels": levels,
            "locations": locations
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error generating summary: {str(e)}")


@router.get("/compare/{role}/{level}/{location}")
async def get_specific_benchmark(
    role: str,
    level: str,
    location: str
) -> BenchmarkData:
    """
    Get specific benchmark data for role/level/location combination
    
    Args:
        role: Job role (e.g., "Software Engineer")
        level: Job level (e.g., "L4")
        location: Location (e.g., "San Francisco")
        
    Returns:
        Benchmark data for the specific combination
    """
    try:
        benchmarks = load_benchmark_data()
        
        # Find matching benchmark
        for benchmark in benchmarks:
            if (benchmark.get("role") == role and
                benchmark.get("level") == level and
                benchmark.get("location") == location):
                return BenchmarkData(**benchmark)
        
        raise HTTPException(
            status_code=404,
            detail=f"No benchmark data found for {role} {level} in {location}"
        )
    
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error retrieving benchmark: {str(e)}") 