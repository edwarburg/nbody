import math

def _magnitude2(vector):
    x, y = vector
    return math.sqrt(x * x + y * y)

def _vec_minus2(v1, v2):
    x1, y1 = v1
    x2, y2 = v2
    return x1 - x2, y1 - y2

class World(object):
    G = 6.67398e-11
    EPS = 1
    EPS2 = EPS * EPS

    def __init__(self, maxx=float(100), maxy=float(100)):
        self.maxx, self.maxy = float(maxx), float(maxy)
        self.masses = []

    def add_mass(self, mass):
        self.masses.append(mass)

    def clear_masses(self):
        self.masses = []

    def tick(self, dt=1):
        for mass in self.masses:
            mass.tick(dt)

        if len(self.masses) >= 2:
            for i in range(len(self.masses)):
                for j in range(i + 1, len(self.masses)):
                        fx, fy = self.interact(self.masses[i], self.masses[j])
                        self.masses[i].apply_force(fx, fy)
                        self.masses[j].apply_force(-fx, -fy)
                
    def interact(self, a, b):
        rab = _vec_minus2((b.px, b.py), (a.px, a.py))
        if rab[0] == 0 and rab[1] == 0:
            return (0, 0)
        force = World.G * (a.m * b.m) / ((rab[0] * rab[0] + rab[1] * rab[1] + World.EPS2) ** 1.5)
        return force * rab[0], force * rab[1]

class Mass(object):
    def __init__(self, mass=1, radius=1, position=(0, 0), velocity=(0, 0), acceleration=(0, 0)):
        self.m = float(mass)
        self.r = float(radius)
        self.px, self.py = float(position[0]), float(position[1])
        self.vx, self.vy = float(velocity[0]), float(velocity[1])
        self.ax, self.ay = float(acceleration[0]), float(acceleration[1])

    def tick(self, dt=1):
        self.px += self.vx * float(dt)
        self.py += self.vy * float(dt)

        self.vx += self.ax * float(dt)
        self.vy += self.ay * float(dt)

        self.ax, self.ay = 0.0, 0.0

    def apply_force(self, fx, fy):
        self.ax += float(fx / self.m)
        self.ay += float(fy / self.m)

    def distance_to(self, mass):
        vector = _vec_minus2(self, mass)
        return _magnitude2(vector)

    def __repr__(self):
        return "Mass(m={0}, r={1}, p={2}, v={3}, a={4})".format(self.m, self.r, (self.px, self.py), (self.vx, self.vy), (self.ax, self.ay))
