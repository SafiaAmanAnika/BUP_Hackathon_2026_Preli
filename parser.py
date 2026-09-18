import json
import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel("gemini-3.6-flash")


def interpret_note(note: str):

    prompt = f"""
You are an energy directive classifier.

Your task is to convert ONE operator note into ONE structured energy directive.

Allowed directive types:

- solar_reduction
- minimum_battery_reserve
- no_charge_window
- no_discharge_window
- max_grid_window
- no_op

Return ONLY valid JSON.
Do not use markdown.
Do not include explanations outside the JSON.

Schema:

{{
    "directive_type": "...",
    "hours": [],
    "value": null
}}

RULES:

1. TIME RANGES

Use 24-hour integer format.

The END of a time range is EXCLUSIVE.

Examples:

"1 PM to 3 PM" -> [13, 14]
"6 PM until 9 PM" -> [18, 19, 20]
"2 PM to 4 PM" -> [14, 15]
"midnight to 4 AM" -> [0, 1, 2, 3]
"5 PM to 8 PM" -> [17, 18, 19]

2. SOLAR REDUCTION

If the note says solar output will drop/reduce TO a percentage:

directive_type = "solar_reduction"

hours = affected hourly slots

value = remaining solar fraction as a decimal between 0 and 1

Examples:

"Solar output will drop to about 20% from 1 PM to 3 PM"
-> {{"directive_type":"solar_reduction","hours":[13,14],"value":0.2}}

"PV production will drop to about 20% between 13:00 and 15:00"
-> {{"directive_type":"solar_reduction","hours":[13,14],"value":0.2}}

"Panel washing from one until three will leave roughly one-fifth
of normal solar output"
-> {{"directive_type":"solar_reduction","hours":[13,14],"value":0.2}}

"Expect an 80% reduction in rooftop solar during the 1-3 PM
maintenance window"
-> {{"directive_type":"solar_reduction","hours":[13,14],"value":0.2}}

Important:
- "drop TO 20%" means factor = 0.2
- "leave one-fifth" means factor = 0.2
- "80% reduction" means factor = 0.2
- Always return factor as a decimal from 0 to 1.

3. MINIMUM BATTERY RESERVE

If the note requires the battery to keep at least a specified amount of energy:

directive_type = "minimum_battery_reserve"

hours = affected hourly slots

value = minimum energy in kWh

Example:

"Keep at least 120 kWh in reserve from 6 PM until 9 PM"

must produce:

{{
    "directive_type": "minimum_battery_reserve",
    "hours": [18, 19, 20],
    "value": 120
}}

4. NO CHARGE WINDOW

If the note says not to charge the battery during a time window:

directive_type = "no_charge_window"

hours = affected hourly slots

value = null

Example:

"Do not charge the battery between 2 PM and 4 PM"

must produce:

{{
    "directive_type": "no_charge_window",
    "hours": [14, 15],
    "value": null
}}

5. NO DISCHARGE WINDOW

If the note says not to discharge the battery during a time window:

directive_type = "no_discharge_window"

hours = affected hourly slots

value = null

Example:

"Do not discharge the battery between midnight and 4 AM"

must produce:

{{
    "directive_type": "no_discharge_window",
    "hours": [0, 1, 2, 3],
    "value": null
}}

6. MAXIMUM GRID IMPORT

If the note limits grid import to a maximum amount:

directive_type = "max_grid_window"

hours = affected hourly slots

value = maximum grid import in kWh

Example:

"Grid import must stay below 80 kWh from 5 PM to 8 PM"

must produce:

{{
    "directive_type": "max_grid_window",
    "hours": [17, 18, 19],
    "value": 80
}}

7. NO-OP

If the note does not affect:

- solar generation
- battery charging
- battery discharging
- battery reserve
- grid import
- energy scheduling

then classify it as no_op.

For no_op:

directive_type = "no_op"
hours = []
value = null

Example:

"The cafeteria menu changes tomorrow"

must produce:

{{
    "directive_type": "no_op",
    "hours": [],
    "value": null
}}

Operator note:

{note}
"""

    response = model.generate_content(prompt)

    text = response.text.strip()

    text = text.replace("```json", "")
    text = text.replace("```", "")
    text = text.strip()

    return json.loads(text)