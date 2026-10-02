# Approach and Assumptions

## 1. Goal

The goal of this project is to generate small, reproducible EV charging-demand scenarios using the fixed rules provided in the project brief.

The program takes a seed and a vehicle count as input and generates an arrival bucket and charging energy value for each vehicle.

The generated data is fictional and is intended only for simulation and learning.

---

## 2. Approach

I implemented the scenario generator in Python using only the standard library.

The program follows the specified Linear Congruential Generator (LCG):

```text
state = (1664525 × state + 1013904223) modulo 2^32
```

After each state update, the value is converted to a uniform value between 0 and 1:

```text
uniform = state / 2^32
```

For every vehicle, two LCG values are generated.

The first value determines the arrival bucket:

```text
arrival = floor(uniform × 4)
```

which gives a value from `0` to `3`.

The second value determines the energy demand:

```text
energy = 1 + floor(uniform × 5)
```

which gives a value from `1` to `5 kWh`.

The total demand is calculated by summing the generated energy values.

---

## 3. Determinism

The generator is deterministic, meaning that the same seed and vehicle count always produce the same result.

This was important because the project requires scenarios to be reproducible.

For example, with:

```text
seed = 0
count = 1
```

the first two LCG states produce:

```text
arrival = 0
energy = 2 kWh
```

Running the same input again produces the same values.

---

## 4. Input Validation

The program validates the JSON input before generating a scenario.

The required fields are:

```text
seed
count
```

Unknown fields are rejected instead of being ignored.

The following limits are enforced:

* `seed`: 0 to 4294967295
* `count`: 1 to 25

A count of zero is rejected because it would produce an empty dataset, and the project rules state that empty datasets are invalid unless specifically permitted.

Invalid input returns a structured JSON response containing the reason for rejection.

---

## 5. Testing

The project uses Python's built-in `unittest` framework.

The tests check:

* the supplied worked example
* reproducibility with the same seed
* arrival values staying between 0 and 3
* energy values staying between 1 and 5
* missing required fields
* unknown fields
* invalid seed values
* invalid count values
* rejection of zero vehicle count

The current test suite contains **9 tests**, and all 9 pass.

---

## 6. Assumptions

The following assumptions were made while implementing the project:

1. Arrival buckets `0` to `3` are treated as fictional categories rather than real clock times.
2. Energy values are measured in kWh and are restricted to the specified range of 1 to 5 kWh.
3. The input contains only the required `seed` and `count` fields.
4. A separate target or expected demand total is not added because it is not part of the supplied input format.
5. The calculated `total_kWh` is the sum of the generated per-vehicle energy values.
6. Python's standard library is sufficient for the project, so no external dependencies are required.

---

## 7. Limitations

This project is a deterministic scenario generator rather than a real EV charging-demand forecasting system.

It does not use real-world charging data, live services, machine learning, or physical charging hardware.

The generated scenarios should therefore not be interpreted as predictions of actual EV charging behavior.

The main purpose of the project is to demonstrate deterministic generation, bounded sampling, JSON input/output, validation, and automated testing.
