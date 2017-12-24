
from vispy import app
from surface import PlaneWaves, CircularWaves
from bed import BedLiner, BedCircular
from canvas import Canvas

if __name__ == '__main__':
    c = Canvas(CircularWaves(), BedLiner())
    app.run()
