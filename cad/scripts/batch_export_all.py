"""
Mars Rover — Batch Export All Components
=========================================

Master script that runs each component script in sequence,
exports STL files, and logs progress. Run this ONCE in Fusion 360
to generate all Phase 1 STLs.

Usage:
  1. Open Fusion 360
  2. Shift+S (Scripts and Add-Ins)
  3. Select "BatchExportAll" > Run
  4. Wait for completion (~5-10 min, exports 29 STL files)
  5. Check D:/Mars Rover Project/3d-print/ for output

Output: STL files in D:/Mars Rover Project/3d-print/<category>/
Log:    D:/Mars Rover Project/3d-print/batch_export_log.txt

Note: EA-25 suspension audit deprecated BogieArm, RockerArm, and
DiffBarAdapter in favour of tube + printed connector approach.
Those scripts are excluded. New scripts: RoverWheelV3,
CableClip, BogiePivotConnector, FrontWheelConnector,
MiddleWheelConnector, RockerHubConnector, TubeSocketTest,
DifferentialPivotHousing, DifferentialLink, SteeringKnuckle,
SteeringHornLink (EA-27).
"""

import adsk.core
import adsk.fusion
import traceback
import os
import sys
import importlib.util
import time

# ── STL export output root ──
STL_ROOT = r'D:\Mars Rover Project\3d-print'

# ── Fusion 360 Scripts root ──
FUSION_SCRIPTS = os.path.join(
    os.environ.get('APPDATA', ''),
    'Autodesk', 'Autodesk Fusion 360', 'API', 'Scripts'
)

# ── Component definitions ──
# (ScriptFolderName, stl_subdir, stl_filename, body_name_filter, notes)
# body_name_filter: if set, only export bodies whose name contains this string
# stl_filename: if None, handled specially (multi-body or multi-run)
COMPONENTS = [
    # Stage 1: Calibration & Test Pieces
    ('CalibrationTestCard', 'calibration', 'calibration_test_card.stl', 'Calibration Card', 'Stage 1'),
    ('BearingTestPiece',    'calibration', 'bearing_test_piece.stl',    None, 'Stage 1'),
    ('TubeSocketTest',      'calibration', 'tube_socket_test.stl',     None, 'Stage 1 — validate 8mm rod fit'),

    # Stage 2: Wheels (V3 replaces V1, EA-25)
    ('RoverWheelV3', 'wheels', 'rover_wheel_v3.stl', 'Wheel V3', 'Stage 2 — print x6'),
    ('RoverTire',    'wheels', 'rover_tire.stl',      None, 'Stage 2 — TPU x6 (friend\'s printer)'),

    # Stage 3: Steering & Motor Mounts
    ('SteeringBracket',  'steering', 'steering_bracket.stl',  None, 'Stage 3 — print x4'),
    ('FixedWheelMount',  'steering', 'fixed_wheel_mount.stl', None, 'Stage 3 — print x2'),
    ('ServoMount',       'steering', 'servo_mount.stl',       None, 'Stage 3 — print x4'),
    ('SteeringKnuckle',  'steering', 'steering_knuckle.stl', 'Steering Knuckle', 'Stage 3 — print x4'),
    ('SteeringHornLink', 'steering', 'steering_horn_link.stl', 'Steering Horn Link', 'Stage 3 — print x4 (EA-27)'),

    # Stage 4: Suspension Connectors (EA-25 tube + connector, EA-26 diff mechanism)
    # Note: BogieArm, RockerArm, DiffBarAdapter DEPRECATED per EA-25
    ('RockerHubConnector',          'suspension', 'rocker_hub_connector.stl',          'Rocker Hub Connector',          'Stage 4 — print x2'),
    ('BogiePivotConnector',         'suspension', 'bogie_pivot_connector.stl',         'Bogie Pivot Connector',         'Stage 4 — print x2'),
    ('FrontWheelConnector',         'suspension', 'front_wheel_connector.stl',         'Front Wheel Connector',         'Stage 4 — print x4'),
    ('MiddleWheelConnector',        'suspension', 'middle_wheel_connector.stl',        'Middle Wheel Connector',        'Stage 4 — print x2'),
    ('DifferentialPivotHousing',    'suspension', 'differential_pivot_housing.stl',    'Diff Pivot Housing',            'Stage 4 — print x1'),
    ('DifferentialLink',            'suspension', 'differential_link.stl',             'Differential Link',             'Stage 4 — print x2'),
    ('CableClip',                   'suspension', 'cable_clip.stl',                    'Cable Clip',                    'Stage 4 — print x12'),

    # Stage 5: Body (BodyQuadrant handled specially — 4 runs)
    ('BodyQuadrant', 'body', None,             None, 'Stage 5 — 4 quadrants'),
    ('TopDeck',      'body', None,             None, 'Stage 5 — 4 tiles'),

    # Stage 6: Internal Components
    ('ElectronicsTray',    'body', 'electronics_tray.stl',    None, 'Stage 6'),
    ('StrainReliefClip',   'body', 'strain_relief_clip.stl',  None, 'Stage 6 — print x10'),
    ('FuseHolderBracket',  'body', 'fuse_holder_bracket.stl', None, 'Stage 6'),
    ('SwitchMountPlate',   'body', 'switch_mount_plate.stl',  None, 'Stage 6'),
]


