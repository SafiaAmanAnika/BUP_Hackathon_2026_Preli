from fastapi import FastAPI
from models import OptimizeRequest
from parser import interpret_note
from validator import validate_parsed_output

app = FastAPI()


@app.get("/health")
def health():
    return {"status": "ok"}


def build_directive(note_index, parsed):

    dtype = parsed["directive_type"]

    if dtype == "no_op":
        return {
            "note_index": note_index,
            "applies": False,
            "directive_type": "no_op",
            "structured_adjustment": None,
            "explanation": "No impact on energy scheduling."
        }

    adjustment = {}

    if dtype == "solar_reduction":
        adjustment = {
            "hours": parsed["hours"],
            "factor": parsed["value"]
        }

    elif dtype == "minimum_battery_reserve":
        adjustment = {
            "hours": parsed["hours"],
            "minimum_energy_kwh": parsed["value"]
        }

    elif dtype == "max_grid_window":
        adjustment = {
            "hours": parsed["hours"],
            "max_grid_kwh": parsed["value"]
        }

    elif dtype in [
        "no_charge_window",
        "no_discharge_window"
    ]:
        adjustment = {
            "hours": parsed["hours"]
        }

    return {
        "note_index": note_index,
        "applies": True,
        "directive_type": dtype,
        "structured_adjustment": adjustment,
        "explanation": f"Interpreted as {dtype}"
    }


@app.post("/optimize-energy")
def optimize_energy(request: OptimizeRequest):

    directives = []

    for i, note in enumerate(request.operator_notes):

        parsed = interpret_note(note)
        parsed = validate_parsed_output(parsed)

        directives.append(
            build_directive(i, parsed)
        )

    return {
        "scenario_id": request.scenario_id,
        "directive_interpretation": directives
    }