from typing import Tuple, List

class ClippingTool:

    def __init__(self, minX: float, maxX: float, minY: float, maxY: float):
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY


    def clipVal(self, val, minVal, maxVal):
        return min(max(val, minVal), maxVal)

    def clipLine(self, point0: Tuple[float,float], point1: Tuple[float,float]):
        if(point0[0] < self.minX and point1[0] < self.minX) or (point0[1] < self.minY and point1[1] < self.minY) or (point0[0] > self.maxX and point1[0] > self.maxX) or (point0[1] > self.maxY and point1[1] > self.maxY):
            return (0,0), (0, 0)
        deltaX = point1[0] - point0[0]
        deltaY = point1[1] - point0[1]
        p = [-deltaX, deltaX, -deltaY, deltaY]
        q = [point0[0] - self.minX, self.maxX - point0[0], point0[1] - self.minY, self.maxY - point0[1]]
        ent = 0
        ex = 1

        for i in range(4):
            if p[i] == 0:
                if q[1] < 0:
                    return (0,0), (0,0)
            else:
                t = q[i]/p[i]
                if p[i] < 0:
                    if t > ent:
                        ent = t
                else:
                    if t < ex:
                        ex = t

        if ent > ex: return (0,0), (0,0)

        new0x = point0[0] + ent * deltaX
        new0y = point0[1] + ent * deltaY
        new1x = point0[0] + ex * deltaX
        new1y = point0[1] + ex * deltaY

        return (new0x, new0y), (new1x, new1y)

        new0 = point0
        new1 = point1

        p1 = -deltaX
        p2 = deltaX
        p3 = -deltaY
        p4 = deltaY

        q1 = point0[0] - self.minX
        q2 = self.maxX - point0[0]
        q3 = point0[1] - self.minY
        q4 = self.maxY - point0[1]

        if(deltaX == 0):
            new0 = (point0[0], self.clipVal(point0[1], self.minY, self.maxY))
            new1 = (point1[0], self.clipVal(point1[1], self.minY, self.maxY))
        elif(deltaY == 0):
            new0 = (self.clipVal(point0[0], self.minX, self.maxX), point0[1])
            new1 = (self.clipVal(point1[0], self.minX, self.maxX), point1[1])

        else:
            zeta1 = max(0, q1/p1, q3/p3) if p1 < 0 else min(1, q1, q3)
            zeta2 = min(1, q2/p2, q4/p3) if p2 < 0 else max(0, q2, q4)

            print("zeta1: ", zeta1, ", zeta2: ", zeta2)

            if(zeta1 > 0): new0 = point0[0] + zeta1 * deltaX, point0[1] + zeta1 * deltaY
            if(zeta2 < 1): new1 = point1[0] + zeta2 * p2, point1[1] + zeta2 * p4

        return new0, new1 # 0,0;50,0;50,50;0,50

    def clipPolygon(self, points: List[Tuple[float,float]]):
        newLines = []
        for i in range(0, len(points)):
            if(i < len(points) - 1):
                n1, n2 = self.clipLine(points[i], points[i + 1])
            else:
                n1, n2 = self.clipLine(points[i], points[0])

            if not (n1[0] == 0 and n1[1] == 0 and n2[0] == 0 and n2[1] == 0):
                if not(self.contains(newLines, n1)):
                    newLines.append(n1)
                    # print("add: ", n1)

                if not (self.contains(newLines, n2)):
                    # print(newLines)
                    newLines.append(n2)
                    # print("add: ", n1, "_")

        return newLines

    def outOfBounds(self, point: Tuple[float,float]):
        return point[0] < self.maxX and point[0] > self.minX and point[1] < self.maxY and point[1] > self.minY

    def region(self, point: Tuple[float,float]):
        top = 8 if point[1] > self.maxY else 0
        bottom = 4 if point[1] < self.minY else 0
        right = 2 if point[0] > self.maxX else 0
        left = 1 if point[0] < self.minX else 0
        return top | bottom | right | left

    def contains(self, points: List[Tuple[float, float]], point: Tuple[float, float]):
        length = len(points)
        for i in range(0, length):
            if(points[i][0] == point[0] and points[i][1] == point[1]):
                # print("true", points[i], point)
                return True

        return False
