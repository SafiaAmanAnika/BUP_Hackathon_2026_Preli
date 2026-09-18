from optimizer import optimize_energy
from models import HourData, Battery


hours = [
    HourData(hour=0, demand_kwh=100, solar_kwh=20, tariff_bdt_per_kwh=8),
    HourData(hour=1, demand_kwh=100, solar_kwh=20, tariff_bdt_per_kwh=8),
    HourData(hour=2, demand_kwh=100, solar_kwh=20, tariff_bdt_per_kwh=8),
    HourData(hour=3, demand_kwh=100, solar_kwh=20, tariff_bdt_per_kwh=8),
    HourData(hour=4, demand_kwh=100, solar_kwh=20, tariff_bdt_per_kwh=8),
    HourData(hour=5, demand_kwh=100, solar_kwh=20, tariff_bdt_per_kwh=8),
    HourData(hour=6, demand_kwh=100, solar_kwh=30, tariff_bdt_per_kwh=9),
    HourData(hour=7, demand_kwh=100, solar_kwh=40, tariff_bdt_per_kwh=9),
    HourData(hour=8, demand_kwh=100, solar_kwh=50, tariff_bdt_per_kwh=10),
    HourData(hour=9, demand_kwh=100, solar_kwh=60, tariff_bdt_per_kwh=10),
    HourData(hour=10, demand_kwh=100, solar_kwh=80, tariff_bdt_per_kwh=11),
    HourData(hour=11, demand_kwh=100, solar_kwh=100, tariff_bdt_per_kwh=11),
    HourData(hour=12, demand_kwh=100, solar_kwh=120, tariff_bdt_per_kwh=12),
    HourData(hour=13, demand_kwh=100, solar_kwh=130, tariff_bdt_per_kwh=12),
    HourData(hour=14, demand_kwh=100, solar_kwh=140, tariff_bdt_per_kwh=12),
    HourData(hour=15, demand_kwh=100, solar_kwh=130, tariff_bdt_per_kwh=11),
    HourData(hour=16, demand_kwh=100, solar_kwh=110, tariff_bdt_per_kwh=11),
    HourData(hour=17, demand_kwh=100, solar_kwh=90, tariff_bdt_per_kwh=10),
    HourData(hour=18, demand_kwh=100, solar_kwh=70, tariff_bdt_per_kwh=10),
    HourData(hour=19, demand_kwh=100, solar_kwh=50, tariff_bdt_per_kwh=10),
    HourData(hour=20, demand_kwh=100, solar_kwh=30, tariff_bdt_per_kwh=9),
    HourData(hour=21, demand_kwh=100, solar_kwh=20, tariff_bdt_per_kwh=9),
    HourData(hour=22, demand_kwh=100, solar_kwh=15, tariff_bdt_per_kwh=8),
    HourData(hour=23, demand_kwh=100, solar_kwh=10, tariff_bdt_per_kwh=8),
]

battery = Battery(
    capacity_kwh=300,
    initial_energy_kwh=150,
    minimum_energy_kwh=50,
    max_charge_kwh_per_hour=50,
    max_discharge_kwh_per_hour=50
)

directives = [
    {
        "note_index": 0,
        "applies": True,
        "directive_type": "solar_reduction",
        "structured_adjustment": {
            "hours": [13, 14],
            "factor": 0.2
        }
    }
]

result = optimize_energy(hours, battery, directives)

print(result)