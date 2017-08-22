
import json
from ext import extensions
from os.path import basename

# Known restrictions:
# 1. You should work with "Blender Game" engine instead of standart "Blender Render"
# 2. If you wish to use Blender shaders, then you strictly should use materials, 
# even if Blender show somethig without it
# 3. Bug in Blender: sometimes use_shadow property = False, but Light still cast shadow
# you should recheck flag to avoid error while loading scene


def load(fname, scene):
    f = open(fname + '.json', 'r')
    data_dict = json.loads(f.read())
    f.close()
    data_dict = data_dict

    extensions_ = data_dict['scene']['extensions']
    # this isn't very good
    # some extensions are required
    # and names don't correspond between exporter/loader
    for ext in extensions:
        name = ext.__name__.split('.')[-1]
        if name not in extensions_: continue
        ext.invoke(data_dict, fname, scene)

    fn = basename(fname)
    root = scene.find(fn)
    return root