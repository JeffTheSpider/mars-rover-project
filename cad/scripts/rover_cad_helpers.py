"""
Mars Rover CAD Helpers — Shared Fusion 360 API Utilities
=========================================================

Eliminates code duplication across all rover CAD scripts. Provides
standardised functions for creating bearing seats, tube sockets,
heat-set insert pockets, motor clips, servo pockets, and more.

All dimensions in cm (Fusion 360 API default). Comments show mm.

Usage in Fusion 360 scripts:
    import sys
    sys.path.insert(0, r"D:\\Mars Rover Project\\cad\\scripts")
    from rover_cad_helpers import *

Reference: EA-08, EA-25, EA-26, EA-27
"""

import adsk.core
import adsk.fusion
import math


# ═══════════════════════════════════════════════════════════════════
# Constants (cm — Fusion API units, mm values in comments)
# ═══════════════════════════════════════════════════════════════════

# 608ZZ bearing
BEARING_OD = 2.215          # 22.15mm (22mm + 0.15mm press-fit oversize)
BEARING_DEPTH = 0.72        # 7.2mm (7mm + 0.2mm clearance)
BEARING_BORE = 0.81         # 8.1mm through-hole (8mm + 0.1mm clearance)

# 8mm tube socket
TUBE_BORE = 0.82            # 8.2mm (8mm + 0.2mm slide-fit)
TUBE_DEPTH = 1.5            # 15mm engagement
TUBE_WALL = 0.4             # 4mm minimum wall

# M3 heat-set insert
INSERT_BORE = 0.48          # 4.8mm hole
INSERT_DEPTH = 0.55         # 5.5mm pocket depth
INSERT_CHAMFER = 0.05       # 0.5mm entry chamfer

# M3 grub screw
GRUB_M3 = 0.15              # 1.5mm radius (3mm dia)

# M2 clearance hole
M2_CLEAR = 0.11             # 1.1mm radius (2.2mm dia)

# N20 motor clip
N20_W = 1.22                # 12.2mm inner width
N20_H = 1.02                # 10.2mm inner height
N20_D = 2.5                 # 25mm pocket depth
N20_WALL = 0.2              # 2mm clip wall
N20_SHAFT_EXIT = 0.2        # 2mm radius (4mm shaft hole)

# SG90 servo pocket
SG90_W = 2.24               # 22.4mm (22.2 + 0.2mm clearance)
SG90_D = 1.22               # 12.2mm (11.8 + 0.4mm clearance)
SG90_POCKET_DEPTH = 1.2     # 12mm pocket depth
SG90_TAB_W = 3.24           # 32.4mm total tab width
SG90_TAB_H = 0.25           # 2.5mm tab thickness

# Standard fillet/chamfer
FILLET_STD = 0.05           # 0.5mm (PLA-safe external fillet)
FILLET_LARGE = 0.2          # 2mm (corner rounding)
CHAMFER_STD = 0.03          # 0.3mm (bearing/insert entry)
CORNER_R = 0.2              # 2mm rounded rectangle corner radius


# ═══════════════════════════════════════════════════════════════════
# Shorthand helpers
# ═══════════════════════════════════════════════════════════════════

def p(x, y, z=0):
    """Create a Point3D (cm)."""
    return adsk.core.Point3D.create(x, y, z)


def val(v):
    """Create a ValueInput from a real number (cm)."""
    return adsk.core.ValueInput.createByReal(v)


# ═══════════════════════════════════════════════════════════════════
# Profile selection
# ═══════════════════════════════════════════════════════════════════

def find_profile_by_area(sketch, target_area, tolerance=0.5):
    """Find the sketch profile closest to target_area (cm^2).

    Args:
        sketch: The Fusion 360 sketch object.
        target_area: Expected area in cm^2.
        tolerance: Max fractional deviation (0.5 = 50%).

    Returns:
        The best-matching profile, or None.
    """
    best = None
    best_diff = float('inf')
    for i in range(sketch.profiles.count):
        pr = sketch.profiles.item(i)
        a = pr.areaProperties().area
        diff = abs(a - target_area)
        if diff < best_diff and diff < target_area * tolerance:
            best_diff = diff
            best = pr
    return best


