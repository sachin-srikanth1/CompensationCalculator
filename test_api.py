#!/usr/bin/env python3
"""
Simple test script for the Compensation Comparison Tool API
Run this after starting the server to verify functionality
"""

import requests
import json
from datetime import date

# API base URL
BASE_URL = "http://localhost:8000"

def test_health():
    """Test health endpoint"""
    print("🔍 Testing health endpoint...")
    response = requests.get(f"{BASE_URL}/health")
    print(f"Status: {response.status_code}")
    print(f"Response: {response.json()}")
    print()

def test_benchmarks():
    """Test benchmarks endpoint"""
    print("🔍 Testing benchmarks endpoint...")
    response = requests.get(f"{BASE_URL}/benchmarks/")
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"Found {len(data)} benchmark entries")
        if data:
            print(f"Sample: {data[0]}")
    print()

def test_compare_offers():
    """Test offer comparison"""
    print("🔍 Testing offer comparison...")
    
    # Sample offer data
    offers = [
        {
            "offer_name": "Tech Corp - Senior Engineer",
            "base_salary": 180000,
            "signing_bonus": 25000,
            "bonus_percentage": 15,
            "bonus_fixed": 0,
            "start_date": "2024-01-15",
            "equity_grants": [
                {
                    "type": "RSU",
                    "value": 200000,
                    "vesting_schedule": {
                        "cliff_months": 12,
                        "duration_months": 48,
                        "frequency": "monthly"
                    },
                    "start_date": "2024-01-15",
                    "refresh_rate": 25,
                    "growth_rate": 0.10
                }
            ]
        },
        {
            "offer_name": "StartupXYZ - Lead Developer",
            "base_salary": 160000,
            "signing_bonus": 10000,
            "bonus_percentage": 10,
            "bonus_fixed": 0,
            "start_date": "2024-02-01",
            "equity_grants": [
                {
                    "type": "option",
                    "value": 300000,
                    "vesting_schedule": {
                        "cliff_months": 12,
                        "duration_months": 48,
                        "frequency": "monthly"
                    },
                    "start_date": "2024-02-01",
                    "refresh_rate": 30,
                    "growth_rate": 0.20
                }
            ]
        }
    ]
    
    payload = {
        "offers": offers,
        "projection_years": 4
    }
    
    response = requests.post(f"{BASE_URL}/compare/", json=payload)
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Generated {len(data['projections'])} projections")
        for projection in data['projections']:
            print(f"  {projection['offer_name']}: {len(projection['years'])} years")
            total_comp = sum(year['total'] for year in projection['years'])
            print(f"    Total 4-year compensation: ${total_comp:,.0f}")
    else:
        print(f"Error: {response.text}")
    print()

def test_scenario():
    """Test scenario endpoint"""
    print("🔍 Testing scenario endpoint...")
    
    offer = {
        "offer_name": "Tech Corp - Senior Engineer",
        "base_salary": 180000,
        "signing_bonus": 25000,
        "bonus_percentage": 15,
        "bonus_fixed": 0,
        "start_date": "2024-01-15",
        "equity_grants": [
            {
                "type": "RSU",
                "value": 200000,
                "vesting_schedule": {
                    "cliff_months": 12,
                    "duration_months": 48,
                    "frequency": "monthly"
                },
                "start_date": "2024-01-15",
                "refresh_rate": 25,
                "growth_rate": 0.10
            }
        ]
    }
    
    # Test exit scenario
    payload = {
        "offer": offer,
        "exit_valuation": 5000000000,  # $5B exit
        "projection_years": 4
    }
    
    response = requests.post(f"{BASE_URL}/scenario/", json=payload)
    print(f"Exit scenario status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print(f"Scenario: {data['offer_name']}")
        total_comp = sum(year['total'] for year in data['years'])
        print(f"Total 4-year compensation: ${total_comp:,.0f}")
    else:
        print(f"Error: {response.text}")
    print()

def main():
    """Run all tests"""
    print("🧪 Testing Compensation Comparison Tool API")
    print("=" * 50)
    
    try:
        test_health()
        test_benchmarks()
        test_compare_offers()
        test_scenario()
        
        print("✅ All tests completed!")
        print("\n📚 API Documentation available at:")
        print(f"   {BASE_URL}/docs")
        print(f"   {BASE_URL}/redoc")
        
    except requests.exceptions.ConnectionError:
        print("❌ Error: Could not connect to the API server.")
        print("Make sure the server is running with:")
        print("   python -m src.main")
        print("   or")
        print("   uvicorn src.main:app --reload")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 