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

def invoke(data_dict, fname, scene):
    data = data_dict['scene']
    egg_file = Filename.fromOsSpecific(fname)
    model = loader.loadModel(egg_file)
    model.reparent_to(scene)
    if 'horizon_color' in data:
        r,g,b = linearrgb_to_srgb(data['horizon_color'])
        #r,g,b = data['horizon_color']
        base.win.setClearColor((r, g, b, 1))
    if 'ambient_color' in data:
        node = AmbientLight("Ambient")
        color = data['ambient_color']
        node.setColor(Vec4(color[0], color[1], color[2], 1.0))
        np = NodePath(node)
        np.reparent_to(scene)
        scene.setLight(np)
    if 'use_mist' in data:
        start = data['mist_start']
        depth = data['mist_depth']
        fog = Fog("Fog")
        # fog.setColor(WHITE)
        # fog.setColor(base.win.getClearColor())
        falloff = data['mist_falloff']
        if falloff == 'LINEAR':
            fog.setLinearRange(start, start + depth)
        # todo others
        scene.setFog(fog)