def load_script_module(script_folder_name):
    """Load a Fusion 360 script module from its Scripts folder.

    Scripts are located at: FUSION_SCRIPTS/<Name>/<Name>.py
    Returns the loaded module.
    """
    script_path = os.path.join(
        FUSION_SCRIPTS, script_folder_name, f'{script_folder_name}.py'
    )
    if not os.path.exists(script_path):
        raise FileNotFoundError(f'Script not found: {script_path}')

    spec = importlib.util.spec_from_file_location(script_folder_name, script_path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def export_body_as_stl(body, filepath):
    """Export a single Fusion 360 body as binary STL (high refinement)."""
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    exportMgr = design.exportManager

    stlOptions = exportMgr.createSTLExportOptions(body)
    stlOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    stlOptions.filename = filepath
    exportMgr.execute(stlOptions)
    return True


def export_bodies(rootComp, stl_dir, filename=None, body_filter=None):
    """Export bodies from root component. Returns list of exported paths."""
    os.makedirs(stl_dir, exist_ok=True)
    exported = []
    bodies = rootComp.bRepBodies

    # Also check nested components (e.g. BearingTestPiece creates a subcomponent)
    all_bodies = []
    for i in range(bodies.count):
        all_bodies.append(bodies.item(i))
    for i in range(rootComp.occurrences.count):
        occ = rootComp.occurrences.item(i)
        comp_bodies = occ.component.bRepBodies
        for j in range(comp_bodies.count):
            all_bodies.append(comp_bodies.item(j))

    for body in all_bodies:
        if body_filter and body_filter not in body.name:
            continue

        if filename:
            filepath = os.path.join(stl_dir, filename)
        else:
            safe_name = body.name.replace(' ', '_').replace('/', '_').lower()
            filepath = os.path.join(stl_dir, f'{safe_name}.stl')

        try:
            export_body_as_stl(body, filepath)
            exported.append(filepath)
            if filename:
                break  # Only first match when specific filename given
        except Exception as e:
            pass  # Will be caught in error summary

    return exported


def create_new_design():
    """Create a new empty design document. Returns (design, rootComponent)."""
    app = adsk.core.Application.get()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    return design, design.rootComponent


def close_active_document():
    """Close the current document without saving."""
    app = adsk.core.Application.get()
    doc = app.activeDocument
    if doc:
        doc.close(False)


def _patch_source_for_batch(source):
    """Patch script source to suppress ui.messageBox() blocking dialogs.

    Replaces ui.messageBox( with a no-op function call so scripts don't
    block waiting for user interaction during batch execution.
    """
    # Inject a silent replacement function at the top of the source
    prefix = "def _batch_noop(*args, **kwargs): return 0\n"
    patched = prefix + source.replace('ui.messageBox(', '_batch_noop(')
    return patched


def run_component_script(script_folder_name, context):
    """Load and run a component script with messageBox suppressed."""
    script_path = os.path.join(
        FUSION_SCRIPTS, script_folder_name, f'{script_folder_name}.py'
    )
    if not os.path.exists(script_path):
        raise FileNotFoundError(f'Script not found: {script_path}')

    with open(script_path, 'r', encoding='utf-8') as f:
        source = f.read()

    patched = _patch_source_for_batch(source)
    ns = {'__name__': f'{script_folder_name}_batch'}
    exec(compile(patched, script_path, 'exec'), ns)
    ns['run'](context)


def run_body_quadrant(quadrant, context):
    """Run BodyQuadrant script with a specific quadrant (FL/FR/RL/RR).

    Patches both QUADRANT variable and messageBox suppression.
    """
    script_path = os.path.join(
        FUSION_SCRIPTS, 'BodyQuadrant', 'BodyQuadrant.py'
    )
    with open(script_path, 'r', encoding='utf-8') as f:
        source = f.read()

    # Patch QUADRANT variable
    patched = source.replace("QUADRANT = 'FL'", f"QUADRANT = '{quadrant}'")
    # Patch messageBox suppression
    patched = _patch_source_for_batch(patched)

    ns = {'__name__': 'BodyQuadrant_patched'}
    exec(compile(patched, script_path, 'exec'), ns)
    ns['run'](context)


def run_top_deck(tile, context):
    """Run TopDeck script with a specific tile (FL/FR/RL/RR).

    Patches both TILE variable and messageBox suppression.
    """
    script_path = os.path.join(
        FUSION_SCRIPTS, 'TopDeck', 'TopDeck.py'
    )
    with open(script_path, 'r', encoding='utf-8') as f:
        source = f.read()

    # Patch TILE variable
    patched = source.replace("TILE = 'FL'", f"TILE = '{tile}'")
    # Patch messageBox suppression
    patched = _patch_source_for_batch(patched)

    ns = {'__name__': 'TopDeck_patched'}
    exec(compile(patched, script_path, 'exec'), ns)
    ns['run'](context)


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        message_log = []

        # Count total steps (body_quadrant = 4 runs, everything else = 1)
        total = sum(4 if c[0] in ('BodyQuadrant', 'TopDeck') else 1 for c in COMPONENTS)
        completed = 0
        errors = []
        all_exported = []
        start_time = time.time()

        # Progress dialog
        progressDialog = ui.createProgressDialog()
        progressDialog.cancelButtonText = 'Cancel'
        progressDialog.isBackgroundTranslucent = False
        progressDialog.isCancelButtonShown = True
        progressDialog.show('Mars Rover Batch Export', 'Starting...', 0, total, 0)

        for comp_def in COMPONENTS:
            script_name, stl_subdir, stl_filename, body_filter, notes = comp_def
            stl_dir = os.path.join(STL_ROOT, stl_subdir)

            if progressDialog.wasCancelled:
                break

            # ── SPECIAL: BodyQuadrant — 4 separate runs ──
            if script_name == 'BodyQuadrant':
                for quad in ['FL', 'FR', 'RL', 'RR']:
                    if progressDialog.wasCancelled:
                        break

                    progressDialog.message = f'[{completed+1}/{total}] Body Quadrant {quad}...'
                    adsk.doEvents()

                    try:
                        design, rootComp = create_new_design()
                        run_body_quadrant(quad, context)

                        exported = export_bodies(
                            rootComp, stl_dir,
                            filename=f'body_quadrant_{quad.lower()}.stl',
                            body_filter=f'Body {quad}'
                        )
                        all_exported.extend(exported)
                        close_active_document()

                    except Exception as e:
                        errors.append(f'BodyQuadrant_{quad}: {str(e)[:200]}')
                        try:
                            close_active_document()
                        except:
                            pass

                    completed += 1
                    progressDialog.progressValue = completed
                continue

            # ── SPECIAL: TopDeck — 4 separate tile runs ──
            if script_name == 'TopDeck':
                for tile in ['FL', 'FR', 'RL', 'RR']:
                    if progressDialog.wasCancelled:
                        break

                    progressDialog.message = f'[{completed+1}/{total}] Top Deck {tile}...'
                    adsk.doEvents()

                    try:
                        design, rootComp = create_new_design()
                        run_top_deck(tile, context)

                        exported = export_bodies(
                            rootComp, stl_dir,
                            filename=f'top_deck_{tile.lower()}.stl',
                            body_filter=f'Top Deck {tile}'
                        )
                        all_exported.extend(exported)
                        close_active_document()

                    except Exception as e:
                        errors.append(f'TopDeck_{tile}: {str(e)[:200]}')
                        try:
                            close_active_document()
                        except:
                            pass

                    completed += 1
                    progressDialog.progressValue = completed
                continue

            # ── NORMAL: single script, single STL ──
            progressDialog.message = f'[{completed+1}/{total}] {script_name} ({notes})...'
            adsk.doEvents()

            try:
                design, rootComp = create_new_design()
                run_component_script(script_name, context)

                exported = export_bodies(rootComp, stl_dir, stl_filename, body_filter)
                all_exported.extend(exported)
                close_active_document()

            except Exception as e:
                errors.append(f'{script_name}: {str(e)[:200]}')
                try:
                    close_active_document()
                except:
                    pass

            completed += 1
            progressDialog.progressValue = completed

        progressDialog.hide()

        elapsed = time.time() - start_time

        # ── Build summary ──
        lines = [
            'MARS ROVER — BATCH EXPORT COMPLETE',
            '=' * 50,
            f'Components processed: {completed}/{total}',
            f'STL files exported:   {len(all_exported)}',
            f'Errors:               {len(errors)}',
            f'Elapsed time:         {elapsed:.0f}s ({elapsed/60:.1f} min)',
            '',
            'EXPORTED FILES:',
        ]
        for fp in all_exported:
            sz = os.path.getsize(fp) / 1024 if os.path.exists(fp) else 0
            lines.append(f'  {os.path.relpath(fp, STL_ROOT):45s}  {sz:6.0f} KB')

        if errors:
            lines.append('')
            lines.append('ERRORS:')
            for e in errors:
                lines.append(f'  {e}')

        lines.append('')
        lines.append('NEXT STEPS:')
        lines.append('  1. Open each STL in Cura, verify dimensions')
        lines.append('  2. Slice with settings from print-strategy.md')
        lines.append('  3. Export gcode, convert: gpx -m cr1d input.gcode output.x3g')
        lines.append('  4. Copy .x3g to SD card, print on CTC Bizer')

        summary = '\n'.join(lines)

        # Write log
        log_path = os.path.join(STL_ROOT, 'batch_export_log.txt')
        with open(log_path, 'w') as f:
            f.write(summary)
            f.write(f'\n\nTimestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}')
            if message_log:
                f.write('\n\nSCRIPT MESSAGES:\n')
                for m in message_log:
                    f.write(f'  {m}\n')

        ui.messageBox(summary, 'Mars Rover — Batch Export')

    except:
        if ui:
            ui.messageBox(f'Batch export failed:\n{traceback.format_exc()}')
