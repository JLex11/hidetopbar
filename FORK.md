# Fix notes

Upstream: tuxor1337/hidetopbar, commit aa7d51e.

With auto-hide removing the reserved panel area, maximized windows cover the
monitor. This fork combines a balanced `global.compositor.disable_unredirect()`
with `trackFullscreen: false` while it owns the panel. Both changes are restored
on disable. The combined correction resolved the reported hover and Spotlight
failures on GNOME/Mutter 50.5; the individual contribution of each change was
not isolated on the physical display.

GNOME itself uses the same compositor inhibit API around modal UI:
https://github.com/GNOME/gnome-shell/blob/gnome-50/js/ui/main.js

The panel moves through `translation_y`, without modifying its layout `y`.
Hover uses the fixed monitor edge instead of the moving actor position. Repeated
show requests do not cancel an opening animation, and automatic mouse-leave
requests do not hide the panel while the cursor is inside that region.

The fork also preserves settings signal connections during UI initialization,
destroys old pressure barriers, and removes watches and pending callbacks during
cleanup. It has a separate UUID, settings schema and shortcut name so it can be
installed alongside the original, with only one enabled.

Automated tests cover behavior through GJS with Shell doubles. A separate real
headless GNOME/Mutter 50.5 session loaded this fork and the original Spotlight,
created a maximized GTK 4 application, and verified panel visibility after edge
hover and Spotlight visibility after opening. A headless monitor does not
reproduce physical display scanout; the final confirmation came from the
affected desktop session.

Only GNOME 50 is declared supported. Compositor inhibition is held for the
extension's lifetime and may increase rendering overhead for games or video.
