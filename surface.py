# -*- coding: utf-8 -*-

import numpy as np

class PlaneWaves(object):
    def __init__(self, size=(50,50), flat_wave_size=10, max_height=0.2):
        """
            Конструктор получает размер генерируемого массива.
            Также конструктор Генерируется параметры нескольких плоских волн.
        """
        self._size = size
        self._wave_vector = 5 * np.random.randn(flat_wave_size, 2)
        self._angular_frequency = np.random.randn(flat_wave_size)
        self._phase = 2 * np.pi * np.random.rand(flat_wave_size)
        self._amplitude = max_height * (1 + np.random.rand(flat_wave_size)) / 2 / flat_wave_size
        self._scale = 0.8
        self.t = 0

    def propagate(self, time_shift):
        self.t += time_shift

    def position(self):
        """
            Эта функция возвращает xy координаты точек.
            Точки образуют прямоугольную решетку в квадрате [0,1]x[0,1]
        """
        xy=np.empty(self._size + (2,), dtype=np.float32)
        xy[:, :, 0]=np.linspace(-1, 1, self._size[0])[:, None]
        xy[:, :, 1]=np.linspace(-1, 1, self._size[1])[None, :]
        return self._scale * xy

    def coords(self):
      # N x 1 array
      x = np.linspace(-1, 1, self._size[0])[:, np.newaxis]
      # 1 x N array
      y = np.linspace(-1, 1, self._size[1])[np.newaxis, :]
      return x, y

    def empty_arr(self, shape):
      # each cell equals 0
      return np.zeros(shape, dtype=np.float32)

    def height(self, time=0):
        x = self._scale * np.linspace(-1, 1, self._size[0])[:, None]
        y = self._scale * np.linspace(-1, 1, self._size[1])[None, :]
        z = np.zeros(self._size, dtype=np.float32)
        grad = np.zeros(self._size + (2,), dtype=np.float32)
        for n in range(self._amplitude.shape[0]):
            arg = (self._phase[n]
                   + x * self._wave_vector[n, 0]
                   + y * self._wave_vector[n, 1]
                   + self.t * self._angular_frequency[n]
                   )
            z[:, :] += self._amplitude[n] * np.cos(arg)
            dcos = -self._amplitude[n] * np.sin(arg)
            grad[:, :, 0] += self._wave_vector[n, 0] * dcos
            grad[:, :, 1] += self._wave_vector[n, 1] * dcos
        return z

    def normal(self, time=0):
            x = self._scale * np.linspace(-1, 1, self._size[0])[:, None]
            y = self._scale * np.linspace(-1, 1, self._size[1])[None, :]
            z = np.zeros(self._size, dtype=np.float32)
            grad = np.zeros(self._size + (2,), dtype=np.float32)
            for n in range(self._amplitude.shape[0]):
                arg = (self._phase[n]
                       + x * self._wave_vector[n, 0]
                       + y * self._wave_vector[n, 1]
                       + self.t * self._angular_frequency[n]
                       )
                z[:, :] += self._amplitude[n] * np.cos(arg)
                dcos = -self._amplitude[n] * np.sin(arg)
                grad[:, :, 0] += self._wave_vector[n, 0] * dcos
                grad[:, :, 1] += self._wave_vector[n, 1] * dcos
            return grad

     # Возвращает массив индесов вершин треугольников.
    def triangulation(self):
        # Решетка состоит из прямоугольников с вершинами
        # A (левая нижняя), B(правая нижняя), С(правая верхняя), D(левая верхняя).
        # Посчитаем индексы всех точек A,B,C,D для каждого из прямоугольников.
        a = np.indices((self._size[0] - 1, self._size[1] - 1))
        b = a + np.array([1, 0])[:, None, None]
        c = a + np.array([1, 1])[:, None, None]
        d = a + np.array([0, 1])[:, None, None]
        # Преобразуем массив индексов в список (одномерный массив)
        a_r = a.reshape((2, -1))
        b_r = b.reshape((2, -1))
        c_r = c.reshape((2, -1))
        d_r = d.reshape((2, -1))
        # Заменяем многомерные индексы линейными индексами
        a_l = np.ravel_multi_index(a_r, self._size)
        b_l = np.ravel_multi_index(b_r, self._size)
        c_l = np.ravel_multi_index(c_r, self._size)
        d_l = np.ravel_multi_index(d_r, self._size)
        # Собираем массив индексов вершин треугольников ABC, ACD
        abc = np.concatenate((a_l[..., None], b_l[..., None],c_l [...,None]), axis=-1)
        acd = np.concatenate((a_l[..., None], c_l[..., None],d_l [...,None]), axis=-1)
        # Обьединяем треугольники ABC и ACD для всех прямоугольников
        return np.concatenate((abc, acd), axis=0).astype(np.uint32)


class CircularWaves(PlaneWaves):
    def __init__(self, size=(50, 50), max_height=0.02, wave_length=0.3, center=(0., 0.), speed=3):
        self._size = size
        self._amplitude = max_height
        self._omega = 2 * np.pi / wave_length
        self._center = np.asarray(center, dtype=np.float32)
        self._speed = speed
        self.t = 0
        self._scale = 1.0
        self._amplitude_shift = 0.000005
        self._is_dead = False

    def coords(self):
        # N x 1 array
        x = np.linspace(-1, 1, self._size[0])[:, np.newaxis]
        # 1 x N array
        y = np.linspace(-1, 1, self._size[1])[np.newaxis, :]

        return x, y

    def empty_arr(self, shape):
        # each cell equals 0
        return np.zeros(shape, dtype=np.float32)


    def height(self, time=0):
        x, y = self.coords()
        height = self.empty_arr(self._size)
        d = np.sqrt((x - self._center[0]) ** 2 + (y - self._center[1]) ** 2)
        angle = self._omega * d - time * self._speed
        height[:, :] = self._amplitude * np.cos(angle)
        return height

    def normal(self, time=0):
        x, y = self.coords()
        shape = (self._size[0], self._size[1], 2)
        grad = np.zeros(shape, dtype=np.float32)
        d = np.sqrt((x - self._center[0]) ** 2 + (y - self._center[1]) ** 2)
        angle = self._omega * d - time * self._speed
        delta_cos = -self._amplitude * self._omega * np.sin(angle)
        grad[:, :, 0] += (x - self._center[0]) * delta_cos / d
        grad[:, :, 1] += (y - self._center[1]) * delta_cos / d
        return grad

    def propagate(self, time_shift):
        self.t += time_shift
        if self._amplitude - self._amplitude_shift > 0:
            self._amplitude = self._amplitude - self._amplitude_shift
        else:
            self._is_dead = True

    def is_dead(self):
        return self._is_dead
