# -*- coding: utf-8 -*-

import numpy as np
from surface import CircularWaves


class BedLiner(object):
    def __init__(self, size=(400, 400), max_depth=1.0, min_depth = 1.0):
        """
            Конструктор получает размер генерируемого массива.
            Также конструктор Генерируется параметры нескольких плоских волн.
        """
        self._size = size
        self._max_depth = max_depth
        self._min_depth = min_depth

    def depth(self):
        """
            Эта функция возвращает массив высот водной глади в момент времени t.
            Диапазон изменения высоты от -1 до 1, значение 0 отвечает равновесному положению
        """
        x = np.linspace(self._min_depth, self._max_depth,
                        self._size[0])
        y = np.linspace(self._min_depth, self._max_depth,
                        self._size[1])
        z = np.linspace(1, 1, 3)
        d = np.zeros(self._size + (4, ), dtype=np.uint8)

        for x_idx, x_value in enumerate(x):
            for y_idx, y_value in enumerate(y):
                for z_idx, z_value in enumerate(z):
                    d[x_idx, y_idx, z_idx] = x_value * y_value
                d[x_idx, y_idx, 3] = 255
        return d

class BedCircular():
    def __init__(self, size=(100, 100), max_depth=0.2, min_depth=0.1):
        """
            Конструктор получает размер генерируемого массива.
            Также конструктор Генерируется параметры нескольких плоских волн.
        """
        self._size = size
        self._max_depth = max_depth
        self._min_depth = min_depth

    def depth(self):
        """
            Эта функция возвращает массив высот водной глади в момент времени t.
            Диапазон изменения высоты от -1 до 1, значение 0 отвечает равновесному положению
        """
        wave = CircularWaves(self._size, self._max_depth, wave_length=0.6)
        d = wave.height()
        grad = wave.normal()
        return d + self._min_depth
