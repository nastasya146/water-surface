import numpy as np
from generator import Generator


class Base:
    def __init__(self, method, v=100, delta=1, sigma=0.1, size=(50, 50), 
            max_height=0.4, min_height=0.2, borders=False):
        self.method = method
        self.v = v
        self.delta = delta
        self.sigma = sigma
        self.size = size
        self.max_height = max_height
        self.min_height = min_height
        self.borders = borders
        self.generator = Generator(size)

        self.methods = {
            "drop": self.generator.drop,
            "blyamba": self.generator.blyamba
        }

        self.indices = Base.get_indices(size)

    def init(self, max_height=0.4, min_height=0.2, part=4):
        params = {
            "max_height": max_height,
            "min_height": min_height,
            "part": part
        }
        return self.methods[self.method](params)

    def f(self, x):
        """
            f([h, v]) = [v, h'']
            h'' = Ldh
        """
        return np.array([x[1], self.derivative(x[0])])

    def derivative(self, heights):
        der_heights = np.zeros(self.size, dtype=np.float32)

        if not self.borders:
            der_heights += (
                heights[self.indices["left"][0], self.indices["left"][1]] +
                heights[self.indices["right"][0], self.indices["right"][1]] +
                heights[self.indices["up"][0], self.indices["up"][1]] +
                heights[self.indices["down"][0], self.indices["down"][1]] -
                4 * heights[self.indices["this"][0], self.indices["this"][1]])

        else:
            der_heights[1:-1, 1:-1] += (heights[2:, 1:-1] 
                + heights[0:-2, 1:-1] 
                + heights[1:-1, 2:] 
                + heights[1:-1, 0:-2] 
                - 4 * heights[1:-1, 1:-1])

        return ((self.v ** 2) * (self.sigma ** 2) / (self.delta ** 2)) * der_heights

    def get_heights(self, h_desc):
        pass

    def get_normal(self, heights):
        normal = np.zeros((self.size[0], self.size[1], 2), dtype=np.float32)
        for i in range(0, self.size[0]):
            for j in range(0, self.size[1]):
                left = heights[i][(j - 1 + self.size[1]) % self.size[1]]
                right = heights[i][(j + 1) % self.size[1]]
                up = heights[(i - 1 + self.size[0]) % self.size[0]][j]
                down = heights[(i + 1) % self.size[0]][j]

                normal[i][j][0] = (left + right) / (2 * self.delta)
                normal[i][j][1] = (up + down) / (2 * self.delta)
        return normal

    @staticmethod
    def get_indices(size):
        left = np.indices(size, dtype=np.int)
        left[0] = (left[0] + 1) % size[0]

        right = np.indices(size, dtype=np.int)
        right[0] = (right[0] - 1 + size[0]) % size[0]

        down = np.indices(size, dtype=np.int)
        down[1] = (down[1] + 1) % size[1]

        up = np.indices(size, dtype=np.int)
        up[1] = (up[1] - 1 + size[1]) % size[1]

        this = np.indices(size, dtype=np.int)

        return {
            "left": left,
            "right": right,
            "up": up,
            "down": down,
            "this": this
        }