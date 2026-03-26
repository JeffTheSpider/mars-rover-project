"""
Assembly Diagnostic — Check part positions and find overlaps.
Reports world-space bounding boxes and identifies clipping parts.
"""
import sys
sys.path.insert(0, r'D:\Mars Rover Project\cad\scripts')
from assembly_trimesh import build_parts_list, load_stl, STL_ROOT
import trimesh
import numpy as np
import os

def get_world_bounds(mesh, transform):
    """Get bounding box in world space after applying transform."""
    transformed = mesh.copy().apply_transform(transform)
    return transformed.bounds  # [[min_x,min_y,min_z],[max_x,max_y,max_z]]

def boxes_overlap(b1, b2):
    """Check if two axis-aligned bounding boxes overlap."""
    for i in range(3):
        if b1[1][i] <= b2[0][i] or b2[1][i] <= b1[0][i]:
            return False
    return True

def overlap_volume(b1, b2):
    """Calculate overlap volume between two AABBs."""
    overlap = 1.0
    for i in range(3):
        lo = max(b1[0][i], b2[0][i])
        hi = min(b1[1][i], b2[1][i])
        if hi <= lo:
            return 0.0
        overlap *= (hi - lo)
    return overlap

def main():
    parts = build_parts_list()

    print("=" * 80)
    print("ASSEMBLY DIAGNOSTIC — World-Space Bounding Boxes")
    print("=" * 80)

    world_bounds = {}

    for subpath, name, colour_key, transform in parts:
        mesh = load_stl(subpath)
        if mesh is None:
            continue
        bounds = get_world_bounds(mesh, transform)
        world_bounds[name] = bounds

        mn = bounds[0]
        mx = bounds[1]
        dims = mx - mn
        print(f"{name:30s}  X:[{mn[0]:7.1f}, {mx[0]:7.1f}]  "
              f"Y:[{mn[1]:7.1f}, {mx[1]:7.1f}]  "
              f"Z:[{mn[2]:7.1f}, {mx[2]:7.1f}]  "
              f"({dims[0]:.0f}x{dims[1]:.0f}x{dims[2]:.0f})")

    # ── Check key relationships ──
    print("\n" + "=" * 80)
    print("KEY RELATIONSHIP CHECKS")
    print("=" * 80)

    def check(part_a, part_b, should_touch=True):
        if part_a not in world_bounds or part_b not in world_bounds:
            return
        ba = world_bounds[part_a]
        bb = world_bounds[part_b]
        overlaps = boxes_overlap(ba, bb)
        vol = overlap_volume(ba, bb)

        if should_touch and not overlaps:
            gap = []
            for i, axis in enumerate(['X', 'Y', 'Z']):
                if ba[1][i] < bb[0][i]:
                    gap.append(f"{axis}:{bb[0][i]-ba[1][i]:.1f}mm")
                elif bb[1][i] < ba[0][i]:
                    gap.append(f"{axis}:{ba[0][i]-bb[1][i]:.1f}mm")
            print(f"  GAP: {part_a} <-> {part_b}: {', '.join(gap)}")
        elif not should_touch and overlaps:
            print(f"  CLIP: {part_a} <-> {part_b}: overlap vol {vol:.0f}mm³")
        else:
            status = "OK (touching)" if overlaps else "OK (separated)"
            print(f"  {status}: {part_a} <-> {part_b}")

    print("\n-- Wheels should NOT overlap body --")
    for w in ['Wheel FL', 'Wheel FR', 'Wheel ML', 'Wheel MR', 'Wheel RL', 'Wheel RR']:
        for b in ['Body FL', 'Body FR', 'Body RL', 'Body RR']:
            check(w, b, should_touch=False)

    print("\n-- Steering bracket should touch FW connector --")
    for sfx in ['FL', 'FR', 'RL', 'RR']:
        check(f'Steer Bracket {sfx}', f'FW Conn {sfx}', should_touch=True)

    print("\n-- Knuckle should be below bracket --")
    for sfx in ['FL', 'FR', 'RL', 'RR']:
        if f'Knuckle {sfx}' in world_bounds and f'Steer Bracket {sfx}' in world_bounds:
            k_top = world_bounds[f'Knuckle {sfx}'][1][2]
            b_bot = world_bounds[f'Steer Bracket {sfx}'][0][2]
            print(f"  Knuckle {sfx} top Z={k_top:.1f}, Bracket {sfx} bottom Z={b_bot:.1f}, "
                  f"{'OK' if k_top <= b_bot + 5 else 'OVERLAP'}")

    print("\n-- Rocker hubs should be at body mid-height (Z~120) --")
    for side in ['L', 'R']:
        name = f'Rocker Hub {side}'
        if name in world_bounds:
            mid_z = (world_bounds[name][0][2] + world_bounds[name][1][2]) / 2
            print(f"  {name}: centre Z={mid_z:.1f}mm (target: 120mm)")

    print("\n-- Body quadrants should tile correctly --")
    if 'Body FL' in world_bounds and 'Body RR' in world_bounds:
        fl = world_bounds['Body FL']
        rr = world_bounds['Body RR']
        print(f"  Body FL: X[{fl[0][0]:.1f}, {fl[1][0]:.1f}] Y[{fl[0][1]:.1f}, {fl[1][1]:.1f}]")
        print(f"  Body RR: X[{rr[0][0]:.1f}, {rr[1][0]:.1f}] Y[{rr[0][1]:.1f}, {rr[1][1]:.1f}]")
        total_x = max(fl[1][0], rr[1][0]) - min(fl[0][0], rr[0][0])
        total_y = max(fl[1][1], rr[1][1]) - min(fl[0][1], rr[0][1])
        print(f"  Total body footprint: {total_x:.0f} x {total_y:.0f}mm (target: 261 x 451)")

    # ── Classify ALL overlapping pairs ──
    print("\n" + "=" * 80)
    print("OVERLAP CLASSIFICATION")
    print("=" * 80)

    # Parts that are physically INSIDE the body cavity
    body_parts = {'Body FL', 'Body FR', 'Body RL', 'Body RR'}
    internal_parts = {'Electronics Tray', 'Battery Tray', 'Fuse Holder',
                      'Switch Mount', 'Diff Pivot', 'Diff Link L', 'Diff Link R',
                      'Strain Relief L', 'Strain Relief R'}

    # Parts that physically mate/attach at the same location
    mating_sets = [
        # FW connector + steering sub-assembly (bracket bolts to connector, knuckle hangs below)
        {'FW Conn FL', 'Steer Bracket FL', 'Knuckle FL', 'Servo FL', 'Horn Link FL'},
        {'FW Conn FR', 'Steer Bracket FR', 'Knuckle FR', 'Servo FR', 'Horn Link FR'},
        {'FW Conn RL', 'Steer Bracket RL', 'Knuckle RL', 'Servo RL', 'Horn Link RL'},
        {'FW Conn RR', 'Steer Bracket RR', 'Knuckle RR', 'Servo RR', 'Horn Link RR'},
        # MW connector + fixed mount
        {'MW Conn L', 'Fixed Mount L'},
        {'MW Conn R', 'Fixed Mount R'},
        # Rocker hub + strain relief (at same pivot)
        {'Rocker Hub L', 'Strain Relief L'},
        {'Rocker Hub R', 'Strain Relief R'},
    ]

    def is_body_internal(a, b):
        """One is a body panel, other is inside the body."""
        if a in body_parts and b in internal_parts:
            return True
        if b in body_parts and a in internal_parts:
            return True
        return False

    def is_body_wall_mount(a, b):
        """Part mounts on/through body wall (connectors, clips, suspension)."""
        wall_parts = {'FW Conn FL', 'FW Conn FR', 'FW Conn RL', 'FW Conn RR',
                      'MW Conn L', 'MW Conn R', 'Rocker Hub L', 'Rocker Hub R',
                      'Bogie Pivot L', 'Bogie Pivot R',
                      'Steer Bracket FL', 'Steer Bracket FR', 'Steer Bracket RL', 'Steer Bracket RR',
                      'Knuckle FL', 'Knuckle FR', 'Knuckle RL', 'Knuckle RR',
                      'Servo FL', 'Servo FR', 'Servo RL', 'Servo RR',
                      'Fixed Mount L', 'Fixed Mount R',
                      'Clip L1', 'Clip L2', 'Clip R1', 'Clip R2'}
        if a in body_parts and b in wall_parts:
            return True
        if b in body_parts and a in wall_parts:
            return True
        return False

    def is_mating(a, b):
        """Parts that physically bolt/attach together."""
        for s in mating_sets:
            if a in s and b in s:
                return True
        return False

    def is_internal_internal(a, b):
        """Both parts inside the body."""
        all_internal = internal_parts | {'Electronics Tray', 'Battery Tray', 'Fuse Holder'}
        return a in all_internal and b in all_internal

    names = list(world_bounds.keys())
    categories = {'expected_internal': [], 'expected_wall': [], 'expected_mating': [],
                  'expected_internal_internal': [], 'minor_wheel': [], 'unexpected': []}

    for i in range(len(names)):
        for j in range(i + 1, len(names)):
            vol = overlap_volume(world_bounds[names[i]], world_bounds[names[j]])
            if vol <= 100:
                continue
            a, b = names[i], names[j]
            if is_body_internal(a, b):
                categories['expected_internal'].append((a, b, vol))
            elif is_body_wall_mount(a, b):
                categories['expected_wall'].append((a, b, vol))
            elif is_mating(a, b):
                categories['expected_mating'].append((a, b, vol))
            elif is_internal_internal(a, b):
                categories['expected_internal_internal'].append((a, b, vol))
            elif 'Wheel' in a or 'Wheel' in b:
                categories['minor_wheel'].append((a, b, vol))
            else:
                categories['unexpected'].append((a, b, vol))

    expected_total = (len(categories['expected_internal']) + len(categories['expected_wall'])
                      + len(categories['expected_mating']) + len(categories['expected_internal_internal']))
    print(f"\n  Expected overlaps (parts inside body, mating, wall-mount): {expected_total}")
    print(f"    - Internal parts inside body cavity: {len(categories['expected_internal'])}")
    print(f"    - Parts mounting on/through body wall: {len(categories['expected_wall'])}")
    print(f"    - Mating/bolted-together parts: {len(categories['expected_mating'])}")
    print(f"    - Internal-to-internal: {len(categories['expected_internal_internal'])}")

    print(f"\n  Minor wheel overlaps (tiny, <6mm): {len(categories['minor_wheel'])}")
    for a, b, vol in categories['minor_wheel']:
        print(f"    {a:25s} <-> {b:25s}  vol={vol:,.0f}mm³")

    print(f"\n  UNEXPECTED overlaps: {len(categories['unexpected'])}")
    if categories['unexpected']:
        for a, b, vol in categories['unexpected']:
            print(f"    *** {a:25s} <-> {b:25s}  vol={vol:,.0f}mm³")
    else:
        print("    None! All overlaps are expected assembly contacts.")

    total = sum(len(v) for v in categories.values())
    print(f"\n  TOTAL: {total} overlapping pairs ({expected_total} expected, "
          f"{len(categories['minor_wheel'])} minor, {len(categories['unexpected'])} unexpected)")

if __name__ == '__main__':
    main()
