# Compensation Comparison Tool Backend

A modular FastAPI backend for comparing compensation offers and running what-if scenarios. Built with clean architecture principles using FastAPI, Pydantic, and numpy.

## 🏗️ Architecture

```
src/
├── main.py              # FastAPI entry point
├── api/                 # Route handlers
│   ├── compare.py       # Offer comparison endpoints
│   ├── scenario.py      # What-if scenario endpoints
│   └── benchmarks.py    # Market benchmark endpoints
├── models/              # Pydantic models
│   └── compensation.py  # Data models for offers, equity, projections
├── services/            # Business logic
│   ├── compensation_service.py    # Main compensation calculations
│   ├── equity_projection_service.py # Equity growth and vesting
│   └── scenario_service.py        # What-if scenarios
├── data/                # Static data
│   ├── benchmarks.json  # Market compensation data
│   └── example_offers.json # Sample offers for testing
└── utils/               # Utility functions
    └── math_helpers.py  # CAGR, vesting, tax calculations
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone and setup:**
```bash
git clone <repository-url>
cd NvidiaCompCalculator
```

2. **Install dependencies:**
```bash
pip install -r requirements.txt
```

3. **Run the server:**
```bash
python -m src.main
```

The API will be available at `http://localhost:8000`

### Alternative: Using uvicorn directly
```bash
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

## 📚 API Documentation

Once running, visit:
- **Interactive API docs:** http://localhost:8000/docs
- **ReDoc documentation:** http://localhost:8000/redoc

## 🔧 Core Features

### 1. Offer Comparison (`/compare`)

Compare multiple compensation offers with year-by-year projections.

**POST** `/compare/`
```json
{
  "offers": [
    {
      "offer_name": "Tech Corp",
      "base_salary": 180000,
      "signing_bonus": 25000,
      "bonus_percentage": 15,
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
      ],
      "start_date": "2024-01-15"
    }
  ],
  "projection_years": 4
}
```

**Response:**
```json
{
  "projections": [
    {
      "offer_name": "Tech Corp",
      "years": [
        {
          "year": 1,
          "base_salary": 180000,
          "bonus": 52000,
          "equity_value": 45000,
          "total": 277000
        },
        {
          "year": 2,
          "base_salary": 180000,
          "bonus": 27000,
          "equity_value": 90000,
          "total": 297000
        }
      ]
    }
  ]
}
```

### 2. What-If Scenarios (`/scenario`)

Run scenarios like start date changes, exit valuations, growth rate changes.

**POST** `/scenario/`
```json
{
  "offer": { /* compensation offer */ },
  "new_start_date": "2024-06-01",
  "projection_years": 4
}
```

**Available scenario endpoints:**
- `POST /scenario/exit` - Exit valuation scenarios
- `POST /scenario/growth-rate` - Equity growth rate changes
- `POST /scenario/refresh-rate` - Refresh grant rate changes
- `POST /scenario/multiple` - Run multiple scenarios

### 3. Market Benchmarks (`/benchmarks`)

Get market compensation data for comparisons.

**GET** `/benchmarks/?role=Software Engineer&level=L4&location=San Francisco`

**Available endpoints:**
- `GET /benchmarks/` - Filtered benchmark data
- `GET /benchmarks/roles` - Available job roles
- `GET /benchmarks/levels` - Available job levels
- `GET /benchmarks/locations` - Available locations
- `GET /benchmarks/summary` - Summary statistics

## 🧮 Key Calculations

### Equity Vesting
- **Cliff period:** No vesting until cliff is reached
- **Vesting frequency:** Monthly, quarterly, or annually
- **Growth rate:** Annual appreciation of equity value
- **Refresh grants:** Annual equity refreshes

### Compensation Components
- **Base salary:** Annual base compensation
- **Signing bonus:** One-time signing bonus (year 1 only)
- **Performance bonus:** Percentage or fixed amount
- **Equity value:** Vested equity value for the year

### CAGR Calculation
Compound Annual Growth Rate for total compensation over time.

## 🧪 Testing

### Example Usage

```python
import requests
import json

# Load example offers
with open('src/data/example_offers.json') as f:
    data = json.load(f)

# Compare offers
response = requests.post(
    'http://localhost:8000/compare/',
    json={
        "offers": data["example_offers"][:2],
        "projection_years": 4
    }
)

print(json.dumps(response.json(), indent=2))
```

### Run Tests
```bash
pytest tests/ -v
```

## 📊 Data Models

### CompensationOffer
- `offer_name`: String identifier
- `base_salary`: Annual base salary
- `signing_bonus`: One-time signing bonus
- `bonus_percentage`: Annual bonus as % of base
- `bonus_fixed`: Fixed annual bonus amount
- `equity_grants`: List of equity grants
- `start_date`: Employment start date

### EquityGrant
- `type`: RSU, option, or ISO
- `value`: Total grant value
- `vesting_schedule`: Vesting configuration
- `start_date`: Grant start date
- `refresh_rate`: Annual refresh percentage
- `growth_rate`: Annual growth rate

### VestingSchedule
- `cliff_months`: Cliff period in months
- `duration_months`: Total vesting duration
- `frequency`: Monthly, quarterly, or annually

## 🔍 API Endpoints Summary

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/` | GET | API information |
| `/health` | GET | Health check |
| `/compare/` | POST | Compare multiple offers |
| `/scenario/` | POST | Run what-if scenarios |
| `/scenario/exit` | POST | Exit valuation scenarios |
| `/scenario/growth-rate` | POST | Growth rate scenarios |
| `/scenario/refresh-rate` | POST | Refresh rate scenarios |
| `/benchmarks/` | GET | Market benchmark data |
| `/benchmarks/roles` | GET | Available job roles |
| `/benchmarks/levels` | GET | Available job levels |
| `/benchmarks/locations` | GET | Available locations |

## 🛠️ Development

### Project Structure
```
NvidiaCompCalculator/
├── src/
│   ├── main.py
│   ├── api/
│   ├── models/
│   ├── services/
│   ├── data/
│   └── utils/
├── requirements.txt
├── README.md
└── tests/
```

### Adding New Features

1. **New Models:** Add to `src/models/compensation.py`
2. **New Services:** Add to `src/services/`
3. **New Routes:** Add to `src/api/`
4. **New Data:** Add to `src/data/`

### Code Style
- Use type hints throughout
- Follow FastAPI best practices
- Use Pydantic for validation
- Keep services stateless where possible

## 🚀 Deployment

### Production Setup
1. Set environment variables for production
2. Use proper CORS origins
3. Add authentication if needed
4. Use production WSGI server (gunicorn)

```bash
pip install gunicorn
gunicorn src.main:app -w 4 -k uvicorn.workers.UvicornWorker
```

### Docker (Optional)
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY src/ ./src/
CMD ["uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📈 Performance

- **Stateless design:** No database required
- **Efficient calculations:** Optimized math operations
- **Caching ready:** Easy to add Redis caching
- **Scalable:** Horizontal scaling supported

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Ensure all tests pass
5. Submit a pull request

## 📄 License

MIT License - see LICENSE file for details.

---

**Built with ❤️ using FastAPI, Pydantic, and Python**
