# Pricing Formula Reference

Worked examples for the deterministic pricing calculation.

## Formula

```
Input: floor_plan_dimensions (e.g. "10x15m"), roof_type, roof_pitch

1. Parse dimensions: width=10, height=15
2. floor_area = 10 * 15 = 150
3. total_joints = round(150 * 1.32) = 198
4. timber_volume = 150 * 0.254 = 38.1
5. total_trusses = round(150 * 0.147) = 22

6. CZK costs:
   gusset_plates = 198 * 40    = 7,920
   timber        = 38.1 * 4500 = 171,450
   assembly      = (22/20) * 15000 = 16,500
   hangers       = 22 * 100    = 2,200

7. Roof type factor (default 1.0):
   Gable = 1.0, Hip = 1.3, Mono-pitch = 0.9, Flat = 0.8

8. total_czk = (7920 + 171450 + 16500 + 2200) * factor
             = 198,070 * factor

9. For Gable (factor=1.0): total_gbp = round(198070 / 30) = 6,602

10. Output: "Estimated price: £6,602 (excl. VAT)"
```

## Example: 8x12m Hip roof

```
floor_area = 96
total_joints = round(96 * 1.32) = 127
timber_volume = 96 * 0.254 = 24.384
total_trusses = round(96 * 0.147) = 14

gusset_plates = 127 * 40 = 5,080
timber = 24.384 * 4500 = 109,728
assembly = (14/20) * 15000 = 10,500
hangers = 14 * 100 = 1,400

total_czk = (5080 + 109728 + 10500 + 1400) * 1.3 = 164,710.4
total_gbp = round(164710.4 / 30) = 5,490

Output: "Estimated price: £5,490 (excl. VAT)"
```

## Missing dimensions

If `floor_plan_dimensions` was not extracted, the output must be:

```
To generate a price estimate, I need the floor plan dimensions.
Please provide the dimensions (e.g. 10x15m).
```
