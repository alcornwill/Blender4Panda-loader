from sys import argv
import panda_scene_loader
from direct.showbase.ShowBase import ShowBase

class MyApp(ShowBase):
    def __init__(self):
        ShowBase.__init__(self)

if __name__ == '__main__':
    path = argv[1]
    app = MyApp()
    panda_scene_loader.load(path)
    render.ls()
    app.run()
