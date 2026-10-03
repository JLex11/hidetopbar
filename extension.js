/**
 * This file is part of Hide Top Bar
 *
 * Copyright 2020 Thomas Vogt
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program.  If not, see <https://www.gnu.org/licenses/>.
 */

import * as Main from 'resource:///org/gnome/shell/ui/main.js';

import * as PanelVisibilityManager from './panelVisibilityManager.js';
import * as Convenience from './convenience.js';
const DEBUG = Convenience.DEBUG;

import {Extension} from 'resource:///org/gnome/shell/extensions/extension.js';

let mSettings = null;
let mPVManager = null;
let monitorIndex = null;

export default class HideTopBarExtension extends Extension {
    constructor(metadata) {
        super(metadata);
        console.log(`Initiating ${this.uuid}`);
    }

    enable() {
        DEBUG("enable()");
        mSettings = this.getSettings();
        monitorIndex = Main.layoutManager.primaryIndex;
        // Without the reserved panel area, maximized apps can bypass composition.
        // Hold one balanced inhibit while auto-hide and Shell overlays are in use.
        global.compositor.disable_unredirect();
        this._compositionHeld = true;
        try {
            mPVManager = new PanelVisibilityManager.PanelVisibilityManager(
                mSettings, monitorIndex,
            );
        } catch (error) {
            global.compositor.enable_unredirect();
            this._compositionHeld = false;
            throw error;
        }
    }

    disable() {
        DEBUG("disable()");
        try {
            mPVManager?.destroy();
        } finally {
            mPVManager = null;
            mSettings = null;
            if (this._compositionHeld) {
                global.compositor.enable_unredirect();
                this._compositionHeld = false;
            }
        }
    }
}
