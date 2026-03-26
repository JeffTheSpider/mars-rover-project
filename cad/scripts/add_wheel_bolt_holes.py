"""
Add M3 Bolt Holes to V5 Curiosity Wheel Hub
=============================================

Modifies the V5 wheel STL files to add 4× M3 clearance holes through
the hub back face, enabling bolt-on mounting to parametric connectors.

Design Decisions (see docs/engineering/bolt-on-wheel-mounting-design.md):
  - 4× M3 clearance holes (3.2mm diameter)
  - 20mm BCD (bolt circle diameter) -> bolt centres at R=10mm
  - Positions: 0°, 90°, 180°, 270° (aligned with X/Y axes)
  - Through-holes spanning the full hub face thickness

Clearance Analysis:
  - Hub bore: 8.2mm (R=4.1mm) -> inner clearance to bolt: 10-1.6-4.1 = 4.3mm OK
  - Hub face OD: ~28mm (R=14mm) -> outer clearance: 14-10-1.6 = 2.4mm OK
  - Spoke roots at ~12mm radius -> no spoke collision at R=10mm OK

Input:  3d-print/wheels/CuriosityV5_Complete.stl
        3d-print/wheels/CuriosityV5_HubSpokes.stl
Output: Same files (overwritten) + backups saved as *_pre_boltholes.stl

Reference: EA-25, EA-30
"""

import numpy as np
import manifold3d
import trimesh
import os
import shutil

# ── Configuration ──
PROJECT_ROOT = r"D:\Mars Rover Project"
WHEEL_DIR = os.path.join(PROJECT_ROOT, "3d-print", "wheels")

# Bolt pattern parameters (mm)
M3_CLEARANCE_DIA = 3.2      # M3 clearance hole diameter
BCD = 20.0                   # Bolt circle diameter
BOLT_RADIUS = BCD / 2        # 10mm from centre
NUM_BOLTS = 4
BOLT_ANGLES_DEG = [0, 90, 180, 270]  # Aligned with X/Y axes

# Wheel geometry (from STL analysis)
HUB_BACK_Z = -6.0            # Start well behind hub (extra margin)
HOLE_LENGTH = 15.0            # Generous length to ensure clean through-cut
CYLINDER_SEGMENTS = 32        # Facet count for bolt hole cylinders


def trimesh_to_manifold(mesh):
    """Convert a trimesh mesh to a manifold3d Manifold object."""
    verts = np.array(mesh.vertices, dtype=np.float32)
    faces = np.array(mesh.faces, dtype=np.uint32)
    m3d_mesh = manifold3d.Mesh(vert_properties=verts, tri_verts=faces)
    return manifold3d.Manifold(m3d_mesh)


def manifold_to_trimesh(manifold_obj):
    """Convert a manifold3d Manifold back to a trimesh mesh."""
    m3d_mesh = manifold_obj.to_mesh()
    verts = np.array(m3d_mesh.vert_properties[:, :3], dtype=np.float64)
    faces = np.array(m3d_mesh.tri_verts, dtype=np.int64)
    return trimesh.Trimesh(vertices=verts, faces=faces)


def create_bolt_hole_cylinder(x, y, z_start, length, radius, segments=32):
    """Create a cylinder mesh for boolean subtraction.

    The cylinder is oriented along the Z axis (wheel rotation axis).
    """
    cyl = manifold3d.Manifold.cylinder(
        height=length,
        radius_low=radius,
        radius_high=radius,
        circular_segments=segments,
    )
    # Translate to position: cylinder starts at z_start
    cyl = cyl.translate([x, y, z_start])
    return cyl


