#!/usr/bin/env python3
from pathlib import Path
import re, subprocess, tempfile
root=Path(__file__).resolve().parents[1]
s=(root/'extension.js').read_text()
s=re.sub(r'^import .*?;\n','',s,flags=re.M).replace('export default class','class')
mocks='''
let holds=0, destroyed=0, fail=false;
const Main={layoutManager:{primaryIndex:0}};
const global={compositor:{disable_unredirect(){holds++;},enable_unredirect(){holds--;}}};
const Convenience={DEBUG(){}};
class Extension {constructor(metadata){this.uuid=metadata.uuid;}getSettings(){return {};}}
const PanelVisibilityManager={PanelVisibilityManager:class {
    constructor(){if(fail)throw new Error('init failure');}
    destroy(){destroyed++;}
}};
function assert(x,m){if(!x)throw new Error(m);}
'''
checks='''
const e=new HideTopBarExtension({uuid:'test'});
e.enable();assert(holds===1,'composition is held while enabled');
e.disable();assert(holds===0 && destroyed===1,'disable releases composition');
e.disable();assert(holds===0,'repeated disable does not over-release');
fail=true;
try {e.enable();}catch(error){}
assert(holds===0,'initialization failure releases composition');
print('PASS: balanced composition inhibition and initialization-failure cleanup');
'''
with tempfile.NamedTemporaryFile(suffix='.js',mode='w') as f:
    f.write(mocks+s+checks);f.flush()
    subprocess.run(['gjs',f.name],check=True)