def find_smallest_profile(sketch, max_area=None):
    """Find the smallest profile in a sketch (useful for bore holes).

    Args:
        sketch: The Fusion 360 sketch object.
        max_area: Optional upper bound in cm^2.

    Returns:
        The smallest profile, or None.
    """
    best = None
    best_area = float('inf')
    for i in range(sketch.profiles.count):
        pr = sketch.profiles.item(i)
        a = pr.areaProperties().area
        if a < best_area:
            if max_area is None or a < max_area:
                best_area = a
                best = pr
    return best


def find_largest_profile(sketch, min_area=None):
    """Find the largest profile in a sketch."""
    best = None
    best_area = 0
    for i in range(sketch.profiles.count):
        pr = sketch.profiles.item(i)
        a = pr.areaProperties().area
        if a > best_area:
            if min_area is None or a > min_area:
                best_area = a
                best = pr
    return best


# ═══════════════════════════════════════════════════════════════════
# Sketch primitives
# ═══════════════════════════════════════════════════════════════════

def draw_rounded_rect(sketch, cx, cy, w, h, r=None):
    """Draw a rectangle with rounded corners on a sketch.

    Args:
        sketch: The Fusion 360 sketch.
        cx, cy: Centre point (cm).
        w, h: Width and height (cm).
        r: Corner radius (cm). Defaults to CORNER_R (2mm).

    Returns:
        None. The profile is created in the sketch.
    """
    if r is None:
        r = CORNER_R

    # Clamp radius to half the smallest dimension
    r = min(r, w / 2 - 0.001, h / 2 - 0.001)
    if r <= 0.005:
        # Too small for arcs — fall back to plain rectangle
        sketch.sketchCurves.sketchLines.addTwoPointRectangle(
            p(cx - w / 2, cy - h / 2), p(cx + w / 2, cy + h / 2)
        )
        return

    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs

    hw = w / 2
    hh = h / 2

    # Corner centres
    tl = (cx - hw + r, cy + hh - r)
    tr = (cx + hw - r, cy + hh - r)
    br = (cx + hw - r, cy - hh + r)
    bl = (cx - hw + r, cy - hh + r)

    # Straight edges (between arc endpoints)
    # Top edge
    lines.addByTwoPoints(p(tl[0], cy + hh), p(tr[0], cy + hh))
    # Right edge
    lines.addByTwoPoints(p(cx + hw, tr[1]), p(cx + hw, br[1]))
    # Bottom edge
    lines.addByTwoPoints(p(br[0], cy - hh), p(bl[0], cy - hh))
    # Left edge
    lines.addByTwoPoints(p(cx - hw, bl[1]), p(cx - hw, tl[1]))

    # Corner arcs (90 degrees each, connecting the edges)
    half_pi = math.pi / 2
    # Top-left: from left-edge top to top-edge left
    arcs.addByCenterStartSweep(p(*tl), p(cx - hw, tl[1]), -half_pi)
    # Top-right: from top-edge right to right-edge top
    arcs.addByCenterStartSweep(p(*tr), p(tr[0], cy + hh), -half_pi)
    # Bottom-right: from right-edge bottom to bottom-edge right
    arcs.addByCenterStartSweep(p(*br), p(cx + hw, br[1]), -half_pi)
    # Bottom-left: from bottom-edge left to left-edge bottom
    arcs.addByCenterStartSweep(p(*bl), p(bl[0], cy - hh), -half_pi)


