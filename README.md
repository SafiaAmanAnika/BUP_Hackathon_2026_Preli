<h1 align="center">SmartGrid ENERGY OPTIMIZATION API</h1>

<p align="center">
  <strong>Natural-language energy directives converted into optimized 24-hour energy schedules.</strong>
</p>

<p align="center">
  <a href="https://bup-hackathon-2026-preli.onrender.com"><strong>Live API / Swagger Docs</strong></a>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10%2B-blue">
  <img src="https://img.shields.io/badge/FastAPI-0.115.0-009688">
  <img src="https://img.shields.io/badge/PuLP-3.3.2-orange">
  <img src="https://img.shields.io/badge/Google%20Gemini-API-yellow">
  <img src="https://img.shields.io/badge/Deployed-Render-purple">
</p>

---

## Navigation

<p align="center">
  <a href="#overview">Overview</a> 🔷
  <a href="#installation">Installation</a> 🔷
  <a href="#api-usage">API Usage</a> 🔷
  <a href="#testing">Testing</a> 🔷
  <a href="#project-structure">Project Structure</a> 🔷
  <a href="#technology-stack">Technology Stack</a> 🔷
  <a href="#deployment">Deployment</a>
</p>

---

## Overview

**GridWise** is an energy optimization API that converts operator instructions written in natural language into structured energy constraints and generates an optimized 24-hour energy schedule.

For example:

> "Expect an 80% reduction in rooftop solar during the 1–3 PM maintenance window."

The system interprets the instruction using **Google Gemini**, validates the resulting directive, and applies it to a **PuLP linear programming model**.

### System Workflow

```text
Operator Note
      │
      ▼
Google Gemini
      │
      ▼
Structured Directive
      │
      ▼
Validation
      │
      ▼
PuLP Optimization
      │
      ▼
24-Hour Energy Schedule
```

---

## Live Demo

<p align="center">

**Swagger API Documentation**

<a href="https://bup-hackathon-2026-preli.onrender.com/docs">
https://bup-hackathon-2026-preli.onrender.com/docs
</a>

</p>

The deployed API can be tested directly through the Swagger interface.

---

## Installation

<details>
<summary><strong>1. Clone the Repository</strong></summary>

```bash
git clone https://github.com/SafiaAmanAnika/BUP_Hackathon_2026_Preli.git
cd BUP_Hackathon_2026_Preli
```

</details>

<details>
<summary><strong>2. Install Dependencies</strong></summary>

```bash
pip install -r requirements.txt
```

</details>

<details>
<summary><strong>3. Configure Gemini API</strong></summary>

Create a `.env` file in the project root:

```env
GEMINI_API_KEY=your_api_key_here
```

</details>

<details>
<summary><strong>4. Run the API</strong></summary>

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

</details>

---

## API Usage

### `GET /health`

Checks whether the API is running.

```json
{
  "status": "ok"
}
```

### `POST /optimize-energy`

Accepts a 24-hour energy scenario together with natural-language operator instructions.

Example:

```json
{
  "scenario_id": "demo-001",
  "operator_notes": [
    "Expect an 80% reduction in rooftop solar during the 1-3 PM maintenance window."
  ],
  "hours": [
    {
      "hour": 0,
      "demand_kwh": 100,
      "solar_kwh": 0,
      "tariff_bdt_per_kwh": 8
    }
  ],
  "battery": {
    "capacity_kwh": 300,
    "initial_energy_kwh": 150,
    "minimum_energy_kwh": 50,
    "max_charge_kwh_per_hour": 40,
    "max_discharge_kwh_per_hour": 40
  }
}
```

The response provides:

* Interpreted operator directives
* Hourly energy schedule
* Grid usage
* Battery charging and discharging
* Total grid energy
* Total electricity cost
* Peak grid usage

---

## Supported Directives

| Directive                   | Example                                        |
| --------------------------- | ---------------------------------------------- |
| **Solar reduction**         | Reduce solar output to 20% from 1–3 PM         |
| **Minimum battery reserve** | Keep at least 100 kWh in the battery           |
| **No charging window**      | Do not charge from 6–8 PM                      |
| **No discharging window**   | Do not discharge during maintenance            |
| **Maximum grid usage**      | Limit grid usage during specified hours        |
| **No operation**            | Informational note with no optimization impact |

---

## Testing

Run the optimizer test with:

```bash
python test_optimizer.py
```

The test verifies that the optimization model produces a feasible 24-hour schedule and correctly applies operator constraints.

Example verified result:

```text
status: optimal
total_grid_kwh: 1221.0
total_cost_bdt: 10222.0
peak_grid_kwh: 140.0
```

The solar-reduction test also correctly changed:

```text
Hour 13: 130 kWh → 26 kWh
Hour 14: 140 kWh → 28 kWh
```

---

## Project Structure

```text
BUP_Hackathon_2026_Preli/
│
├── main.py              # FastAPI application and endpoints
├── models.py            # Request data models
├── parser.py            # Gemini directive interpretation
├── validator.py         # Directive validation
├── optimizer.py         # PuLP optimization model
├── test_optimizer.py    # Optimizer test
├── test_request.json    # Sample request
├── requirements.txt     # Python dependencies
├── .env                 # API configuration
└── .gitignore
```

---

## Technology Stack

| Technology        | Purpose                                   |
| ----------------- | ----------------------------------------- |
| **Python**        | Core programming language                 |
| **FastAPI**       | REST API framework                        |
| **Google Gemini** | Natural-language directive interpretation |
| **PuLP**          | Linear programming optimization           |
| **Pydantic**      | Request validation                        |
| **Uvicorn**       | ASGI server                               |
| **Render**        | Deployment                                |

---

## Deployment

The application is deployed on **Render**.

### Build Command

```bash
pip install -r requirements.txt
```

### Start Command

```bash
python -m uvicorn main:app --host 0.0.0.0 --port $PORT
```

### Environment Variable

```text
GEMINI_API_KEY
```

### Deployment Flow

```text
GitHub Repository
       │
       ▼
     Render
       │
       ▼
FastAPI Application
       │
       ▼
Swagger API
```

---

## Repository

**GitHub:**
https://github.com/SafiaAmanAnika/BUP_Hackathon_2026_Preli

**Live API:**
https://bup-hackathon-2026-preli.onrender.com

---

<p align="center">
  <strong>🔷 SmartGrid — AI-assisted energy optimization through natural-language directives and mathematical optimization 🔷</strong>
</p>

---
