from base import Base
import numpy as np


class Euler(Base):
    def __init__(self, method, v=200, delta=1, sigma=0.02, size=(50, 50), 
            max_height=0.4, min_height=0.2, borders=False):
        super().__init__(method, v, delta, sigma, size, max_height, min_height, borders)

    def euler(self, f, x, h):
        """
            y(x+h) = y(x) + h * f(x)
            x is vector [h(t), v(t)]
        """
        return x + h * f(x)

    def get_heights(self, h_desc):
        # first time
        if h_desc is None:
            h = self.init()
            h_der = np.zeros(self.size, dtype=np.float32)
            return np.array([h, h_der])
        # other times
        else:
            return self.euler(self.f, h_desc, self.sigma)