def draw_stadium(sketch, cx, cy, half_length, radius):
    """Draw a stadium (capsule) shape — rectangle with semicircle ends.

    Args:
        sketch: The Fusion 360 sketch.
        cx, cy: Centre point (cm).
        half_length: Half the centre-to-centre distance (cm).
        radius: End radius (cm).
    """
    lines = sketch.sketchCurves.sketchLines
    arcs = sketch.sketchCurves.sketchArcs

    # Top line
    lines.addByTwoPoints(p(cx - half_length, cy + radius),
                         p(cx + half_length, cy + radius))
    # Bottom line
    lines.addByTwoPoints(p(cx + half_length, cy - radius),
                         p(cx - half_length, cy - radius))
    # Right semicircle
    arcs.addByCenterStartSweep(p(cx + half_length, cy),
                               p(cx + half_length, cy + radius),
                               -math.pi)
    # Left semicircle
    arcs.addByCenterStartSweep(p(cx - half_length, cy),
                               p(cx - half_length, cy - radius),
                               -math.pi)


# ═══════════════════════════════════════════════════════════════════
# Extrude / Revolve helpers
# ═══════════════════════════════════════════════════════════════════

def extrude_profile(comp, profile, height, operation=None, symmetric=False):
    """Extrude a profile to a given height.

    Args:
        comp: The root component.
        profile: The sketch profile to extrude.
        height: Extrusion distance (cm, positive).
        operation: FeatureOperations enum. Default: NewBody for first, Join otherwise.
        symmetric: If True, extrude symmetrically about the sketch plane.

    Returns:
        The ExtrudeFeature, or None on failure.
    """
    if profile is None:
        return None
    if operation is None:
        operation = adsk.fusion.FeatureOperations.NewBodyFeatureOperation

    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(profile, operation)
    if symmetric:
        ext_input.setSymmetricExtent(val(height / 2), True)
    else:
        ext_input.setDistanceExtent(False, val(height))
    try:
        return extrudes.add(ext_input)
    except Exception as e:
        print(f'  Warning: {e}')
        return None


def cut_profile(comp, profile, depth, flip=False):
    """Cut (subtract) a profile into the existing body.

    Args:
        comp: The root component.
        profile: The sketch profile to cut.
        depth: Cut depth (cm).
        flip: If True, cut direction is reversed.

    Returns:
        The ExtrudeFeature, or None on failure.
    """
    if profile is None:
        return None
    extrudes = comp.features.extrudeFeatures
    ext_input = extrudes.createInput(
        profile, adsk.fusion.FeatureOperations.CutFeatureOperation
    )
    ext_input.setDistanceExtent(flip, val(depth))
    try:
        return extrudes.add(ext_input)
    except Exception as e:
        print(f'  Warning: {e}')
        return None


def join_profile(comp, profile, height):
    """Join (add) an extruded profile to the existing body.

    Args:
        comp: The root component.
        profile: The sketch profile.
        height: Extrusion height (cm).

    Returns:
        The ExtrudeFeature, or None on failure.
    """
    return extrude_profile(
        comp, profile, height,
        adsk.fusion.FeatureOperations.JoinFeatureOperation
    )


def make_offset_plane(comp, base_plane, offset):
    """Create a construction plane offset from base_plane.

    Args:
        comp: The root component.
        base_plane: The reference plane (e.g. comp.xYConstructionPlane).
        offset: Distance in cm.

    Returns:
        The new ConstructionPlane.
    """
    planes = comp.constructionPlanes
    plane_input = planes.createInput()
    plane_input.setByOffset(base_plane, val(offset))
    return planes.add(plane_input)


# ═══════════════════════════════════════════════════════════════════
# Feature builders — 608ZZ bearing seat
# ═══════════════════════════════════════════════════════════════════

