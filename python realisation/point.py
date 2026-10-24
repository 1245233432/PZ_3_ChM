class Point:
    def __init__(self, x=0.0, y=0.0, z=0.0):
        self._x = float(x)
        self._y = float(y)
        self._z = float(z)

    def x(self):
        return self._x

    def y(self):
        return self._y

    def z(self):
        return self._z

    def __repr__(self):
        return (
            f"Point(x={self._x}, "
            f"y={self._y}, z={self._z})"
        )