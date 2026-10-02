import unittest

from src.scenario_generator import (
    generate_scenario,
    validate_input,
)


class TestScenarioGenerator(unittest.TestCase):

    def test_worked_example(self):
        arrivals, energy, total = generate_scenario(0, 1)

        self.assertEqual(arrivals, [0])
        self.assertEqual(energy, [2])
        self.assertEqual(total, 2)

    def test_reproducibility(self):
        result1 = generate_scenario(12345, 10)
        result2 = generate_scenario(12345, 10)

        self.assertEqual(result1, result2)

    def test_energy_is_bounded(self):
        arrivals, energy, total = generate_scenario(0, 25)

        for value in energy:
            self.assertGreaterEqual(value, 1)
            self.assertLessEqual(value, 5)

    def test_arrival_is_bounded(self):
        arrivals, energy, total = generate_scenario(0, 25)

        for value in arrivals:
            self.assertGreaterEqual(value, 0)
            self.assertLessEqual(value, 3)

    def test_missing_required_field(self):
        result = validate_input({
            "seed": 0
        })

        self.assertEqual(
            result,
            {
                "status": "invalid",
                "reason": "missing_required_field",
                "fields": ["count"]
            }
        )

    def test_unknown_field(self):
        result = validate_input({
            "seed": 0,
            "count": 1,
            "vehicles": 5
        })

        self.assertEqual(
            result,
            {
                "status": "invalid",
                "reason": "unknown_field",
                "fields": ["vehicles"]
            }
        )

    def test_invalid_seed(self):
        result = validate_input({
            "seed": 4294967296,
            "count": 1
        })

        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["reason"], "invalid_seed")

    def test_invalid_count(self):
        result = validate_input({
            "seed": 0,
            "count": 26
        })

        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["reason"], "invalid_count")

    def test_zero_count_is_invalid(self):
        result = validate_input({
            "seed": 0,
            "count": 0
        })

        self.assertEqual(result["status"], "invalid")
        self.assertEqual(result["reason"], "invalid_count")


if __name__ == "__main__":
    unittest.main()