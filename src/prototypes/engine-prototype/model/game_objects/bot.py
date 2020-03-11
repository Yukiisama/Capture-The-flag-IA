from model.game_objects.game_objet import Game_object

RED = (197, 60, 38, 255)
BLUE = (125, 132, 174, 255)

class Bot(Game_object):
    def __init__(self, team, x=0., y=0., radius=0.):
        super().__init__(x, y)

        self._team = team
        self._angle = 0.
        self._speed = 0.
        self._color = BLUE if team == 2 else RED
        self._radius = radius


    def teleport(self, x, y):
        self._x = x
        self._y = y

    def get_coord(self):
        return (self._x, self._y)

    def get_radius(self):
        return self._radius

    def getColor(self):
        return self._color

    def get_angle(self):
        return self._angle

    def move(self, newX, newY, newAngle):
        self._x = newX
        self._y = newY
        self._angle = newAngle

    def __repr__(self):
        return "Bot({}, {}, {}, {})".format(self._team, self._x, self._y, self._radius)