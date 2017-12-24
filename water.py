
from vispy import app
from surface import PlaneWaves, CircularWaves
from bed import BedLiner, BedCircular
from canvas import Canvas

if __name__ == '__main__':
    c = Canvas(PlaneWaves(), BedLiner())
    # c = Canvas(CircularWaves(), BedLiner(), new_waves_class=CircularWaves)
    # c = Canvas(CircularWaves(), BedLiner())
    # c = Canvas(PlaneWaves(), BedCircular())
    app.run()
