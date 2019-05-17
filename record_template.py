import cocos
import time
import json, math
from time import strftime
import cocos.actions.instant_actions
from cocos import sprite
from cocos import draw
import cocos.menu
from cocos.director import director
import cocos.custom_clocks
import pyglet
import sys
from pyglet import gl

class BackgroundLayer(cocos.layer.Layer):
    def __init__(self):
        super(BackgroundLayer, self).__init__()
        self.img = pyglet.resource.image('homer1original.jpg')
        w, h = director.get_window_size()
        iw, ih = self.img.width, self.img.height
        self.lx = w/2 - iw/2
        self.ly = h/2 - ih/2 

    def draw (self):
        self.img.blit(self.lx, self.ly)


class RecordLayer(cocos.layer.ColorLayer):
    is_event_handler = True

    def __init__(self, filename):
        super(RecordLayer, self).__init__(255, 255, 255, 0)
        self.cursor = sprite.Sprite("green-circle.png")
        self.add(self.cursor, z=1)
        w, h = director.get_window_size()
        self.centerx, self.centery = w/2, h/2 
        self.label = cocos.text.Label('Press Space to record, Esc to end',
                                      color=(255, 20, 0, 250),
                                      font_name='Times New Roman',
                                      font_size=32,
                                      anchor_x='center', anchor_y='center')
        self.label.position = self.centerx, self.centery
        self.add(self.label)
        self.filename = filename
        self.clock = pyglet.clock.get_default()
        self.mode = "pause"
        self.clock.schedule(self.update_screen)
        self.t1 = time.perf_counter()
        self.cursxs = []
        self.cursys = []
        self.cx = 0
        self.cy = 0
        self.reset()

    def recorder(self, dt):
        t = time.perf_counter()
        while(((t - self.t1) * 1000) < 4.99):
            t = time.perf_counter()
        self.clock.schedule_once(self.recorder, 0.004)
        self.t1 = t
        self.cursxs.append(self.cx)
        self.cursys.append(self.cy)
        self.ts.append(t)
        self.counter = self.counter + 1

    def update_pos(self, x, y):
        self.cx = x
        self.cy = y

    def on_mouse_press(self, x, y, buttons, modifiers):
        self.update_pos(x, y)

    def on_mouse_drag(self, x, y, dx, dy, buttons, modifiers):
        self.update_pos(x, y)

    def on_mouse_motion(self, x, y, dx, dy):
        self.update_pos(x, y)

    def reset(self):
        self.clock.unschedule(self.recorder)
        self.clock.unschedule(self.save_n_exit)
        self.cursxs = []
        self.cursys = []
        self.cx = 0
        self.cy = 0

        self.ts = []
        self.t1 = time.perf_counter()
        self.counter = 0
        self.label.position = self.centerx, 200
   
    def start_run(self):
        self.clock.schedule(self.update_screen)
        self.label.position = -100, -100
        self.clock.schedule_once(self.recorder, 0.004)

    def update_screen(self, dt):
        self.cursor.position = self.cx, self.cy

    def on_key_press(self, key, modifiers):
        if (key == pyglet.window.key.SPACE):
            if self.mode == 'pause':
                self.mode = 'running'
                self.reset()
                self.start_run()
        if (key == pyglet.window.key.ESCAPE):
            self.save_n_exit()

    def save_n_exit(self):
        tstamp = strftime(" %Y-%m-%d %H-%M-%S")
        fnout = self.filename + tstamp + ".txt"
        file = open(fnout, "w")
        cut_start = 0
        cut_end = 0
        cursor_xs = self.cursxs
        cursor_ys = self.cursys
        ts = self.ts

        ts = [x - ts[0] for x in ts]

        for i in range(len(cursor_xs)):
            file.write(f"{ts[i]} {cursor_xs[i]} {cursor_ys[i]} \n")

        file.close()
        director.scene.end()


def main():
    filename = "homer trace"
    config = pyglet.gl.Config(sample_buffers=1, samples=4)
    w = director.init(vsync=False, fullscreen=True, config=config)
    w.set_mouse_visible(False)
    
    main_scene = cocos.scene.Scene()
    background = BackgroundLayer()
    
    rec = RecordLayer(filename)
    
    main_scene.add(background, z=0)
    main_scene.add(rec, z = 1)
   

    director.run(main_scene)


main()
