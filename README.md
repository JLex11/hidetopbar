# Hide Top Bar Fixed

A fork of [Hide Top Bar](https://github.com/tuxor1337/hidetopbar) for GNOME 50,
with fixes for a panel that flashes and disappears when revealed over a
maximized window, invisible panel buttons that remain clickable, and interference
with Spotlight-style launchers.

The combined fix has been confirmed on GNOME/Mutter 50.5. Compatibility with
other GNOME versions is not claimed.

## What changed

- Hold a balanced compositor inhibition while the extension is enabled, so
  windows covering the monitor cannot bypass Shell overlay composition.
- Let auto-hide control panel visibility instead of racing GNOME fullscreen tracking.
- Animate visual translation rather than the panel's layout position.
- Keep hover bounds anchored to the monitor edge, including panel height changes.
- Reveal after a stationary 150 ms hover at the top edge, without requiring pressure.
- Avoid interrupting an opening animation on repeated edge notifications.
- Clean up settings signals, pointer barriers, watches, menus and pending timers.
- Suppress edge activation while an unrelated Shell popup owns keyboard focus.

The original project and this fork have separate settings and extension IDs.
Do not enable both extensions at the same time.

## Install

Clone your fork or download its source, then run from the repository directory:

```sh
glib-compile-schemas --strict schemas
gnome-extensions pack --force --out-dir=. \
  --extra-source=panelVisibilityManager.js \
  --extra-source=intellihide.js \
  --extra-source=convenience.js \
  --extra-source=desktopIconsIntegration.js \
  --extra-source=Settings.ui \
  --extra-source=COPYING.txt .
gnome-extensions install --force hidetopbar-fixed@local.shell-extension.zip
```

Log out and log back in so GNOME loads the extension, then enable **Hide Top Bar
Fixed** in Extensions. Disable the original Hide Top Bar first. The fork retains
`hidetopbar-fixed@local` as its ID for compatibility with existing installations.

Enable **Show panel when mouse approaches edge of the screen**. Leave
**Show overview when mouse approaches edge of the screen** disabled if you only
want to reveal the panel. The new hover behavior targets the primary monitor.

## Validation

Requires Python 3, GJS and GLib tools; no Python packages are needed.

```sh
python3 tests/run.py
python3 tests/run_lifecycle.py
glib-compile-schemas --strict schemas
```

Regression tests use Shell doubles for hover, geometry, animation deduplication,
hidden input state, cleanup and balanced compositor inhibition. An isolated real
GNOME/Mutter 50.5 session with a maximized GTK 4 window and Spotlight verified
that edge hover keeps the panel visible and Spotlight remains open. The fix was
also confirmed in the affected desktop session.

Keeping composition enabled disables the unredirect optimization while the
extension is active; this may increase rendering overhead for games and video.
Normal compositor behavior is restored when the extension is disabled.

## Troubleshooting and rollback

Disable this fork and re-enable the original extension to roll back. Original
settings are preserved. Do not run both simultaneously.

For transition diagnostics:

```sh
gsettings --schemadir schemas set org.gnome.shell.extensions.hidetopbarfixed debug-transitions true
journalctl -b _COMM=gnome-shell --no-pager -g 'Hide Top Bar Fix'
gsettings --schemadir schemas set org.gnome.shell.extensions.hidetopbarfixed debug-transitions false
```

## Upstream and license

Based on upstream commit `aa7d51e`; original source:
[GNOME GitLab](https://gitlab.gnome.org/tuxor1337/hidetopbar).
The GitHub parent is its read-only mirror.

GPL-3.0-or-later. Original copyright notices and translations are preserved.
See [COPYING.txt](COPYING.txt) and [FORK.md](FORK.md).
