from panda3d.core import *
import math, os

order = 30
target = 'object'

RESTRICT_BUFFER_SIZE = 1024


def make_shadow_cam(scene, name, obj):
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
    LBuffer = scene.show_base.graphicsEngine.makeOutput(
        scene.show_base.pipe, "offscreen buffer", -2,
        props, winprops,
        GraphicsPipe.BFRefuseWindow,
        scene.show_base.win.getGsg(), scene.show_base.win)
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
    LCam = scene.show_base.makeCamera(LBuffer)
    LCam.node().setScene(scene.root)
    # copy lens from light and reparent
    LCam.node().setLens(scene.lights[name]['NP'].node().getLens())
    LCam.reparentTo(scene.lights[name]['NP'])
    return Ldepthmap, LCam


def invoke(scene, data, action):
    for name, obj in data['objects'].items():
        if action == 'LOAD':
            # if obj['type'] == 'MESH':
            #     single_geom_mode = 'scene_mesh' in scene.data_dict['scene'].keys()
            #     if not single_geom_mode:
            #         path = os.path.join(scene.path_dict['meshes'], name)
            #         model = scene.loader.loadModel(path).find('**/+GeomNode')
            #         model.reparentTo(scene.mesh)
            #         model.setMat(Mat4(*obj['mat']))
            #         scene.meshes[name] = model
            #     else:
            #         scene.meshes[name] = scene.mesh.find('**/' + name)

            if obj['type'] == 'LAMP':
                if obj['lamp_type'] == 'POINT':
                    light = PointLight(name)
                elif obj['lamp_type'] == 'SUN':
                    light = DirectionalLight(name)
                    # lens = light.getLens()
                    # lens.setFilmSize(obj['film_size']*2, obj['film_size']*2)
                elif obj['lamp_type'] == 'SPOT':
                    light = Spotlight(name)
                    lens = light.getLens()
                    lens.setFov(math.degrees(obj['fov']))
                light.setColor(VBase4(*obj['lamp_color']))
                # todo energy? (if panda doesn't support then multiply color)
                lnp = scene.root.find("**/" + name)
                hpr = Vec3(lnp.getHpr())  # hmm, replaceNode doesn't preserve transform
                light.replaceNode(lnp.node())
                # lnp.setHpr(hpr)  # why doesn't this work?...
                light.setDirection(hpr)  # todo direction is wrong...
                scene.root.setLight(lnp)

                scene.lights[name] = {}
                scene.lights[name].update(obj)  # Copy data to use in future
                scene.lights[name]['NP'] = lnp

                if obj['lamp_type'] in ['SUN', 'SPOT'] and 'shadow_caster' in obj and obj['shadow_caster']:
                    lens.setNearFar(obj['near'], obj['far'])
                    tex, cam = make_shadow_cam(scene, name, obj)
                    # cam.setR(180)
                    scene.lights[name]['shadow_tex'] = tex
                    scene.lights[name]['shadow_cam'] = cam


            elif obj['type'] == 'CAMERA':
                ln = LensNode(name)
                # todo probably change node type instead
                cam_node = scene.root.find("**/" + name)
                cnp = cam_node.attachNewNode(ln)
                if obj['camera_type'] == 'PERSP':
                    lens = PerspectiveLens()
                    lens.setFov(math.degrees(obj['fov']))
                elif obj['camera_type'] == 'ORTHO':
                    lens = OrthographicLens()
                    cnp.setScale(obj['scale'])
                lens.setNearFar(obj['near'], obj['far'])
                ln.setLens(lens)
                scene.cameras[name] = cnp
