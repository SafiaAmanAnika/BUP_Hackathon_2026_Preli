import pulp


def optimize_energy(hours, battery, directives):
    """
    Optimize hourly energy scheduling using PuLP.

    hours:
        List of HourData objects.

    battery:
        Battery object.

    directives:
        List of parsed directive dictionaries from build_directive().
    """

    # ---------------------------------------------------------
    # Create optimization problem
    # ---------------------------------------------------------

    problem = pulp.LpProblem(
        "Energy_Optimization",
        pulp.LpMinimize
    )

    n = len(hours)

    # ---------------------------------------------------------
    # Decision variables
    # ---------------------------------------------------------

    grid = {
        i: pulp.LpVariable(
            f"grid_{i}",
            lowBound=0
        )
        for i in range(n)
    }

    charge = {
        i: pulp.LpVariable(
            f"charge_{i}",
            lowBound=0,
            upBound=battery.max_charge_kwh_per_hour
        )
        for i in range(n)
    }

    discharge = {
        i: pulp.LpVariable(
            f"discharge_{i}",
            lowBound=0,
            upBound=battery.max_discharge_kwh_per_hour
        )
        for i in range(n)
    }

    energy = {
        i: pulp.LpVariable(
            f"battery_energy_{i}",
            lowBound=battery.minimum_energy_kwh,
            upBound=battery.capacity_kwh
        )
        for i in range(n)
    }

    # Binary variables prevent charging and discharging
    # at the same time.
    charging = {
        i: pulp.LpVariable(
            f"is_charging_{i}",
            cat="Binary"
        )
        for i in range(n)
    }

    # ---------------------------------------------------------
    # Objective: minimize grid electricity cost
    # ---------------------------------------------------------

    problem += pulp.lpSum(
        grid[i] * hours[i].tariff_bdt_per_kwh
        for i in range(n)
    )

    # ---------------------------------------------------------
    # Battery charge/discharge constraints
    # ---------------------------------------------------------

    for i in range(n):

        problem += (
            charge[i]
            <= battery.max_charge_kwh_per_hour * charging[i]
        )

        problem += (
            discharge[i]
            <= battery.max_discharge_kwh_per_hour
            * (1 - charging[i])
        )

    # ---------------------------------------------------------
    # Hourly energy balance
    # ---------------------------------------------------------

    for i in range(n):

        solar = hours[i].solar_kwh

        # Check whether a solar reduction applies to this hour.
        for directive in directives:

            if (
                directive.get("applies", True)
                and directive["directive_type"] == "solar_reduction"
            ):

                adjustment = directive.get(
                    "structured_adjustment"
                )

                if adjustment and hours[i].hour in adjustment.get("hours", []):

                    factor = adjustment["factor"]

                    solar = (
                        solar * factor / 100
                    )

        problem += (
            solar
            + grid[i]
            + discharge[i]
            ==
            hours[i].demand_kwh
            + charge[i]
        )

    # ---------------------------------------------------------
    # Battery energy balance
    # ---------------------------------------------------------

    for i in range(n):

        if i == 0:
            previous_energy = battery.initial_energy_kwh
        else:
            previous_energy = energy[i - 1]

        problem += (
            energy[i]
            ==
            previous_energy
            + charge[i]
            - discharge[i]
        )

    # ---------------------------------------------------------
    # Apply operator directives
    # ---------------------------------------------------------

    for directive in directives:

        if not directive.get("applies", True):
            continue

        directive_type = directive["directive_type"]

        adjustment = directive.get(
            "structured_adjustment"
        )

        if not adjustment:
            continue

        directive_hours = adjustment.get(
            "hours",
            []
        )

        for hour_number in directive_hours:

            # Find the corresponding optimization index.
            matching_indices = [
                i
                for i, hour_data in enumerate(hours)
                if hour_data.hour == hour_number
            ]

            for i in matching_indices:

                # ---------------------------------------------
                # Minimum battery reserve
                # ---------------------------------------------

                if directive_type == "minimum_battery_reserve":

                    minimum_energy = adjustment[
                        "minimum_energy_kwh"
                    ]

                    problem += (
                        energy[i]
                        >= minimum_energy
                    )

                # ---------------------------------------------
                # No battery charging
                # ---------------------------------------------

                elif directive_type == "no_charge_window":

                    problem += (
                        charge[i] == 0
                    )

                # ---------------------------------------------
                # No battery discharging
                # ---------------------------------------------

                elif directive_type == "no_discharge_window":

                    problem += (
                        discharge[i] == 0
                    )

                # ---------------------------------------------
                # Maximum grid import
                # ---------------------------------------------

                elif directive_type == "max_grid_window":

                    maximum_grid = adjustment[
                        "max_grid_kwh"
                    ]

                    problem += (
                        grid[i] <= maximum_grid
                    )

    # ---------------------------------------------------------
    # Solve
    # ---------------------------------------------------------

    status = problem.solve(
        pulp.PULP_CBC_CMD(msg=False)
    )

    if pulp.LpStatus[status] != "Optimal":
        return {
            "status": "infeasible",
            "message": (
                "No feasible energy schedule satisfies "
                "all constraints."
            )
        }

    # ---------------------------------------------------------
    # Build result
    # ---------------------------------------------------------

    schedule = []

    for i in range(n):

        schedule.append({
            "hour": hours[i].hour,
            "demand_kwh": hours[i].demand_kwh,
            "solar_kwh": hours[i].solar_kwh,
            "grid_kwh": round(
                pulp.value(grid[i]), 4
            ),
            "battery_charge_kwh": round(
                pulp.value(charge[i]), 4
            ),
            "battery_discharge_kwh": round(
                pulp.value(discharge[i]), 4
            ),
            "battery_energy_kwh": round(
                pulp.value(energy[i]), 4
            ),
            "tariff_bdt_per_kwh": (
                hours[i].tariff_bdt_per_kwh
            )
        })

    total_cost = sum(
        item["grid_kwh"]
        * item["tariff_bdt_per_kwh"]
        for item in schedule
    )

    total_grid = sum(
        item["grid_kwh"]
        for item in schedule
    )

    return {
        "status": "optimal",
        "total_cost_bdt": round(total_cost, 2),
        "total_grid_import_kwh": round(total_grid, 4),
        "schedule": schedule
    }