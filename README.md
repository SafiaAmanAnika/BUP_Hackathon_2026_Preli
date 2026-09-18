<div align="center">

# GRIDWISE ENERGY OPTIMIZATION API

[![Python](https://img.shields.io/badge/Python-3.10%2B-3776AB?style=flat-square\&logo=python\&logoColor=white)](#)
[![FastAPI](https://img.shields.io/badge/FastAPI-API-009688?style=flat-square\&logo=fastapi\&logoColor=white)](#)
[![PuLP](https://img.shields.io/badge/Optimization-PuLP-orange?style=flat-square)](#)
[![Gemini](https://img.shields.io/badge/AI-Gemini-4285F4?style=flat-square\&logo=google\&logoColor=white)](#)
[![Deployment](https://img.shields.io/badge/Deployment-Render-46E3B7?style=flat-square\&logo=render\&logoColor=black)](#)
[![Status](https://img.shields.io/badge/Status-Deployed-brightgreen?style=flat-square)](#)

<br>

<i>GridWise is an AI-assisted energy optimization API that converts natural-language operator notes into structured energy directives and generates a cost-efficient 24-hour electricity schedule using constrained mathematical optimization.</i>

<br>

<a href="#overview">Overview</a>  🔷 <a href="#workflow">System Workflow</a>  🔷 <a href="#features">Core Features</a>  🔷 <a href="#architecture">Architecture</a>  🔷 <a href="#installation">Installation</a>  🔷 <a href="#api">API Integration</a>  🔷 <a href="#testing">Testing</a>  🔷 <a href="#deployment">Deployment</a>

</div>

---

<a name="overview"></a>

## Overview

GridWise combines **natural-language processing** with **linear programming** to optimize energy usage over a 24-hour planning horizon.

Operators provide notes describing operational constraints or changes. For example:

> "Solar output will drop to about 20% from 1 PM to 3 PM."

The system interprets the note as a structured directive:

```json
{
  "directive_type": "solar_reduction",
  "hours": [13, 14],
  "value": 0.2
}
```

The validated directive is then incorporated into the optimization model together with:

* Hourly electricity demand
* Solar generation
* Electricity tariffs
* Battery capacity
* Initial battery energy
* Minimum battery energy
* Battery charging limits
* Battery discharging limits

The resulting schedule satisfies the supplied operational constraints while minimizing total grid electricity cost.

---

<a name="workflow"></a>

## System Workflow

```text
┌───────────────────────────┐
│     Operator Notes        │
│   Natural-language text   │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│     Gemini Interpreter    │
│  Note → Energy Directive  │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│       Validator           │
│ Validate type, hours,     │
│ values and ranges         │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│    PuLP Optimization      │
│ Cost minimization under   │
│ energy and battery rules  │
└─────────────┬─────────────┘
              │
              ▼
┌───────────────────────────┐
│      24-Hour Plan         │
│ Grid / Solar / Battery    │
│ Cost / Peak Grid          │
└───────────────────────────┘
```

The complete request follows:

```text
Natural Language
       ↓
Directive Interpretation
       ↓
Validation
       ↓
Constraint Application
       ↓
Linear Optimization
       ↓
24-Hour Energy Schedule
       ↓
JSON Response
```

---

<a name="features"></a>

## Core Features

<details>
<summary><b>Natural-Language Directive Interpretation</b> — Gemini-based operator note processing</summary>

<br>

Gemini interprets operator notes and classifies them into supported energy directives.

| Directive                 | Description                                               |
| ------------------------- | --------------------------------------------------------- |
| `solar_reduction`         | Reduces available solar generation during specified hours |
| `minimum_battery_reserve` | Maintains a minimum battery energy level                  |
| `no_charge_window`        | Prevents battery charging during specified hours          |
| `no_discharge_window`     | Prevents battery discharging during specified hours       |
| `max_grid_window`         | Limits grid consumption during specified hours            |
| `no_op`                   | Identifies notes with no scheduling impact                |

The parser is designed to recognize variations in natural-language wording while producing a consistent structured representation.

<br>

</details>

<details>
<summary><b>Directive Validation</b> — Structured validation before optimization</summary>

<br>

Every parsed directive is validated before entering the optimization model.

Validation includes:

* Allowed directive type checking
* Hour normalization
* Hour range validation (`0`–`23`)
* Numeric value validation
* Solar reduction factor validation (`0`–`1`)
* Non-negative battery reserve validation
* Non-negative grid limit validation
* `no_op` normalization

Invalid directives are rejected rather than silently passed to the optimizer.

<br>

</details>

<details>
<summary><b>24-Hour Energy Optimization</b> — Constrained linear programming</summary>

<br>

The optimizer uses **PuLP** to formulate and solve a linear programming problem.

The objective is:

```text
Minimize:
Σ(grid energy × hourly electricity tariff)
```

Subject to:

* Hourly energy balance
* Battery energy balance
* Battery capacity
* Minimum battery energy
* Maximum charging rate
* Maximum discharging rate
* Initial battery energy
* Final battery energy equal to initial energy
* Solar availability
* Operator-defined constraints

<br>

</details>

<details>
<summary><b>Battery Management</b> — Hour-by-hour energy tracking</summary>

<br>

Battery energy is tracked throughout the complete planning horizon.

For each hour:

```text
Battery Energy(t)
=
Battery Energy(t-1)
+ Charge(t)
- Discharge(t)
```

The model enforces:

```text
Minimum Energy ≤ Battery Energy ≤ Capacity
```

and:

```text
0 ≤ Charge(t) ≤ Maximum Charge Rate
0 ≤ Discharge(t) ≤ Maximum Discharge Rate
```

The final battery energy is constrained to equal the initial battery energy.

<br>

</details>

<details>
<summary><b>Solar Adjustment</b> — Operational changes to solar availability</summary>

<br>

Solar-reduction directives modify the available solar energy before optimization.

For example:

```json
{
  "hours": [13, 14],
  "factor": 0.2
}
```

means:

```text
Effective Solar = Original Solar × 0.2
```

For:

```text
Hour 13 → 130 kWh
Hour 14 → 140 kWh
```

the optimizer receives:

```text
Hour 13 → 26 kWh
Hour 14 → 28 kWh
```

<br>

</details>

<details>
<summary><b>Optimization Results</b> — Detailed 24-hour scheduling output</summary>

<br>

The API returns:

* Hourly energy schedule
* Grid consumption
* Solar availability
* Battery charging
* Battery discharging
* Battery energy
* Hourly tariff
* Total grid consumption
* Total electricity cost
* Peak grid consumption
* Optimization status

<br>

</details>

---

<a name="architecture"></a>

## Architecture

GridWise uses a lightweight modular architecture. Each major responsibility is isolated into a separate module for easier testing and maintenance.

```text
┌─────────────────────────────────────────────────────────┐
│                     FastAPI API                         │
│                       main.py                           │
│                                                         │
│               POST /optimize-energy                     │
│               GET  /health                              │
└──────────────────────────┬──────────────────────────────┘
                           │
             ┌─────────────┴─────────────┐
             │                           │
             ▼                           ▼
┌─────────────────────────┐   ┌─────────────────────────┐
│       models.py         │   │        parser.py        │
│                         │   │                         │
│ Pydantic request models │   │ Gemini interpretation   │
│ HourData                │   │ Natural language → JSON │
│ Battery                 │   │                         │
│ OptimizeRequest         │   │                         │
└────────────┬────────────┘   └────────────┬────────────┘
             │                             │
             │                             ▼
             │                  ┌─────────────────────────┐
             │                  │      validator.py       │
             │                  │                         │
             │                  │ Directive validation   │
             │                  └────────────┬────────────┘
             │                               │
             └───────────────┬───────────────┘
                             ▼
                  ┌─────────────────────────┐
                  │      optimizer.py       │
                  │                         │
                  │       PuLP LP           │
                  │ Cost minimization       │
                  │ Energy constraints      │
                  │ Battery constraints     │
                  └────────────┬────────────┘
                               │
                               ▼
                  ┌─────────────────────────┐
                  │      JSON Response      │
                  │                         │
                  │ Directives + 24h Plan   │
                  │ Cost + Grid Statistics  │
                  └─────────────────────────┘
```

### Project Structure

```text
BUP_Hackathon_2026_Preli/
│
├── main.py                 # FastAPI application and API endpoint
├── models.py               # Pydantic request models
├── parser.py               # Gemini directive interpretation
├── validator.py            # Directive validation and normalization
├── optimizer.py             # PuLP optimization model
│
├── requirements.txt        # Python dependencies
├── test_optimizer.py       # Direct optimizer test
├── test_request.json       # API test request
│
├── .env                    # Local environment variables
└── .gitignore              # Ignored files and secrets
```

---

<a name="installation"></a>

## Installation

### Prerequisites

| Requirement    | Version                               |
| -------------- | ------------------------------------- |
| Python         | 3.10+                                 |
| pip            | Recommended latest version            |
| Git            | Required for repository setup         |
| Gemini API Key | Required for directive interpretation |

### Setup

```bash
# 1. Clone the repository
git clone <repository-url>

# 2. Enter the project directory
cd BUP_Hackathon_2026_Preli

# 3. Create a virtual environment
python -m venv venv

# 4. Activate the virtual environment
# Windows PowerShell
venv\Scripts\Activate.ps1

# Windows Git Bash
source venv/Scripts/activate

# 5. Install dependencies
pip install -r requirements.txt
```

### Environment Configuration

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_gemini_api_key_here
```

The `.env` file is excluded from version control.

### Run the API

```bash
python -m uvicorn main:app --reload
```

The API will be available at:

```text
http://127.0.0.1:8000
```

Swagger documentation:

```text
http://127.0.0.1:8000/docs
```

Health check:

```text
http://127.0.0.1:8000/health
```

Expected response:

```json
{
  "status": "ok"
}
```

---

<a name="api"></a>

## API Integration

### `GET /health`

Returns the current API service status.

#### Response

```json
{
  "status": "ok"
}
```

---

### `POST /optimize-energy`

Processes operator notes and generates an optimized 24-hour energy schedule.

#### Request

```json
{
  "scenario_id": "test-one",
  "operator_notes": [
    "Solar output will drop to about 20% from 1 PM to 3 PM."
  ],
  "hours": [
    {
      "hour": 13,
      "demand_kwh": 100,
      "solar_kwh": 130,
      "tariff_bdt_per_kwh": 12
    }
  ],
  "battery": {
    "capacity_kwh": 300,
    "initial_energy_kwh": 150,
    "minimum_energy_kwh": 50,
    "max_charge_kwh_per_hour": 50,
    "max_discharge_kwh_per_hour": 50
  }
}
```

The API requires exactly **24 hourly records**, containing one record for every hour from `0` through `23`.

#### Response Structure

```json
{
  "scenario_id": "test-one",
  "directive_interpretation": [],
  "optimization": {
    "status": "optimal",
    "hourly_plan": [],
    "total_grid_kwh": 0,
    "total_cost_bdt": 0,
    "peak_grid_kwh": 0
  }
}
```

### Interactive Documentation

FastAPI provides an interactive Swagger UI at:

```text
/docs
```

The endpoint can be tested directly through the browser without an external API client.

---

<a name="testing"></a>

## Testing

### Optimizer Testing

The optimization model can be tested independently of Gemini:

```bash
python test_optimizer.py
```

The verified test produced:

```text
status: optimal
total_grid_kwh: 1221.0
total_cost_bdt: 10222.0
peak_grid_kwh: 140.0
```

The test also verified the solar-reduction directive:

```text
Original:
Hour 13 → 130 kWh
Hour 14 → 140 kWh

After 20% reduction factor:
Hour 13 → 26 kWh
Hour 14 → 28 kWh
```

### API Testing

Start the application:

```bash
python -m uvicorn main:app --reload
```

Then open:

```text
http://127.0.0.1:8000/docs
```

Select:

```text
POST /optimize-energy
```

and provide the test request.

### Deployment Testing

The deployed service was verified using:

```text
GET /health
```

and the FastAPI Swagger interface:

```text
/docs
```

The deployed application successfully started and responded to API requests.

---

<a name="deployment"></a>

## Deployment

The API is deployed as a **Render Web Service**.

### Render Configuration

**Build Command**

```bash
pip install -r requirements.txt
```

**Start Command**

```bash
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Environment Variables

The deployed service requires:

```text
GEMINI_API_KEY
```

The API key is configured through Render environment variables and is not committed to the repository.

### Deployment Workflow

```text
GitHub Repository
       │
       ▼
Render Web Service
       │
       ├── Install dependencies
       ├── Load environment variables
       ├── Start FastAPI
       │
       ▼
Public API
```

---

## Optimization Model

The optimization objective minimizes the cost of electricity purchased from the grid:

```text
Minimize:
Σ(grid[h] × tariff[h])
```

For every hour, the energy balance is:

```text
Solar[h] + Grid[h] + BatteryDischarge[h]
=
Demand[h] + BatteryCharge[h]
```

Battery evolution is:

```text
BatteryEnergy[h]
=
PreviousBatteryEnergy
+ BatteryCharge[h]
- BatteryDischarge[h]
```

The model enforces:

```text
Minimum Battery Energy
≤
Battery Energy
≤
Battery Capacity
```

and:

```text
0 ≤ Charge[h] ≤ Maximum Charge Rate
0 ≤ Discharge[h] ≤ Maximum Discharge Rate
```

The final battery energy is constrained to equal the initial battery energy.

---

## Technology Stack

| Technology        | Purpose                                   |
| ----------------- | ----------------------------------------- |
| **Python**        | Core application logic                    |
| **FastAPI**       | REST API framework                        |
| **Pydantic**      | Request validation and data modeling      |
| **Google Gemini** | Natural-language directive interpretation |
| **PuLP**          | Linear programming and optimization       |
| **Uvicorn**       | ASGI application server                   |
| **python-dotenv** | Environment variable management           |
| **Render**        | Cloud deployment                          |
| **Git / GitHub**  | Version control and source hosting        |

---

## Security

* Gemini API credentials are stored in environment variables.
* `.env` is excluded from version control.
* API credentials are not hard-coded into the source code.
* Parsed directives are validated before reaching the optimization model.
* Incomplete or invalid 24-hour schedules are rejected.

---

## Supported Operator Directives

### Solar Reduction

```text
PV production will drop to about 20% between 13:00 and 15:00.
```

Produces:

```json
{
  "directive_type": "solar_reduction",
  "hours": [13, 14],
  "value": 0.2
}
```

### Minimum Battery Reserve

```text
Keep at least 120 kWh in the battery from 6 PM to 9 PM.
```

### No Charging

```text
Do not charge the battery between 2 PM and 4 PM.
```

### No Discharging

```text
Do not discharge the battery between 5 PM and 8 PM.
```

### Maximum Grid Usage

```text
Grid consumption must stay below 80 kWh from 6 PM to 9 PM.
```

### No Operation

Notes with no effect on energy scheduling are classified as:

```json
{
  "directive_type": "no_op"
}
```

---

## Project Status

```text
✓ Natural-language directive interpretation
✓ Directive validation
✓ Solar reduction constraints
✓ Battery reserve constraints
✓ No-charge constraints
✓ No-discharge constraints
✓ Grid consumption limits
✓ 24-hour linear optimization
✓ Cost minimization
✓ API implementation
✓ Optimizer testing
✓ API testing
✓ Cloud deployment
✓ Deployment verification
```

**Status: Completed and deployed.**

---

<div align="center">

<br>

<b>GRIDWISE — AI-ASSISTED ENERGY OPTIMIZATION</b>

<br><br>

<i>Natural-language operational constraints translated into optimized energy schedules.</i>

</div>