def make_bearing_seat(comp, sketch_plane, cx=0, cy=0,
                      od=None, depth=None, bore=None,
                      bore_through=None, chamfer=True):
    """Create a 608ZZ bearing seat (cylindrical pocket + through-bore).

    Creates two cuts on the given sketch plane:
    1. Bearing pocket: 22.15mm dia x 7.2mm deep (from sketch plane inward)
    2. Shaft bore: 8.1mm dia through the full body

    Args:
        comp: Root component.
        sketch_plane: Plane to sketch on (should be the face where bearing enters).
        cx, cy: Centre position on sketch plane (cm).
        od: Bearing seat outer diameter / 2 (cm). Default: BEARING_OD/2.
        depth: Seat depth (cm). Default: BEARING_DEPTH.
        bore: Shaft bore radius (cm). Default: BEARING_BORE/2.
        bore_through: Through-bore distance (cm). Default: same as depth.
        chamfer: If True, add 0.3mm entry chamfer.

    Returns:
        dict with keys 'seat_feature', 'bore_feature', 'chamfer_feature'.
    """
    seat_r = (od or BEARING_OD) / 2
    seat_d = depth or BEARING_DEPTH
    bore_r = (bore or BEARING_BORE) / 2
    through = bore_through or seat_d

    result = {'seat_feature': None, 'bore_feature': None, 'chamfer_feature': None}

    # Bearing pocket
    s1 = comp.sketches.add(sketch_plane)
    s1.name = 'Bearing Seat'
    s1.sketchCurves.sketchCircles.addByCenterRadius(p(cx, cy), seat_r)

    prof = find_smallest_profile(s1)
    result['seat_feature'] = cut_profile(comp, prof, seat_d, flip=True)

    # Shaft through-bore
    s2 = comp.sketches.add(sketch_plane)
    s2.name = 'Shaft Bore'
    s2.sketchCurves.sketchCircles.addByCenterRadius(p(cx, cy), bore_r)

    prof2 = find_smallest_profile(s2)
    result['bore_feature'] = cut_profile(comp, prof2, through, flip=True)

    # Entry chamfer
    if chamfer and result['seat_feature']:
        result['chamfer_feature'] = _chamfer_circular_edge(
            comp, result['seat_feature'], seat_r, CHAMFER_STD
        )

    return result


# ═══════════════════════════════════════════════════════════════════
# Feature builders — tube socket
# ═══════════════════════════════════════════════════════════════════

def make_tube_socket(comp, sketch_plane, cx=0, cy=0,
                     bore=None, depth=None, grub=True,
                     grub_plane=None, grub_cx=0, grub_cy=0,
                     chamfer=True):
    """Create an 8mm tube socket (bore + optional M3 grub screw).

    Args:
        comp: Root component.
        sketch_plane: Plane at the socket opening.
        cx, cy: Centre position on sketch plane (cm).
        bore: Socket bore radius (cm). Default: TUBE_BORE/2.
        depth: Socket depth (cm). Default: TUBE_DEPTH.
        grub: If True, add an M3 grub screw hole.
        grub_plane: Optional plane for the grub screw sketch.
        grub_cx, grub_cy: Grub hole position on grub_plane.
        chamfer: If True, add 0.3mm entry chamfer on bore.

    Returns:
        dict with keys 'bore_feature', 'grub_feature'.
    """
    bore_r = (bore or TUBE_BORE) / 2
    sock_d = depth or TUBE_DEPTH

    result = {'bore_feature': None, 'grub_feature': None}

    # Socket bore
    s1 = comp.sketches.add(sketch_plane)
    s1.name = 'Tube Socket'
    s1.sketchCurves.sketchCircles.addByCenterRadius(p(cx, cy), bore_r)

    prof = find_smallest_profile(s1)
    result['bore_feature'] = cut_profile(comp, prof, sock_d, flip=True)

    # M3 grub screw
    if grub and grub_plane is not None:
        s2 = comp.sketches.add(grub_plane)
        s2.name = 'Tube Grub'
        s2.sketchCurves.sketchCircles.addByCenterRadius(
            p(grub_cx, grub_cy), GRUB_M3
        )
        gprof = find_smallest_profile(s2)
        # FIX M23: Limit grub depth to wall thickness only (not wall + bore_r
        # which could punch through the opposite wall)
        result['grub_feature'] = cut_profile(
            comp, gprof, TUBE_WALL + 0.01, flip=True
        )

    return result


