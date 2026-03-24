"""
Mars Rover — Fix Remaining Components
======================================

Re-runs only the components that failed in the initial batch:
  - CalibrationTestCard (was 684 bytes — cut direction bug was present)
  - BodyQuadrant x4 (encoding error reading script file)

Run after the main BatchExportAll has been fixed.
"""

import adsk.core
import adsk.fusion
import traceback
import os
import time


STL_ROOT = r'D:\Mars Rover Project\3d-print'
FUSION_SCRIPTS = os.path.join(
    os.environ.get('APPDATA', ''),
    'Autodesk', 'Autodesk Fusion 360', 'API', 'Scripts'
)


def _patch_source_for_batch(source):
    prefix = "def _batch_noop(*args, **kwargs): return 0\n"
    return prefix + source.replace('ui.messageBox(', '_batch_noop(')


def export_body_as_stl(body, filepath):
    app = adsk.core.Application.get()
    design = adsk.fusion.Design.cast(app.activeProduct)
    exportMgr = design.exportManager
    stlOptions = exportMgr.createSTLExportOptions(body)
    stlOptions.meshRefinement = adsk.fusion.MeshRefinementSettings.MeshRefinementHigh
    stlOptions.filename = filepath
    exportMgr.execute(stlOptions)


def export_bodies(rootComp, stl_dir, filename=None, body_filter=None):
    os.makedirs(stl_dir, exist_ok=True)
    exported = []

    all_bodies = []
    bodies = rootComp.bRepBodies
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
                break
        except Exception as e:
            pass

    return exported


def create_new_design():
    app = adsk.core.Application.get()
    doc = app.documents.add(adsk.core.DocumentTypes.FusionDesignDocumentType)
    design = adsk.fusion.Design.cast(app.activeProduct)
    return design, design.rootComponent


def close_active_document():
    app = adsk.core.Application.get()
    doc = app.activeDocument
    if doc:
        doc.close(False)


def run(context):
    app = adsk.core.Application.get()
    ui = app.userInterface

    try:
        errors = []
        all_exported = []
        total = 5  # 1 CalibrationTestCard + 4 BodyQuadrant
        completed = 0
        start_time = time.time()

        progressDialog = ui.createProgressDialog()
        progressDialog.cancelButtonText = 'Cancel'
        progressDialog.isBackgroundTranslucent = False
        progressDialog.isCancelButtonShown = True
        progressDialog.show('Mars Rover Fix Remaining', 'Starting...', 0, total, 0)

        # ── 1. CalibrationTestCard ──
        progressDialog.message = f'[1/{total}] CalibrationTestCard...'
        adsk.doEvents()

        try:
            design, rootComp = create_new_design()
            script_path = os.path.join(FUSION_SCRIPTS, 'CalibrationTestCard', 'CalibrationTestCard.py')
            with open(script_path, 'r', encoding='utf-8') as f:
                source = f.read()
            patched = _patch_source_for_batch(source)
            ns = {'__name__': 'CalibrationTestCard_fix'}
            exec(compile(patched, script_path, 'exec'), ns)
            ns['run'](context)

            stl_dir = os.path.join(STL_ROOT, 'calibration')
            exported = export_bodies(rootComp, stl_dir, 'calibration_test_card.stl', 'Calibration Card')
            all_exported.extend(exported)
            close_active_document()
        except Exception as e:
            errors.append(f'CalibrationTestCard: {str(e)[:200]}')
            try:
                close_active_document()
            except:
                pass

        completed += 1
        progressDialog.progressValue = completed

        # ── 2-5. BodyQuadrant x4 ──
        for quad in ['FL', 'FR', 'RL', 'RR']:
            if progressDialog.wasCancelled:
                break

            progressDialog.message = f'[{completed+1}/{total}] Body Quadrant {quad}...'
            adsk.doEvents()

            try:
                design, rootComp = create_new_design()
                script_path = os.path.join(FUSION_SCRIPTS, 'BodyQuadrant', 'BodyQuadrant.py')
                with open(script_path, 'r', encoding='utf-8') as f:
                    source = f.read()

                patched = source.replace("QUADRANT = 'FL'", f"QUADRANT = '{quad}'")
                patched = _patch_source_for_batch(patched)
                ns = {'__name__': 'BodyQuadrant_fix'}
                exec(compile(patched, script_path, 'exec'), ns)
                ns['run'](context)

                stl_dir = os.path.join(STL_ROOT, 'body')
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

        progressDialog.hide()

        elapsed = time.time() - start_time
        lines = [
            'FIX REMAINING — COMPLETE',
            '=' * 40,
            f'Processed: {completed}/{total}',
            f'STL files: {len(all_exported)}',
            f'Errors:    {len(errors)}',
            f'Time:      {elapsed:.0f}s',
            '',
        ]
        for fp in all_exported:
            sz = os.path.getsize(fp) / 1024 if os.path.exists(fp) else 0
            lines.append(f'  {os.path.relpath(fp, STL_ROOT):45s}  {sz:6.0f} KB')

        if errors:
            lines.append('')
            lines.append('ERRORS:')
            for e in errors:
                lines.append(f'  {e}')

        summary = '\n'.join(lines)

        log_path = os.path.join(STL_ROOT, 'batch_fix_log.txt')
        with open(log_path, 'w') as f:
            f.write(summary)
            f.write(f'\n\nTimestamp: {time.strftime("%Y-%m-%d %H:%M:%S")}')

        ui.messageBox(summary, 'Mars Rover — Fix Remaining')

    except:
        if ui:
            ui.messageBox(f'Fix batch failed:\n{traceback.format_exc()}')
