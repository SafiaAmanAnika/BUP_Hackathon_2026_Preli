ALLOWED_DIRECTIVES = {
    "solar_reduction",
    "minimum_battery_reserve",
    "no_charge_window",
    "no_discharge_window",
    "max_grid_window",
    "no_op"
}


def normalize_hours(hours):

    if not isinstance(hours, list):
        return []

    hours = sorted(set(hours))

    return [
        h for h in hours
        if isinstance(h, int) and 0 <= h <= 23
    ]


def validate_parsed_output(parsed):

    if not isinstance(parsed, dict):
        raise ValueError("Parser output must be a JSON object.")

    directive_type = parsed.get("directive_type")

    if directive_type not in ALLOWED_DIRECTIVES:
        raise ValueError(
            f"Invalid directive_type: {directive_type}"
        )

    parsed["hours"] = normalize_hours(
        parsed.get("hours", [])
    )

    if directive_type == "no_op":
        parsed["hours"] = []
        parsed["value"] = None

    elif directive_type in {
        "no_charge_window",
        "no_discharge_window"
    }:
        parsed["value"] = None

    elif directive_type == "solar_reduction":
        value = parsed.get("value")

        if not isinstance(value, (int, float)):
            raise ValueError(
                "solar_reduction requires a numeric value."
            )

        if not 0 <= value <= 100:
            raise ValueError(
                "Solar reduction value must be between 0 and 100."
            )

    elif directive_type == "minimum_battery_reserve":
        value = parsed.get("value")

        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(
                "minimum_battery_reserve requires a non-negative value."
            )

    elif directive_type == "max_grid_window":
        value = parsed.get("value")

        if not isinstance(value, (int, float)) or value < 0:
            raise ValueError(
                "max_grid_window requires a non-negative value."
            )

    return parsed