def add_bolt_holes(input_path, output_path, backup=True):
    """Add 4× M3 bolt holes to a wheel STL file.

    Args:
        input_path: Path to input STL file
        output_path: Path to output STL file
        backup: Whether to create a backup of the original

    Returns:
        dict with results and diagnostics
    """
    print(f"\n{'='*60}")
    print(f"Processing: {os.path.basename(input_path)}")
    print(f"{'='*60}")

    # Load original mesh
    mesh = trimesh.load(input_path)
    print(f"  Original: {len(mesh.vertices)} verts, {len(mesh.faces)} faces")
    print(f"  Bounds: {mesh.bounds}")
    print(f"  Watertight: {mesh.is_watertight}")

    # Backup original
    if backup:
        backup_path = input_path.replace('.stl', '_pre_boltholes.stl')
        if not os.path.exists(backup_path):
            shutil.copy2(input_path, backup_path)
            print(f"  Backup: {os.path.basename(backup_path)}")

    # Convert to manifold
    print("  Converting to manifold3d...")
    wheel_manifold = trimesh_to_manifold(mesh)
    status = wheel_manifold.status()
    print(f"  Manifold status: {status}")
    print(f"  Manifold verts: {wheel_manifold.num_vert()}, tris: {wheel_manifold.num_tri()}")

    # Determine hub face Z position from mesh geometry
    # Hub back face is on the negative Z side
    center_verts = mesh.vertices[np.linalg.norm(mesh.vertices[:, [0, 1]], axis=1) < 5]
    hub_z_min = center_verts[:, 2].min() if len(center_verts) > 0 else -5.0
    hub_z_max = center_verts[:, 2].max() if len(center_verts) > 0 else 0.0
    print(f"  Hub Z range: {hub_z_min:.2f} to {hub_z_max:.2f}mm")

    # Create bolt hole cylinders
    bolt_radius = M3_CLEARANCE_DIA / 2  # 1.6mm
    z_start = hub_z_min - 2.0  # Start 2mm before hub back face
    hole_length = (hub_z_max - hub_z_min) + 4.0  # Full hub depth + 4mm margin

    print(f"\n  Bolt pattern:")
    print(f"    BCD: {BCD}mm, Bolt hole dia: {M3_CLEARANCE_DIA}mm")
    print(f"    Hole Z: {z_start:.1f} to {z_start + hole_length:.1f}mm")

    # Create union of all 4 bolt hole cylinders
    holes = None
    for i, angle_deg in enumerate(BOLT_ANGLES_DEG):
        angle_rad = np.radians(angle_deg)
        x = BOLT_RADIUS * np.cos(angle_rad)
        y = BOLT_RADIUS * np.sin(angle_rad)

        cyl = create_bolt_hole_cylinder(
            x, y, z_start, hole_length, bolt_radius, CYLINDER_SEGMENTS
        )
        print(f"    Hole {i+1}: ({x:+.1f}, {y:+.1f})mm @ {angle_deg}°")

        if holes is None:
            holes = cyl
        else:
            holes = holes + cyl  # Union of cylinders

    # Perform boolean subtraction: wheel - holes
    print("\n  Performing boolean subtraction...")
    result_manifold = wheel_manifold - holes

    # Convert back to trimesh
    result_mesh = manifold_to_trimesh(result_manifold)
    print(f"  Result: {len(result_mesh.vertices)} verts, {len(result_mesh.faces)} faces")

    # Verify bolt holes exist by checking vertices near bolt positions
    diagnostics = {'holes_found': 0, 'hole_details': []}
    for i, angle_deg in enumerate(BOLT_ANGLES_DEG):
        angle_rad = np.radians(angle_deg)
        x = BOLT_RADIUS * np.cos(angle_rad)
        y = BOLT_RADIUS * np.sin(angle_rad)

        # Check for vertices forming the bolt hole
        dists = np.linalg.norm(
            result_mesh.vertices[:, [0, 1]] - np.array([x, y]),
            axis=1
        )
        hole_verts = result_mesh.vertices[dists < bolt_radius + 0.5]
        if len(hole_verts) > 0:
            diagnostics['holes_found'] += 1
            diagnostics['hole_details'].append({
                'angle': angle_deg,
                'x': float(x), 'y': float(y),
                'verts_near_hole': len(hole_verts),
                'z_range': [float(hole_verts[:, 2].min()),
                           float(hole_verts[:, 2].max())]
            })

    print(f"\n  Verification: {diagnostics['holes_found']}/4 bolt holes detected")
    for d in diagnostics['hole_details']:
        print(f"    {d['angle']}°: {d['verts_near_hole']} verts, "
              f"Z=[{d['z_range'][0]:.1f}, {d['z_range'][1]:.1f}]")

    # Collision check: verify bolt holes don't intersect spokes
    # Spoke roots are at ~12mm radius — our bolts at 10mm with 1.6mm radius
    # means bolt edge at 11.6mm which is < 12mm spoke root. Check anyway.
    spoke_zone = result_mesh.vertices[
        (np.linalg.norm(result_mesh.vertices[:, [0, 1]], axis=1) > 11.0) &
        (np.linalg.norm(result_mesh.vertices[:, [0, 1]], axis=1) < 13.0) &
        (result_mesh.vertices[:, 2] < hub_z_max + 1.0)
    ]
    if len(spoke_zone) > 0:
        print(f"  Spoke clearance check: {len(spoke_zone)} verts in 11-13mm radius band")
    else:
        print(f"  Spoke clearance check: Clear (no geometry in 11-13mm band)")

    # Export
    result_mesh.export(output_path)
    file_size_kb = os.path.getsize(output_path) / 1024
    print(f"\n  Exported: {os.path.basename(output_path)} ({file_size_kb:.0f} KB)")

    diagnostics['input_faces'] = len(mesh.faces)
    diagnostics['output_faces'] = len(result_mesh.faces)
    diagnostics['file_size_kb'] = file_size_kb

    return diagnostics


def main():
    print("=" * 60)
    print("V5 Curiosity Wheel — Bolt Hole Addition")
    print("=" * 60)
    print(f"Pattern: {NUM_BOLTS}× M3 ({M3_CLEARANCE_DIA}mm) on {BCD}mm BCD")
    print(f"Angles: {BOLT_ANGLES_DEG}")

    files = [
        ("CuriosityV5_Complete.stl", "Full wheel (for printing)"),
        ("CuriosityV5_HubSpokes.stl", "Hub+spokes only (for assembly viz)"),
    ]

    all_results = {}
    for filename, desc in files:
        input_path = os.path.join(WHEEL_DIR, filename)
        if not os.path.exists(input_path):
            print(f"\n  SKIP: {filename} not found")
            continue

        result = add_bolt_holes(input_path, input_path, backup=True)
        all_results[filename] = result

    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    for filename, result in all_results.items():
        print(f"  {filename}:")
        print(f"    Holes: {result['holes_found']}/4 verified")
        print(f"    Faces: {result['input_faces']} -> {result['output_faces']}")
        print(f"    Size: {result['file_size_kb']:.0f} KB")

    total_holes = sum(r['holes_found'] for r in all_results.values())
    total_expected = len(all_results) * 4
    if total_holes == total_expected:
        print(f"\n  OK All {total_expected} bolt holes verified successfully")
    else:
        print(f"\n  ✗ WARNING: Only {total_holes}/{total_expected} holes verified")

    return all_results


if __name__ == "__main__":
    main()
