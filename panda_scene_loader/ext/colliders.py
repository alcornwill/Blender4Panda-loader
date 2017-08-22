
from panda3d.core import *

order = 30
target = 'object'

def copy_tags(a, b):
    for k in a.getTagKeys():
        v = a.getTag(k)
        b.setTag(k, v)

def invoke(data_dict, fname, scene):
    colliders = data_dict['colliders']
    for name, collider in colliders.items():
        parent = scene.find("**/" + name)
        bounds = collider["bounds"]
        radius = [i / 2.0 for i in bounds]

        from_ = BitMask32(collider["from"])
        into = BitMask32(collider["into"])

        # NOTE: only TRIANGLE_MESH, BOX, CAPSULE and SPHERE supported
        if collider["type"] == "TRIANGLE_MESH":
            # use visible geometry
            parent.node().setIntoCollideMask(into)
            continue
        if collider["type"] == "BOX":
            solid = CollisionBox(0.0, radius[0], radius[1], radius[2])
        if collider["type"] == "CAPSULE":
            z = radius[2]
            solid = CollisionTube(0.0, 0.0, -z, 0.0, 0.0, z, max(*radius[:2]))
        if collider["type"] == "SPHERE":
            solid = CollisionSphere(0, 0, 0, max(*radius))

        col = CollisionNode(name)
        col.addSolid(solid) # if was compound add here
        col.setFromCollideMask(from_)
        col.setIntoCollideMask(into)
        if collider['keep']:
            np = parent.attachNewNode(col)
            copy_tags(parent, np)
        else:
            col.replaceNode(parent.node())
            parent.hide()
        handler = CollisionHandlerQueue()  # might want to parametize type of handler
        base.cTrav.addCollider(np, handler)