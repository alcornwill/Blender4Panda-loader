from panda3d.core import *
import math, os

order = 30
target = 'object'

RESTRICT_BUFFER_SIZE = 1024


def make_shadow_cam(name, obj):
    # make FBO
    bsize = obj['buffer_size']
    if bsize > RESTRICT_BUFFER_SIZE:
        print('WARNING: restrict shadow buffer size from %i to %i. See base_objects.py RESTRICT_BUFFER_SIZE.' % (
            bsize, RESTRICT_BUFFER_SIZE))
        bsize = RESTRICT_BUFFER_SIZE
    winprops = WindowProperties.size(bsize, bsize)
    props = FrameBufferProperties()
    props.setRgbColor(0)
    props.setAlphaBits(0)
    props.setDepthBits(1)
    LBuffer = base.graphicsEngine.makeOutput(
        base.pipe, "offscreen buffer", -2,
        props, winprops,
        GraphicsPipe.BFRefuseWindow,
        base.win.getGsg(), base.win)
    # render to texture
    Ldepthmap = Texture()
    Ldepthmap.setFormat(Texture.FDepthComponent)
    Ldepthmap.setMinfilter(Texture.FTShadow)
    Ldepthmap.setMagfilter(Texture.FTShadow)
    LBuffer.addRenderTexture(Ldepthmap, GraphicsOutput.RTMBindOrCopy, GraphicsOutput.RTPDepth)
    # clamp
    # Ldepthmap.setWrapU(Texture.WMClamp)
    # Ldepthmap.setWrapV(Texture.WMClamp)
    # make depth camera
    LCam = base.makeCamera(LBuffer)
    LCam.node().setScene(render)
    # copy lens from light and reparent
    # LCam.node().setLens(scene.lights[name]['NP'].node().getLens())
    # LCam.reparentTo(scene.lights[name]['NP'])
    return Ldepthmap, LCam

def invoke(data, fname):
    for name, obj in data['objects'].items():
        if obj['type'] == 'LAMP':
            lnp = render.find("**/" + name)
            if obj['lamp_type'] == 'POINT':
                light = PointLight(name)
                # wow render.ls() says point light inherits (PerspectiveLens, PerspectiveLens, PerspectiveLens, ...)
                # todo attenuation algorithm
                att = obj['lamp_distance']
                light.setAttenuation((att, 0, 0))
            elif obj['lamp_type'] == 'SUN':
                light = DirectionalLight(name)
                # lens = light.getLens()
                # lens.setFilmSize(obj['film_size']*2, obj['film_size']*2)
            elif obj['lamp_type'] == 'SPOT':
                light = Spotlight(name)
                lens = light.getLens()
                lens.setFov(math.degrees(obj['fov']))
            light.setColor(VBase4(*obj['lamp_color']))
            # todo energy? (multiply color)
            light.replaceNode(lnp.node())
            # lnp.setHpr(hpr)  # why doesn't this work?...
            render.setLight(lnp)

            # if obj['lamp_type'] in ['SUN', 'SPOT'] and 'shadow_caster' in obj and obj['shadow_caster']:
            #     lens.setNearFar(obj['near'], obj['far'])
            #     tex, cam = make_shadow_cam(name, obj)

        elif obj['type'] == 'CAMERA':
            # todo 'default camera'?
            ln = LensNode(name)
            cnp = render.find("**/" + name)
            if obj['camera_type'] == 'PERSP':
                lens = PerspectiveLens()
                lens.setFov(math.degrees(obj['fov']))
            elif obj['camera_type'] == 'ORTHO':
                lens = OrthographicLens()
                cnp.setScale(obj['scale'])
            lens.setNearFar(obj['near'], obj['far'])
            ln.setLens(lens)
            ln.replaceNode(cnp.node())

