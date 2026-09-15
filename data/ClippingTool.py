from enum import Enum
from tkinter.constants import RIGHT
from typing import Tuple, List


class Directions(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4
    NONE = 0

class ClippingTool:
    def __init__(self, minX: float, maxX: float, minY: float, maxY: float):
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY


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
                if q[i] < 0:
                    return (0,0), (0,0)
            else:
                t = q[i]/p[i]
                if p[i] < 0:
                    if t > ent:
                        ent = t
                else:
                    if t < ex:
                        ex = t

        if ent > ex:
            return (0,0), (0,0)

        new0x = point0[0] + ent * deltaX
        new0y = point0[1] + ent * deltaY
        new1x = point0[0] + ex * deltaX
        new1y = point0[1] + ex * deltaY

        return (new0x, new0y), (new1x, new1y)

    def clipPolygon(self, points: List[Tuple[float,float]]):
        newLines = []
        previousDirection = Directions.NONE
        for i in range(0, len(points)):
            if(i < len(points) - 1):
                n1, n2 = self.clipLine(points[i], points[i + 1])
            else:
                n1, n2 = self.clipLine(points[i], points[0])

            if not (n1[0] == 0 and n1[1] == 0 and n2[0] == 0 and n2[1] == 0):

                if not(self.contains(newLines, n1)):
                    newLines.append(n1)

                if not (self.contains(newLines, n2)):
                    newLines.append(n2)

                newDirection = self.intersectionWith([n1, n2])
                if(previousDirection != newDirection and previousDirection != Directions.NONE
                    and newDirection != Directions.NONE):
                    corner = self.getCorner([previousDirection, newDirection])
                    if not(self.contains(newLines, corner)):
                        newLines.append(corner)
                previousDirection = newDirection

        return newLines

    def contains(self, points: List[Tuple[float, float]], point: Tuple[float, float]):
        length = len(points)
        for i in range(0, length):
            if(points[i][0] == point[0] and points[i][1] == point[1]):
                return True

        return False

    def intersectionWith(self, points: List[Tuple[float, float]]):
        print(points)
        for i in range(0, len(points)):
            if(points[i][0] == 1):
                return Directions.RIGHT
            if(points[i][0] == -1):
                return Directions.LEFT
            if(points[i][1] == 1):
                return Directions.UP
            if(points[i][1] == -1):
                return Directions.DOWN
        return Directions.NONE

    def getCorner(self, dirs: List[Directions]):
        retX = 0
        retY = 0
        for i in range(0, len(dirs)):
            if (dirs[i] == Directions.RIGHT):
                retX = 1
            elif(dirs[i] == Directions.LEFT):
                retX = -1
            elif(dirs[i] == Directions.UP):
                retY = 1
            elif(dirs[i] == Directions.DOWN):
                retY = -1

        return (retX, retY)