# ═══════════════════════════════════════════════════════════════════
# Feature builders — heat-set insert pocket
# ═══════════════════════════════════════════════════════════════════

def make_heat_set_pocket(comp, sketch_plane, cx=0, cy=0,
                         bore=None, depth=None, chamfer=True):
    """Create an M3 heat-set insert pocket.

    Args:
        comp: Root component.
        sketch_plane: Plane at the insertion face.
        cx, cy: Centre position (cm).
        bore: Pocket bore radius (cm). Default: INSERT_BORE/2.
        depth: Pocket depth (cm). Default: INSERT_DEPTH.
        chamfer: Add entry chamfer.

    Returns:
        The ExtrudeFeature for the pocket, or None.
    """
    bore_r = (bore or INSERT_BORE) / 2
    pocket_d = depth or INSERT_DEPTH

    sk = comp.sketches.add(sketch_plane)
    sk.name = 'Heat-Set Pocket'
    sk.sketchCurves.sketchCircles.addByCenterRadius(p(cx, cy), bore_r)

    prof = find_smallest_profile(sk)
    return cut_profile(comp, prof, pocket_d, flip=True)


def make_heat_set_pair(comp, sketch_plane, spacing, cx=0, cy=0,
                       axis='y', bore=None, depth=None):
    """Create a pair of heat-set insert pockets symmetrically placed.

    Args:
        comp: Root component.
        sketch_plane: Insertion face plane.
        spacing: Centre-to-centre distance (cm).
        cx, cy: Midpoint of the pair (cm).
        axis: 'x' or 'y' — which axis the pair is spread along.
        bore, depth: Override pocket dimensions.

    Returns:
        List of 2 ExtrudeFeatures.
    """
    results = []
    half = spacing / 2
    for sign in [-1, 1]:
        if axis == 'y':
            results.append(make_heat_set_pocket(
                comp, sketch_plane, cx, cy + sign * half, bore, depth
            ))
        else:
            results.append(make_heat_set_pocket(
                comp, sketch_plane, cx + sign * half, cy, bore, depth
            ))
    return results


# ═══════════════════════════════════════════════════════════════════
# Feature builders — N20 motor clip
# ═══════════════════════════════════════════════════════════════════

def make_n20_clip(comp, sketch_plane, cx=0, cy=0,
                  depth=None, shaft_exit_plane=None,
                  shaft_exit_cx=0, shaft_exit_cy=0):
    """Create an N20 motor clip pocket.

    The pocket is a rectangular cut for the motor body (12.2 x 10.2 x 25mm).

    Args:
        comp: Root component.
        sketch_plane: Plane at the pocket opening.
        cx, cy: Centre of the motor pocket on sketch plane (cm).
        depth: Pocket depth (cm). Default: N20_D.
        shaft_exit_plane: Optional plane for shaft exit hole.
        shaft_exit_cx, shaft_exit_cy: Shaft hole position.

    Returns:
        dict with 'pocket_feature' and 'shaft_feature'.
    """
    motor_d = depth or N20_D
    result = {'pocket_feature': None, 'shaft_feature': None}

    sk = comp.sketches.add(sketch_plane)
    sk.name = 'N20 Motor Pocket'
    draw_rounded_rect(sk, cx, cy, N20_W, N20_H, r=0.05)  # 0.5mm corners

    target = N20_W * N20_H
    prof = find_profile_by_area(sk, target, tolerance=0.4)
    result['pocket_feature'] = cut_profile(comp, prof, motor_d, flip=True)

    # Shaft exit hole
    if shaft_exit_plane is not None:
        s2 = comp.sketches.add(shaft_exit_plane)
        s2.name = 'Shaft Exit'
        s2.sketchCurves.sketchCircles.addByCenterRadius(
            p(shaft_exit_cx, shaft_exit_cy), N20_SHAFT_EXIT
        )
        sprof = find_smallest_profile(s2)
        result['shaft_feature'] = cut_profile(comp, sprof, 1.0, flip=True)

    return result


