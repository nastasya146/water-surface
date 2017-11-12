import numpy as np
from vispy import gloo
from vispy import app

class Surface(object):
    # Конструктор получает размер генерируемого массива.
    # Также конструктор Генерируется параметры нескольких плоских волн.
    def __init__(self, size=(100,100), nwave=5):
        self._size=size
        self._wave_vector=5*np.random.randn(nwave,2) # 5*2 матрица, нормальное распределение
        self._angular_frequency=np.random.randn(nwave) # 5 вектор, нормальное распределение
        self._phase=2*np.pi*np.random.rand(nwave) # вектор от 0 до 2pi
        self._amplitude=np.random.rand(nwave)/nwave # Зачем делить на 5???
    # Эта функция возвращает xy координаты точек.
    # Точки образуют прямоугольную решетку в квадрате [0,1]x[0,1]
    def position(self):
        xy=np.empty(self._size+(2,),dtype=np.float32) # вектор (100, 100, 2), пустой
        xy[:,:,0]=np.linspace(-1,1,self._size[0])[:,None]
        """ 
      [[[-1. ,  0. ],
        [-1. ,  0. ],
        [-1. ,  0. ],
        [-1. ,  0. ],
        [-1. ,  0. ]],

       [[-0.5,  0. ],
        [-0.5,  0. ],
        [-0.5,  0. ],
        [-0.5,  0. ],
        [-0.5,  0. ]],

       [[ 0. ,  0. ],
        [ 0. ,  0. ],
        [ 0. ,  0. ],
        [ 0. ,  0. ],
        [ 0. ,  0. ]],

       [[ 0.5,  0. ],
        [ 0.5,  0. ],
        [ 0.5,  0. ],
        [ 0.5,  0. ],
        [ 0.5,  0. ]],

       [[ 1. ,  0. ],
        [ 1. ,  0. ],
        [ 1. ,  0. ],
        [ 1. ,  0. ],
        [ 1. ,  0. ]]]"""
        xy[:,:,1]=np.linspace(-1,1,self._size[1])[None,:]
        """
      [[[-1. , -1. ],
        [-1. , -0.5],
        [-1. ,  0. ],
        [-1. ,  0.5],
        [-1. ,  1. ]],

       [[-0.5, -1. ],
        [-0.5, -0.5],
        [-0.5,  0. ],
        [-0.5,  0.5],
        [-0.5,  1. ]],

       [[ 0. , -1. ],
        [ 0. , -0.5],
        [ 0. ,  0. ],
        [ 0. ,  0.5],
        [ 0. ,  1. ]],

       [[ 0.5, -1. ],
        [ 0.5, -0.5],
        [ 0.5,  0. ],
        [ 0.5,  0.5],
        [ 0.5,  1. ]],

       [[ 1. , -1. ],
        [ 1. , -0.5],
        [ 1. ,  0. ],
        [ 1. ,  0.5],
        [ 1. ,  1. ]]]"""
        return xy
    # Эта функция возвращает массив высот водной глади в момент времени t.
    # Диапазон изменения высоты от -1 до 1, значение 0 отвечает равновесному положению
    def height(self, t):
        x=np.linspace(-1,1,self._size[0])[:,None]
        y=np.linspace(-1,1,self._size[1])[None,:]
        z=np.zeros(self._size,dtype=np.float32)
        for n in range(self._amplitude.shape[0]): # magic
            z[:,:] += self._amplitude[n] * np.cos(self._phase[n] +
             x*self._wave_vector[n,0] + y*self._wave_vector[n,1] +
                t*self._angular_frequency[n])
        return z
    def wireframe(self):
        # Возвращаем координаты всех вершин, кроме крайнего правого столбца
        left=np.indices((self._size[0]-1,self._size[1]))
        # Пересчитываем в координаты всех точек, кроме крайнего левого столбца
        right=left+np.array([1,0])[:,None,None]
        # Преобразуем массив точек в список (одномерный массив)
        left_r=left.reshape((2,-1))
        right_r=right.reshape((2,-1))
        # Заменяем многомерные индексы линейными индексами
        left_l=np.ravel_multi_index(left_r, self._size)
        right_l=np.ravel_multi_index(right_r, self._size)
        # собираем массив пар точек
        horizontal=np.concatenate((left_l[...,None],right_l[...,None]),axis=-1)
        # делаем то же самое для вертикальных отрезков
        bottom=np.indices((self._size[0],self._size[1]-1))
        top=bottom+np.array([0,1])[:,None,None]
        bottom_r=bottom.reshape((2,-1))
        top_r=top.reshape((2,-1))
        bottom_l=np.ravel_multi_index(bottom_r, self._size)
        top_l=np.ravel_multi_index(top_r, self._size)
        vertical=np.concatenate((bottom_l[...,None],top_l[...,None]),axis=-1)
        return np.concatenate((horizontal,vertical),axis=0).astype(np.uint32)

