
from panda3d.core import *

order = 30
target = 'object'

def get_mask(lst):
    bits = [CollideMask.bit(i) for i, value in enumerate(lst) if value]
    if len(bits) == 0:
        mask = CollideMask.allOff()
    else:
        mask = bits[0]
        for bit in bits[1:]: mask |= bit
    return mask

def invoke(data_dict, fname):
    colliders = data_dict['colliders']
    for name, collider in colliders.items():
        parent = render.find("**/" + name)
        bounds = collider["bounds"]
        radius = [i / 2.0 for i in bounds]

        # NOTE: only BOX, CAPSULE and SPHERE supported
        if collider["type"] == "BOX":
            solid = CollisionBox(0.0, radius[0], radius[1], radius[2])
        if collider["type"] == "CAPSULE":
            z = radius[2]
            solid = CollisionTube(0.0, 0.0, -z, 0.0, 0.0, z, max(*radius[:2]))
        if collider["type"] == "SPHERE":
            solid = CollisionSphere(0, 0, 0, max(*radius))

        from_ = get_mask(collider["from"])
        into = get_mask(collider["into"])

        col = CollisionNode(name)
        col.addSolid(solid) # if was compound add here
        col.setFromCollideMask(from_)
        col.setIntoCollideMask(into)
        col.setPythonTag('link', parent)  # we do this now
        np = parent.attachNewNode(col)  # might want to replace parent?
        handler = CollisionHandlerQueue()  # might want to parametize type of handler
        base.cTrav.addCollider(np, handler)
        base.colliders.append(np)