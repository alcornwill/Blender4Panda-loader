import os
from panda3d.core import * 

order = 20
target = 'scene'
description = 'Base scene import'
author = '09th'

def linearrgb_to_srgb(col):
    # Function ported from standard Blender shader
    new_col = []
    for c in col:
        if c < 0.0031308:
            new_col.append(max(0, c * 12.92))
        else:
            new_col.append(1.055 * pow(c, 1.0/2.4) - 0.055)
    return new_col

def invoke(data_dict, fname):
    data = data_dict['scene']
    egg_file = fname.replace('.egg.json', '.egg')
    egg_file = egg_file.replace('\\','/')
    if ':' in egg_file:
        # has drive letter
        egg_file = egg_file.replace(':', '')
        drive_letter, egg_file = egg_file[:1], egg_file[1:]
        drive_letter = drive_letter.lower()
        egg_file = '/' + drive_letter + egg_file
    model = loader.loadModel(egg_file)
    model.reparent_to(render)
    if 'horizon_color' in data:
        r,g,b = linearrgb_to_srgb(data['horizon_color'])
        #r,g,b = data['horizon_color']
        base.win.setClearColor((r, g, b, 1))
    node = AmbientLight("Ambient Light")
    color = data['ambient_color']
    node.setColor(Vec4(color[0], color[1], color[2], 1.0))
    np = NodePath(node)
    np.reparent_to(render)