# ═══════════════════════════════════════════════════════════════════
# Feature builders — SG90 servo pocket
# ═══════════════════════════════════════════════════════════════════

def make_sg90_pocket(comp, sketch_plane, cx=0, cy=0,
                     depth=None, tab_slots=True):
    """Create an SG90 servo pocket with optional tab slots.

    Args:
        comp: Root component.
        sketch_plane: Plane at the pocket opening (top face).
        cx, cy: Centre of pocket (cm).
        depth: Pocket depth (cm). Default: SG90_POCKET_DEPTH.
        tab_slots: If True, add wider tab-level slots.

    Returns:
        dict with 'pocket_feature', 'tab_feature'.
    """
    pocket_d = depth or SG90_POCKET_DEPTH
    result = {'pocket_feature': None, 'tab_feature': None}

    # Main servo body pocket
    sk = comp.sketches.add(sketch_plane)
    sk.name = 'SG90 Pocket'
    draw_rounded_rect(sk, cx, cy, SG90_W, SG90_D, r=0.05)

    target = SG90_W * SG90_D
    prof = find_profile_by_area(sk, target, tolerance=0.4)
    result['pocket_feature'] = cut_profile(comp, prof, pocket_d, flip=True)

    # Tab slots (wider rectangle at tab level)
    if tab_slots:
        sk2 = comp.sketches.add(sketch_plane)
        sk2.name = 'Servo Tab Slots'
        draw_rounded_rect(sk2, cx, cy, SG90_TAB_W, SG90_D, r=0.05)

        tab_target = SG90_TAB_W * SG90_D
        tprof = find_profile_by_area(sk2, tab_target, tolerance=0.5)
        if tprof:
            result['tab_feature'] = cut_profile(comp, tprof, SG90_TAB_H, flip=True)

    return result


# ═══════════════════════════════════════════════════════════════════
# Fillet / chamfer helpers
# ═══════════════════════════════════════════════════════════════════

def add_edge_fillets(comp, body, radius=None, skip_circular=True):
    """Add fillets to all external edges of a body.

    Uses try/except per edge — some may fail (tangent edges, etc.).
    Skips circular edges by default (bearing seats, bores).

    Args:
        comp: Root component.
        body: The BRepBody to fillet.
        radius: Fillet radius (cm). Default: FILLET_STD.
        skip_circular: Skip Circle3D edges (bores, seats).

    Returns:
        Number of edges successfully filleted.
    """
    if body is None:
        return 0

    r = radius or FILLET_STD
    count = 0

    # Collect eligible edges
    edges = adsk.core.ObjectCollection.create()
    for i in range(body.edges.count):
        edge = body.edges.item(i)
        if skip_circular:
            geom = edge.geometry
            if isinstance(geom, adsk.core.Circle3D):
                continue
        edges.add(edge)

    if edges.count == 0:
        return 0

    # Try to fillet all at once first (fastest)
    fillets = comp.features.filletFeatures
    try:
        fillet_input = fillets.createInput()
        fillet_input.addConstantRadiusEdgeSet(edges, val(r), True)
        fillets.add(fillet_input)
        return edges.count
    except Exception as e:
        print(f'  Warning: batch fillet failed, falling back to one-at-a-time: {e}')

    # Fall back to one-at-a-time if batch fails
    for i in range(edges.count):
        single = adsk.core.ObjectCollection.create()
        single.add(edges.item(i))
        try:
            fillet_input = fillets.createInput()
            fillet_input.addConstantRadiusEdgeSet(single, val(r), True)
            fillets.add(fillet_input)
            count += 1
        except Exception as e:
            print(f'  Warning: fillet edge {i} skipped: {e}')

    return count


