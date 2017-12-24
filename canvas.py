# -*- coding: utf-8 -*-

import numpy as np
from vispy import gloo, app, io
from vertex import vertex
from fragment_triangle import fragment_triangle
from fragment_point import fragment_point

from runge_kutta import RungeKutta
from euler import Euler
from verlet import Verlet

class Canvas(app.Canvas):
    def __init__(self, surface, bed, size=(600, 600), 
            sky_img_path="water-surface/fluffy_clouds.png",
            bed_img_path="water-surface/seabed.png",
            depth_img_path="water-surface/depth.png"):
        app.Canvas.__init__(self, size=size,
                            title="Water surface simulator")
        # запрещаем текст глубины depth_test (все точки будут отрисовываться),
        # запрещает смещивание цветов blend - цвет пикселя на экране равен gl_fragColor.
        gloo.set_state(clear_color=(0, 0, 0, 1), depth_test=True, blend=True)
        self.program = gloo.Program(vertex, fragment_triangle)
        self.program_point = gloo.Program(vertex, fragment_point)
        
        self.h_description = None
        self.integrator = RungeKutta(method="blyamba", borders=True)
        #self.integrator = Euler(method="drop", borders=True)
        #self.integrator = Verlet(method="peak", borders=True)

        self.surface = surface

        self.time = 0
        self.bed = bed
        self.sky_img = io.read_png(sky_img_path)
        self.bed_img = io.read_png(bed_img_path)
        io.write_png(depth_img_path, self.bed.depth())
        self.depth_img = io.read_png(depth_img_path)
        
        # xy координаты точек сразу передаем шейдеру, они не будут изменятся со временем
        self.program["a_position"] = self.surface.position()
        self.program_point["a_position"] = self.surface.position()

        self.program['u_sky_texture'] = gloo.Texture2D(
            self.sky_img, wrapping='repeat', interpolation='linear')
        self.program['u_bed_texture'] = gloo.Texture2D(
            self.bed_img, wrapping='repeat', interpolation='linear')
        
        self.program['u_bed_depth_texture'] = gloo.Texture2D(
            self.depth_img, wrapping='repeat', interpolation='linear')
            
        self.program_point["u_eye_height"] = self.program["u_eye_height"] = 3
        self.program["u_alpha"] = 0.3
        self.program["u_bed_depth"] = -0.5

        self.program["u_sun_direction"] = self.normalize([0, 1, 0.1])
        self.program["u_sun_diffused_color"] = [1, 0.8, 1]
        self.program["u_sun_reflected_color"] = [1, 0.8, 0.6]

        self.triangles = gloo.IndexBuffer(self.surface.triangulation())

        # Set up GUI
        self.camera = np.array([0, 0, 1])
        self.up = np.array([0, 1, 0])
        self.set_camera()
        self.are_points_visible = False
        self.drag_start = None
        self.diffused_flag = True
        self.reflected_flag = True
        self.bed_flag = True
        self.depth_flag = True
        self.sky_flag = True
        self.stop_flag = False
        self.apply_flags()

        # Run
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.activate_zoom()
        self.show()

    def apply_flags(self):
        self.program["u_diffused_mult"] = 0.5 if self.diffused_flag else 0
        self.program["u_reflected_mult"] = 1.0 if self.reflected_flag else 0
        self.program["u_bed_mult"] = 1 if self.bed_flag else 0
        self.program["u_depth_mult"] = 1 if self.depth_flag else 0
        self.program["u_sky_mult"] = 1 if self.sky_flag else 0

    def set_camera(self):
        rotation = np.zeros((4, 4), dtype=np.float32)
        rotation[3, 3] = 1
        rotation[0, :3] = np.cross(self.up, self.camera)
        rotation[1, :3] = self.up
        rotation[2, :3] = self.camera
        world_view = rotation
        self.program['u_world_view'] = world_view.T
        self.program_point['u_world_view'] = world_view.T

    def rotate_camera(self, shift):
        right = np.cross(self.up, self.camera)
        new_camera = self.camera - right * shift[0] + self.up * shift[1]
        new_up = self.up - self.camera * shift[0]
        self.camera = self.normalize(new_camera)
        self.up = self.normalize(new_up)
        self.up = np.cross(self.camera, np.cross(self.up, self.camera))

    def activate_zoom(self):
        """
            Эта функция вызывается при установке размера окна
            1.Читаем размер окна
            2.Передаем размер окна в OpenGL
        """
        self.width, self.height = self.size
        gloo.set_viewport(0, 0, *self.physical_size)

    def on_draw(self, event):
        # Все пиксели устанавливаются в значение clear_color,
        gloo.clear()
        # Читаем положение высот для текущего времени
        self.h_description = self.integrator.get_heights(self.h_description)
        height = self.h_description[0]
        normal = self.integrator.get_normal(height)
        self.program["a_height"] = height
        self.program["a_normal"] = normal
        gloo.set_state(depth_test=True)
        self.program.draw('triangles', self.triangles)
        if self.are_points_visible:
            self.program_point["a_height"] = height
            gloo.set_state(depth_test=False)
            self.program_point.draw('points')

    def on_timer(self, event):
        if not self.stop_flag:
            self.time += 0.01
            # calls on_draw
            self.update()

    def on_resize(self, event):
        self.activate_zoom()

    def on_key_press(self, event):
        if event.key == 'Escape':
            self.close()
        elif event.key == ' ':
            self.are_points_visible = not self.are_points_visible
            print("Show lattice vertices:", self.are_points_visible)
        elif event.key == '1':
            self.diffused_flag = not self.diffused_flag
            print("Show sun diffused light:", self.diffused_flag)
            self.apply_flags()
        elif event.key == '2':
            self.bed_flag = not self.bed_flag
            print("Show refracted image of seabed:", self.bed_flag)
            self.apply_flags()
        elif event.key == '3':
            self.depth_flag = not self.depth_flag
            print("Show ambient light in water:", self.depth_flag)
            self.apply_flags()
        elif event.key == '4':
            self.sky_flag = not self.sky_flag
            print("Show reflected image of sky:", self.sky_flag)
            self.apply_flags()
        elif event.key == '5':
            self.reflected_flag = not self.reflected_flag
            print("Show reflected image of sun:", self.reflected_flag)
            self.apply_flags()
        elif event.key == 'Up':
            self.program["u_bed_depth"] += 0.1
        elif event.key == 'Down':
            self.program["u_bed_depth"] -= 0.1

    def screen_to_gl_coordinates(self, pos):
        return 2 * np.array(pos) / np.array(self.size) - 1

    def on_mouse_press(self, event):
        self.drag_start = self.screen_to_gl_coordinates(event.pos)

    def on_mouse_move(self, event):
        if not self.drag_start is None:
            pos = self.screen_to_gl_coordinates(event.pos)
            self.rotate_camera(pos - self.drag_start)
            self.drag_start = pos
            self.set_camera()
            self.update()

    def on_mouse_release(self, event):
        self.drag_start = None

    def normalize(self, vec):
        vec = np.asarray(vec, dtype=np.float32)
        return vec / np.sqrt(np.sum(vec * vec, axis=-1))[..., None]
