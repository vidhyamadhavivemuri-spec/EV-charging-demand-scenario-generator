import json
import math
import sys


MODULUS = 2**32
MULTIPLIER = 1664525
INCREMENT = 1013904223

REQUIRED_FIELDS = {"seed", "count"}
ALLOWED_FIELDS = {"seed", "count"}


def lcg_next(state):
    """Generate the next 32-bit LCG state."""
    return (MULTIPLIER * state + INCREMENT) % MODULUS


def state_to_uniform(state):
    """Convert a 32-bit state to a uniform value in [0, 1)."""
    return state / MODULUS


def generate_vehicle(state):
    """Generate one vehicle's arrival bucket and energy."""

    # First draw: arrival bucket
    state = lcg_next(state)
    arrival_u = state_to_uniform(state)
    arrival = int(arrival_u * 4)

    # Second draw: energy
    state = lcg_next(state)
    energy_u = state_to_uniform(state)
    energy_kwh = 1 + int(energy_u * 5)

    return state, arrival, energy_kwh


def generate_scenario(seed, count):
    """Generate a complete EV charging demand scenario."""

    state = seed
    arrivals = []
    energy_kwh = []

    for _ in range(count):
        state, arrival, energy = generate_vehicle(state)

        arrivals.append(arrival)
        energy_kwh.append(energy)

    total_kwh = sum(energy_kwh)

    return arrivals, energy_kwh, total_kwh


def invalid_result(reason, **details):
    """Create a standard invalid-result response."""
    result = {
        "status": "invalid",
        "reason": reason
    }

    result.update(details)

    return result


def validate_input(data):
    """Validate the input according to the project contract."""

    if not isinstance(data, dict):
        return invalid_result(
            "invalid_input",
            message="Input must be a JSON object."
        )

    # Check missing required fields.
    missing = sorted(REQUIRED_FIELDS - data.keys())

    if missing:
        return invalid_result(
            "missing_required_field",
            fields=missing
        )

    # Check unknown fields.
    unknown = sorted(set(data.keys()) - ALLOWED_FIELDS)

    if unknown:
        return invalid_result(
            "unknown_field",
            fields=unknown
        )

    seed = data["seed"]
    count = data["count"]

    # Reject booleans because bool is a subclass of int in Python.
    if isinstance(seed, bool) or not isinstance(seed, int):
        return invalid_result(
            "invalid_seed",
            message="seed must be an integer from 0 to 4294967295."
        )

    if isinstance(count, bool) or not isinstance(count, int):
        return invalid_result(
            "invalid_count",
            message="count must be an integer from 0 to 25."
        )

    # Nonfinite check for numeric values.
    if isinstance(seed, float) and not math.isfinite(seed):
        return invalid_result(
            "invalid_seed",
            message="seed must be finite."
        )

    if isinstance(count, float) and not math.isfinite(count):
        return invalid_result(
            "invalid_count",
            message="count must be finite."
        )

    # Range checks.
    if not 0 <= seed <= MODULUS - 1:
        return invalid_result(
            "invalid_seed",
            message="seed must be between 0 and 4294967295."
        )

    if not 1 <= count <= 25:
        return invalid_result(
            "invalid_count",
            message="count must be between 1 and 25."
        )

    return None


def main():
    """Read input JSON and print the result."""

    if len(sys.argv) != 2:
        print("Usage: python src/scenario_generator.py <input.json>")
        sys.exit(1)

    input_file = sys.argv[1]

    try:
        with open(input_file, "r", encoding="utf-8") as file:
            data = json.load(file)

    except FileNotFoundError:
        print(json.dumps(
            invalid_result(
                "file_not_found",
                message=f"Input file not found: {input_file}"
            ),
            indent=2
        ))
        sys.exit(1)

    except json.JSONDecodeError:
        print(json.dumps(
            invalid_result(
                "invalid_json",
                message="Input file does not contain valid JSON."
            ),
            indent=2
        ))
        sys.exit(1)

    validation_error = validate_input(data)

    if validation_error is not None:
        print(json.dumps(validation_error, indent=2))
        sys.exit(1)

    seed = data["seed"]
    count = data["count"]

    arrivals, energy_kwh, total_kwh = generate_scenario(seed, count)

    result = {
        "input": {
            "seed": seed,
            "count": count
        },
        "output": {
            "arrivals": arrivals,
            "energy_kWh": energy_kwh,
            "total_kWh": total_kwh
        },
        "explanation": (
            "Scenario generated using the specified deterministic LCG. "
            "Identical seed/count reproduces the same result."
        )
    }

    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()