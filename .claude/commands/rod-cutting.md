---
description: Calculate 8mm steel rod cutting plan from parametric dimensions
---

# Rod Cutting Plan Calculator

Calculate the optimal cutting plan for 8mm steel rods from `generate_rover_params.py`.

## Steps

1. **Load params**: Run `python cad/scripts/generate_rover_params.py` or read the file to get Phase 1 (0.4x) values:
   - `differential_bar.bar_half_span` × 2 = diff bar total length
   - Rocker front tube: from EA-25 arm lengths (150mm × 2 = 300mm)
   - Rocker rear tube: 60mm × 2 = 120mm
   - Bogie front tube: 60mm × 2 = 120mm
   - Bogie rear tube: 60mm × 2 = 120mm

2. **Calculate total**: Sum all rod lengths + 5mm per cut (hacksaw kerf waste)

3. **Optimize cutting from 1m rods**:
   - Use a greedy bin-packing: longest pieces first, fill remaining space with shorter pieces
   - Report how many 1m rods are needed
   - Show a visual cutting diagram

4. **Cross-check** against shopping list (`docs/plans/phase1-shopping-list.md`) rod quantity

5. **Report**:
   ```
   ROD CUTTING PLAN (Phase 1, 0.4x scale)
   ========================================
   Rod 1 (1000mm): [400mm diff bar] + [150mm rocker front L] + [150mm rocker front R] + [60mm rocker rear L] + ...
   Rod 2 (1000mm): [remaining pieces] + [waste: Xmm]

   Total rods needed: X
   Total waste: Xmm (X%)
   Shopping list says: X rods — [MATCH/MISMATCH]
   ```