def add_chamfer(comp, body, target_radius, chamfer_size=None):
    """Add a chamfer to circular edges matching target_radius.

    Useful for bearing seat entry chamfers, insert chamfers, etc.

    Args:
        comp: Root component.
        body: The BRepBody to search.
        target_radius: Radius of the circular edge to chamfer (cm).
        chamfer_size: Chamfer distance (cm). Default: CHAMFER_STD.

    Returns:
        The ChamferFeature, or None.
    """
    return _chamfer_circular_edge(comp, None, target_radius,
                                  chamfer_size or CHAMFER_STD, body=body)


def _chamfer_circular_edge(comp, feature, target_radius, size, body=None):
    """Internal: chamfer a circular edge by radius matching.

    Args:
        comp: Root component.
        feature: The feature whose edges to search (or None if body provided).
        target_radius: Expected circle radius (cm).
        size: Chamfer distance (cm).
        body: Optional body to search instead of feature.

    Returns:
        The ChamferFeature, or None.
    """
    edges = adsk.core.ObjectCollection.create()

    search_body = body
    if search_body is None and feature is not None:
        try:
            search_body = feature.bodies.item(0)
        except Exception as e:
            print(f'  Warning: {e}')
            return None

    if search_body is None:
        return None

    for i in range(search_body.edges.count):
        edge = search_body.edges.item(i)
        geom = edge.geometry
        if isinstance(geom, adsk.core.Circle3D):
            if abs(geom.radius - target_radius) < 0.02:
                edges.add(edge)

    if edges.count == 0:
        return None

    chamfers = comp.features.chamferFeatures
    try:
        cham_input = chamfers.createInput2()
        cham_input.chamferEdgeSets.addEqualDistanceChamferEdgeSet(
            edges, val(size), True
        )
        return chamfers.add(cham_input)
    except Exception as e:
        print(f'  Warning: {e}')
        return None


# ═══════════════════════════════════════════════════════════════════
# Reinforcement ribs
# ═══════════════════════════════════════════════════════════════════

def add_triangular_gusset(comp, sketch_plane, x1, y1, x2, y2, x3, y3,
                          height, operation=None):
    """Add a triangular gusset (reinforcement rib).

    Args:
        comp: Root component.
        sketch_plane: Plane to sketch the triangle on.
        x1,y1,x2,y2,x3,y3: Triangle vertices (cm).
        height: Extrusion height (cm).
        operation: Feature operation. Default: JoinFeatureOperation.

    Returns:
        The ExtrudeFeature, or None.
    """
    if operation is None:
        operation = adsk.fusion.FeatureOperations.JoinFeatureOperation

    sk = comp.sketches.add(sketch_plane)
    sk.name = 'Gusset'
    lines = sk.sketchCurves.sketchLines
    lines.addByTwoPoints(p(x1, y1), p(x2, y2))
    lines.addByTwoPoints(p(x2, y2), p(x3, y3))
    lines.addByTwoPoints(p(x3, y3), p(x1, y1))

    expected = abs((x2 - x1) * (y3 - y1) - (x3 - x1) * (y2 - y1)) / 2
    prof = find_profile_by_area(sk, expected, tolerance=0.6)
    return extrude_profile(comp, prof, height, operation)


# ═══════════════════════════════════════════════════════════════════
# Body creation helpers
# ═══════════════════════════════════════════════════════════════════

