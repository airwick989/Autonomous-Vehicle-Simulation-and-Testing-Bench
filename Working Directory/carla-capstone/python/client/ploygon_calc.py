class XYZPoint:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    def __sub__(self, other):
        '''Define subtraction of points''' ''
        return XYZPoint(
            self.x - other.x,
            self.y - other.y,
            self.z - other.z,
        )

    def __str__(self):
        '''What to return when trying to print object''' ''
        return str(self.x) + ", " + str(self.y) + ", " + str(self.z)

    def __repr__(self):
        return str(self.x) + ", " + str(self.y) + ", " + str(self.z)

    def dot(self, other):
        '''Return the dot product of this and other point''' ''
        return ((self.x * other.x) + (self.y * other.y) + (self.z * other.z))


class Cuboid:
    def __init__(self, p1, p2, p3, p4, p5, p6, p7, p8):
        self.p1 = p1  # p2,p4 and p5 should be the perpendicular edges to p1
        self.p2 = p2
        self.p3 = p3
        self.p4 = p4
        self.p5 = p5
        self.p6 = p6
        self.p7 = p7
        self.p8 = p8

    def point_is_within(self, P):
        x = [
            self.p1.x, self.p2.x, self.p3.x, self.p4.x, self.p5.x, self.p6.x,
            self.p7.x, self.p8.x
        ]
        y = [
            self.p1.y, self.p2.y, self.p3.y, self.p4.y, self.p5.y, self.p6.y,
            self.p7.y, self.p8.y
        ]
        z = [
            self.p1.z, self.p2.z, self.p3.z, self.p4.z, self.p5.z, self.p6.z,
            self.p7.z, self.p8.z
        ]

        if ((min(x) <= P.x <= max(x)) and (min(y) <= P.y <= max(y))
                and (min(z) <= P.z <= max(z))):
            return True
        else:
            return False
