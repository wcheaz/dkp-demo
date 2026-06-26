# Pricing Formula Reference

Worked examples for the deterministic pricing calculation using the calibrated
Pamir coefficients (C24 timber @ 6200 CZK/m³, ABR90 angle brackets @ 370 CZK,
and updated gusset/assembly/hanger costs).

## Formula

```
Input: floor_plan_dimensions (e.g. "10x15m"), roof_type, roof_pitch

1. Parse dimensions: width=10, height=15
2. floor_area = 10 * 15 = 150
3. total_joints   = round(150 * 1.32) = 198
4. timber_volume  = 150 * 0.254      = 38.1
5. total_trusses  = round(150 * 0.147) = 22
6. support_nodes  = total_trusses * 2  = 44
7. bracket_count  = round(support_nodes * 1.6) = round(70.4) = 70

8. CZK costs:
   gusset_plates = 198 * 50       = 9,900
   timber        = 38.1 * 6200    = 236,220
   assembly      = (22/20) * 18000 = 19,800
   hangers       = 22 * 120       = 2,640
   metalwork     = 70 * 370       = 25,900

9. Roof type factor (default 1.0):
   Gable = 1.0, Hip = 1.3, Mono-pitch = 0.9, Flat = 0.8

10. total_czk = (9900 + 236220 + 19800 + 2640 + 25900) * factor
              = 294,460 * factor

11. For Gable (factor=1.0): total_eur = round(294460 / 25) = 11,778

12. Output: "Estimated price: €11778 (excl. VAT)"
```

## Example: 8x12m Hip roof

```
floor_area = 96
total_joints   = round(96 * 1.32) = 127
timber_volume  = 96 * 0.254      = 24.384
total_trusses  = round(96 * 0.147) = 14
support_nodes  = 14 * 2  = 28
bracket_count  = round(28 * 1.6) = round(44.8) = 45

gusset_plates = 127 * 50       = 6,350
timber        = 24.384 * 6200  = 151,180.8
assembly      = (14/20) * 18000 = 12,600
hangers       = 14 * 120       = 1,680
metalwork     = 45 * 370       = 16,650

subtotal = 6350 + 151180.8 + 12600 + 1680 + 16650 = 188,460.8
total_czk = 188460.8 * 1.3 = 244,999.04
total_eur = round(244999.04 / 25) = 9,800

Output: "Estimated price: €9800 (excl. VAT)"
```

## Missing dimensions

If `floor_plan_dimensions` was not extracted, the output must ask for dimensions
in the current locale:

**English (locale `en`):**
```
To generate a price estimate, I need the floor plan dimensions.
Please provide the dimensions (e.g. 10x15m).
```

**Slovak (locale `sk`):**
```
Na výpočet odhadu ceny potrebujem rozmery pôdorysu.
Prosím, zadajte rozmery (napr. 10x15m).
```