def make_rounded_body(comp, cx, cy, w, h, height, r=None, name='Body'):
    """Create a rounded-rectangle body (the starting block for most parts).

    Args:
        comp: Root component.
        cx, cy: Centre of rectangle on XY plane (cm).
        w, h: Width and height of rectangle (cm).
        height: Extrusion height (cm, Z direction).
        r: Corner radius (cm). Default: CORNER_R.
        name: Body name.

    Returns:
        Tuple of (ExtrudeFeature, BRepBody) or (None, None).
    """
    sk = comp.sketches.add(comp.xYConstructionPlane)
    sk.name = f'{name} Outline'
    draw_rounded_rect(sk, cx, cy, w, h, r)

    # Target area is approximately w*h minus corner cuts
    r_actual = r or CORNER_R
    target = w * h - (4 - math.pi) * r_actual * r_actual
    prof = find_profile_by_area(sk, target, tolerance=0.4)

    if prof is None:
        # Fallback: use largest profile
        prof = find_largest_profile(sk)

    ext = extrude_profile(comp, prof, height)
    if ext:
        body = ext.bodies.item(0)
        body.name = name
        return ext, body
    return None, None


def make_cylinder(comp, sketch_plane, cx, cy, radius, height,
                  operation=None, name='Cylinder'):
    """Create a cylinder by extruding a circle.

    Args:
        comp: Root component.
        sketch_plane: Plane for the circle sketch.
        cx, cy: Circle centre (cm).
        radius: Circle radius (cm).
        height: Extrusion height (cm).
        operation: Feature operation. Default: NewBody.
        name: Body name.

    Returns:
        The ExtrudeFeature, or None.
    """
    if operation is None:
        operation = adsk.fusion.FeatureOperations.NewBodyFeatureOperation

    sk = comp.sketches.add(sketch_plane)
    sk.name = name
    sk.sketchCurves.sketchCircles.addByCenterRadius(p(cx, cy), radius)
    prof = find_smallest_profile(sk)
    ext = extrude_profile(comp, prof, height, operation)
    if ext and operation == adsk.fusion.FeatureOperations.NewBodyFeatureOperation:
        try:
            ext.bodies.item(0).name = name
        except Exception as e:
            print(f'  Warning: {e}')
    return ext


# ═══════════════════════════════════════════════════════════════════
# Assembly / mating features
# ═══════════════════════════════════════════════════════════════════

def make_m2_through_hole(comp, sketch_plane, cx, cy, depth):
    """Create an M2 clearance through-hole.

    Args:
        comp: Root component.
        sketch_plane: Plane at entry face.
        cx, cy: Centre (cm).
        depth: Through-depth (cm).

    Returns:
        The ExtrudeFeature, or None.
    """
    sk = comp.sketches.add(sketch_plane)
    sk.name = 'M2 Hole'
    sk.sketchCurves.sketchCircles.addByCenterRadius(p(cx, cy), M2_CLEAR)
    prof = find_smallest_profile(sk)
    return cut_profile(comp, prof, depth, flip=True)


def make_m3_grub_hole(comp, sketch_plane, cx, cy, depth):
    """Create an M3 grub screw hole.

    Args:
        comp: Root component.
        sketch_plane: Plane at entry face.
        cx, cy: Centre (cm).
        depth: Bore depth (cm).

    Returns:
        The ExtrudeFeature, or None.
    """
    sk = comp.sketches.add(sketch_plane)
    sk.name = 'M3 Grub'
    sk.sketchCurves.sketchCircles.addByCenterRadius(p(cx, cy), GRUB_M3)
    prof = find_smallest_profile(sk)
    return cut_profile(comp, prof, depth, flip=True)


# ═══════════════════════════════════════════════════════════════════
# Utility
# ═══════════════════════════════════════════════════════════════════

def zoom_fit(app=None):
    """Zoom the active viewport to fit all geometry."""
    if app is None:
        app = adsk.core.Application.get()
    app.activeViewport.fit()


def get_body(comp, name=None):
    """Get the first body in the component, optionally by name.

    Args:
        comp: Root component.
        name: Optional body name to match.

    Returns:
        The BRepBody, or None.
    """
    for i in range(comp.bRepBodies.count):
        body = comp.bRepBodies.item(i)
        if name is None or body.name == name:
            return body
    return None