vert = ("""
#version 120
attribute vec2 a_position;
"""
# Добавим еще один атрибут, который будет хранит высоту точки.
# Считаем, что высота изменяться в диапазоне [-1,1],
# -1 отвечает нижнему (дальнему от наблюдателя) положению поверхности
# +1 отвечает врехнему (ближнему к наблюдателю) положению поверхности.
"""
attribute float a_height;
void main (void) {
"""
    # Собираем положение точки в пространстве из xy координат и высоты.
    # Отображаем диапазон высот [-1,1] в интервал [1,0],
    # так что самые дальние точки получают координату 1, 
    # будут иметь координату ноль.
"""
    float z=(1-a_height)*0.5;
    gl_Position = vec4(a_position.xy,z,z);
"""
    # После работы шейдера вершин OpenGL отбросит все точке,
    # с координатами, выпадающими из области -1<=x,y<=1, 0<=z<=1.
    # Затем x и y координаты будут поделены на 
    # координату t (последняя в gl_Position),
    # что создает перспективу: предметы ближе кажутся больше.
"""
}
""")

frag = """
#version 120
void main() {
    gl_FragColor = vec4(0.5,0.5,1,1);
}
"""

class Canvas(app.Canvas):

    def __init__(self):
        app.Canvas.__init__(self, size=(600, 600), title="Water surface simulator 2")
        gloo.set_state(clear_color=(0,0,0,1), depth_test=False, blend=False)
        self.program = gloo.Program(vert, frag)
        # Создаем обьект, который будет давать нам состояние поверхности
        self.surface=Surface((15,15))
        # xy координаты точек сразу передаем шейдеру, они не будут изменятся со временем
        self.program["a_position"]=self.surface.position()        
        # Сохраним вершины, которые нужно соединить отрезками, в графическую память.
        self.segments=gloo.IndexBuffer(self.surface.wireframe())
        # Устанавливаем начальное время симуляции
        self.t=0
        # Закускаем таймер, который будет вызывать метод on_timer для
        # приращения времени симуляции
        self._timer = app.Timer('auto', connect=self.on_timer, start=True)
        self.activate_zoom()
        self.show()

    def activate_zoom(self):
        self.width, self.height = self.size
        gloo.set_viewport(0, 0, *self.physical_size)

    def on_draw(self, event):
        gloo.clear()
        # Читаем положение высот для текущего времени
        self.program["a_height"]=self.surface.height(self.t)
        # Теперь мы отресовываем отрезки, поэтому аргумент "lines",
        # и теперь нужно передать индексы вершин self.segments, которые нужно соединить.
        self.program.draw('lines', self.segments)
        # В результате видим сеть из вертикальных и горизонтальных отрезков.
        # Интересно, что нам не пришлось никаких изменения в шейдеры.

    # Метод, вызываемый таймером.
    # Используем для создания анимации.
    def on_timer(self, event):
        # Делаем приращение времени
        self.t+=0.01
        # Сообщаем OpenGL, что нужно обновить изображение,
        # в результате будет вызвано on_draw.
        self.update()        

    # Обработчик изменения размера окна пользователем.
    # Нужно передать данные о новом размере окна в OpenGL,
    # в противном случае OpenGL будет рисовать только на части окна.
    def on_resize(self, event):
        self.activate_zoom()

if __name__ == '__main__':
    c = Canvas()
    app.run()