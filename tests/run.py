#!/usr/bin/env python3
"""Execute regression checks against the manager using GJS and Shell doubles."""
from pathlib import Path
import re, subprocess, tempfile
root = Path(__file__).resolve().parents[1]
source = (root / 'panelVisibilityManager.js').read_text()
source = re.sub(r'^import .*?;\n', '', source, flags=re.M).replace('export class ', 'class ')
mocks = '''
let time = 0, focus = null, pointer = [200, 0];
let removed = [], pressureDestroyed = 0, barrierDestroyed = 0;
const GLib = {get_monotonic_time: () => time, source_remove: id => removed.push(id),
    PRIORITY_DEFAULT: 0, SOURCE_REMOVE: false, SOURCE_CONTINUE: true};
const Meta = {}, Shell = {ActionMode: {NORMAL: 1}}, Clutter = {
    AnimationMode: {EASE_OUT_QUAD: 1},
    ActorBox: class {init_rect(x, y, w, h) {this.x1=x;this.y1=y;this.x2=x+w;this.y2=y+h;}}
};
const Config = {PACKAGE_VERSION: '50.5'}, Layout = {}, PointerWatcher = {};
const Convenience = {DEBUG: () => {}}, Intellihide = {}, DesktopIconsIntegration = {};
let easing = null, easeCount = 0, transitionRemovals = 0;
const panel = {visible: false, x: 0, y: 0, width: 1920, height: 30, translation_y: -30,
    contains: actor => actor === 'panel', get_pivot_point: () => [0, 0],
    show() {this.visible=true;}, hide() {this.visible=false;},
    remove_transition() {transitionRemovals++;},
    ease(params) {easing=params;easeCount++;this.translation_y=params.translation_y;}};
const Main = {messageTray: {}, layoutManager: {panelBox: panel,
    primaryMonitor: {x: 0, y: 0, width: 1920, inFullscreen: false}},
    overview: {visible: false, _overview: {_controls: {_searchEntryBin: null}}}};
const global = {stage: {get_key_focus: () => focus}, get_pointer: () => pointer};
function assert(value, msg) { if (!value) throw new Error(msg); }
'''
tests = '''
const manager = Object.create(PanelVisibilityManager.prototype);
manager._base_y = 0;
manager._edgeEnteredAt = null;
manager._settings = {get_boolean: () => false, get_double: () => 0.2};
let shows = 0;
manager.show = () => shows++;
manager._handleEdgePointer(200, 0);
assert(shows === 0, 'No immediate reveal before hover dwell');
time = 150000;
manager._handleEdgePointer(200, 0);
assert(shows === 1, 'Stationary edge hover reveals after dwell');
focus = 'spotlight';
time += 200000;
manager._handleEdgePointer(200, 0);
assert(shows === 1, 'Shell popup focus suppresses edge activation');
assert(manager._edgeEnteredAt === null, 'Popup focus resets hover dwell');
focus = null;
Main.layoutManager.primaryMonitor.inFullscreen = true;
manager._handleEdgePointer(200, 0);
assert(shows === 1, 'Fullscreen preference respected');
Main.layoutManager.primaryMonitor.inFullscreen = false;
manager._handleEdgePointer(200, 5);
assert(manager._edgeEnteredAt === null, 'Outside edge resets hover dwell');
manager._pointerWatcher = {_removeWatch: watch => removed.push(watch)};
manager._pointerListener = 11;
manager._edgePollId = 12;
manager._panelPressure = {removeBarrier: () => {}, destroy: () => pressureDestroyed++};
manager._panelBarrier = {destroy: () => barrierDestroyed++};
manager._disablePressureBarrier();
manager._disablePressureBarrier();
assert(pressureDestroyed === 1 && barrierDestroyed === 1, 'Pressure cleanup is idempotent');
assert(removed.includes(11) && removed.includes(12), 'Pointer watch and polling are removed');

manager.show = PanelVisibilityManager.prototype.show;
manager._panelShown = false;
manager._originalTranslationY = 0;
manager._preventHide = false;
manager._animationActive = false;
manager._staticBox = new Clutter.ActorBox();
manager._intellihide = {updateTargetBox: () => {}};
manager._desktopIconsUsableArea = {resetMargins: () => {}, setMargins: () => {}};
manager._updateHotCorner = () => {};
manager._pointerWatcher.addWatch = () => 99;
manager._pointerListener = null;
pointer = [200, 0];
manager.show(0.2, 'mouse-enter');
assert(easing.translation_y === 0 && !('y' in easing), 'Reveal animates translation, not Shell layout position');
const count = easeCount;
manager.show(0.2, 'mouse-enter');
assert(easeCount === count && transitionRemovals === 0, 'Repeated edge triggers do not cancel the reveal');
easing.onComplete();
assert(manager._panelShown && manager._isHovering(200, 0), 'Cursor remains in hover region after reveal');
manager.hide(0.2, 'mouse-left');
assert(manager._panelShown && easeCount === count, 'Pointer at top edge must not cause auto-hide');
// A layout change while hidden cannot move the logical hover target off screen.
panel.y = -30;
manager._updateStaticBox();
assert(manager._isHovering(200, 0), 'Hover geometry independent of animated or reassigned actor y');
pointer = [200, 100];
manager.hide(0.2, 'mouse-left');
assert(!manager._panelShown && easing.translation_y === -30, 'Leaving the panel hides through visual translation');
easing.onComplete();
assert(!panel.visible, 'Fully hidden panel is removed from input picking');
const hiddenCount = easeCount;
manager.hide(0.2, 'mouse-left');
assert(easeCount === hiddenCount, 'Repeated hide is idempotent');
print('PASS: hover, popup focus, fullscreen, cleanup, stable geometry, animation deduplication, hidden input state');
'''
with tempfile.NamedTemporaryFile(suffix='.js', mode='w') as f:
    f.write(mocks + source + tests)
    f.flush()
    subprocess.run(['gjs', f.name], check=True)
