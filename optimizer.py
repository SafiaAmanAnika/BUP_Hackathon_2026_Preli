import pulp


def optimize_energy(hours, battery, directives):

    # =========================================================
    # Validate input
    # =========================================================

    if len(hours) != 24:
        return {
            "status": "infeasible",
            "message": "Exactly 24 hours are required."
        }

    hour_numbers = [h.hour for h in hours]

    if sorted(hour_numbers) != list(range(24)):
        return {
            "status": "infeasible",
            "message": "Hours must contain exactly 0 through 23."
        }

    # =========================================================
    # Create optimization problem
    # =========================================================

    problem = pulp.LpProblem(
        "GridWise_Energy_Optimization",
        pulp.LpMinimize
    )

    # =========================================================
    # Decision variables
    # =========================================================

    grid = {
        h: pulp.LpVariable(
            f"grid_{h}",
            lowBound=0
        )
        for h in range(24)
    }

    charge = {
        h: pulp.LpVariable(
            f"charge_{h}",
            lowBound=0,
            upBound=battery.max_charge_kwh_per_hour
        )
        for h in range(24)
    }

    discharge = {
        h: pulp.LpVariable(
            f"discharge_{h}",
            lowBound=0,
            upBound=battery.max_discharge_kwh_per_hour
        )
        for h in range(24)
    }

    battery_energy = {
        h: pulp.LpVariable(
            f"battery_energy_{h}",
            lowBound=battery.minimum_energy_kwh,
            upBound=battery.capacity_kwh
        )
        for h in range(24)
    }

    # =========================================================
    # Effective solar after solar-reduction directives
    # =========================================================

    effective_solar = {
        h: hours[h].solar_kwh
        for h in range(24)
    }

    for directive in directives:

        if not directive.get("applies", False):
            continue

        if directive["directive_type"] != "solar_reduction":
            continue

        adjustment = directive["structured_adjustment"]

        factor = adjustment["factor"]

        for hour in adjustment["hours"]:

            if 0 <= hour <= 23:

                effective_solar[hour] *= factor

    # =========================================================
    # Objective: minimize total grid electricity cost
    # =========================================================

    problem += pulp.lpSum(
        grid[h] * hours[h].tariff_bdt_per_kwh
        for h in range(24)
    )

    # =========================================================
    # Energy balance
    #
    # solar + grid + discharge
    # =
    # demand + charge
    # =========================================================

    for h in range(24):

        problem += (
            effective_solar[h]
            + grid[h]
            + discharge[h]
            ==
            hours[h].demand_kwh
            + charge[h]
        ), f"EnergyBalance_{h}"

    # =========================================================
    # Battery transitions
    # =========================================================

    for h in range(24):

        if h == 0:
            previous_energy = battery.initial_energy_kwh
        else:
            previous_energy = battery_energy[h - 1]

        problem += (
            battery_energy[h]
            ==
            previous_energy
            + charge[h]
            - discharge[h]
        ), f"BatteryBalance_{h}"

    # =========================================================
    # Final battery energy must equal initial energy
    # =========================================================

    problem += (
        battery_energy[23]
        == battery.initial_energy_kwh
    ), "FinalBatteryEqualsInitial"

    # =========================================================
    # Apply operator directives
    # =========================================================

    for directive in directives:

        if not directive.get("applies", False):
            continue

        directive_type = directive["directive_type"]
        adjustment = directive["structured_adjustment"]

        affected_hours = adjustment.get("hours", [])

        for h in affected_hours:

            if h < 0 or h > 23:
                continue

            # -------------------------------------------------
            # Minimum battery reserve
            # -------------------------------------------------

            if directive_type == "minimum_battery_reserve":

                minimum_energy = adjustment[
                    "minimum_energy_kwh"
                ]

                problem += (
                    battery_energy[h]
                    >= minimum_energy
                ), f"MinimumReserve_{h}"

            # -------------------------------------------------
            # No charging
            # -------------------------------------------------

            elif directive_type == "no_charge_window":

                problem += (
                    charge[h] == 0
                ), f"NoCharge_{h}"

            # -------------------------------------------------
            # No discharging
            # -------------------------------------------------

            elif directive_type == "no_discharge_window":

                problem += (
                    discharge[h] == 0
                ), f"NoDischarge_{h}"

            # -------------------------------------------------
            # Maximum grid import
            # -------------------------------------------------

            elif directive_type == "max_grid_window":

                maximum_grid = adjustment[
                    "max_grid_kwh"
                ]

                problem += (
                    grid[h] <= maximum_grid
                ), f"GridLimit_{h}"

    # =========================================================
    # Solve
    # =========================================================

    status = problem.solve(
        pulp.PULP_CBC_CMD(msg=False)
    )

    if pulp.LpStatus[status] != "Optimal":

        return {
            "status": "infeasible",
            "message": (
                "No feasible 24-hour schedule satisfies "
                "all constraints."
            )
        }

    # =========================================================
    # Build hourly plan
    # =========================================================

    hourly_plan = []

    for h in range(24):

        grid_value = pulp.value(grid[h])
        charge_value = pulp.value(charge[h])
        discharge_value = pulp.value(discharge[h])
        battery_value = pulp.value(battery_energy[h])

        hourly_plan.append({
            "hour": hours[h].hour,
            "demand_kwh": round(
                hours[h].demand_kwh, 4
            ),
            "solar_kwh": round(
                effective_solar[h], 4
            ),
            "grid_kwh": round(
                grid_value, 4
            ),
            "battery_charge_kwh": round(
                charge_value, 4
            ),
            "battery_discharge_kwh": round(
                discharge_value, 4
            ),
            "battery_energy_kwh": round(
                battery_value, 4
            ),
            "tariff_bdt_per_kwh": round(
                hours[h].tariff_bdt_per_kwh, 4
            )
        })

    # =========================================================
    # Recalculate totals FROM hourly_plan
    # =========================================================

    total_grid_kwh = sum(
        row["grid_kwh"]
        for row in hourly_plan
    )

    total_cost_bdt = sum(
        row["grid_kwh"]
        * row["tariff_bdt_per_kwh"]
        for row in hourly_plan
    )

    peak_grid_kwh = max(
        row["grid_kwh"]
        for row in hourly_plan
    )

    # =========================================================
    # Return result
    # =========================================================

    return {
        "status": "optimal",
        "hourly_plan": hourly_plan,
        "total_grid_kwh": round(
            total_grid_kwh, 4
        ),
        "total_cost_bdt": round(
            total_cost_bdt, 4
        ),
        "peak_grid_kwh": round(
            peak_grid_kwh, 4
        )
    }