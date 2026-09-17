from enum import Enum
from tkinter.constants import RIGHT
from typing import Tuple, List


class Directions(Enum):
    RIGHT = 2
    LEFT = 1
    UP = 8
    DOWN = 4
    NONE = 0

class ClippingTool:
    def __init__(self, minX: float, maxX: float, minY: float, maxY: float):
        self.minX = minX
        self.maxX = maxX
        self.minY = minY
        self.maxY = maxY


    def clipLineCohenSutherland(self, point0: Tuple[float,float], point1: Tuple[float,float]):
        region0 = self.region(point0)
        region1 = self.region(point1)
        if(region0 | region1 == 0): return (point0, point1)
        if not(region0 & region1 == 0): return ((0, 0), (0, 0))

        slope = (point1[1] - point0[1])/(point1[0] - point0[0])

        bothRegions = region0 | region1
        current0 = point0
        current1 = point1

        while(bothRegions != 0):
            if(self.region(current0) & Directions.UP.value > 0):
                current0 = (current0[0] + (self.maxY - current0[1])/slope, self.maxY)
            if(self.region(current1) & Directions.UP.value > 0):
                current1 = (current1[0] + (self.maxY - current1[1])/slope, self.maxY)

            if(self.region(current0) & Directions.DOWN.value > 0):
                current0 = (current0[0] + (self.minY - current0[1])/slope, self.minY)
            if(self.region(current1) & Directions.DOWN.value > 0):
                current1 = (current1[0] + (self.minY - current1[1])/slope, self.minY)

            if(self.region(current0) & Directions.LEFT.value > 0):
                current0 = (self.minX, current0[1] + (self.minX - current0[0]) * slope)
            if(self.region(current1) & Directions.LEFT.value > 0):
                current1 = (self.minX, current1[1] + (self.minX - current1[0]) * slope)

            if(self.region(current0) & Directions.RIGHT.value > 0):
                current0 = (self.maxX, current0[1] + (self.maxX - current0[0]) * slope)
            if(self.region(current1) & Directions.RIGHT.value > 0):
                current1 = (self.maxX, current1[1] + (self.maxX - current1[0]) * slope)

            bothRegions = self.region(current0) | self.region(current1)

        return (current0, current1)



    def clipLineLinangBarsky(self, point0: Tuple[float,float], point1: Tuple[float,float]):
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
        previousDirection = 0
        for i in range(0, len(points)):
            if(i < len(points) - 1):
                n1, n2 = self.clipLineLinangBarsky(points[i], points[i + 1])
            else:
                n1, n2 = self.clipLineLinangBarsky(points[i], points[0])

            if not (n1[0] == 0 and n1[1] == 0 and n2[0] == 0 and n2[1] == 0):

                if not(self.contains(newLines, n1)):
                    newLines.append(n1)

                if not (self.contains(newLines, n2)):
                    newLines.append(n2)

                # newDirection = self.intersectionWith([n1, n2])
                # if(previousDirection != newDirection and previousDirection != Directions.NONE
                #     and newDirection != Directions.NONE):
                #     corner = self.getCorner([previousDirection, newDirection])
                #     if not(self.contains(newLines, corner)):
                #         newLines.append(corner)
                # previousDirection = newDirection

        if(len(newLines) == 0):
            # print(points)
            if(self.isSurrounding(points)):
                newLines.append((self.minX, self.maxY))
                newLines.append((self.minX, self.minY))
                newLines.append((self.maxX, self.minY))
                newLines.append((self.maxX, self.maxY))

        return newLines

    def contains(self, points: List[Tuple[float, float]], point: Tuple[float, float]):
        length = len(points)
        for i in range(0, length):
            if(points[i][0] == point[0] and points[i][1] == point[1]):
                return True

        return False

    def intersectionWith(self, points: List[Tuple[float, float]]):
        for i in range(0, len(points)):
            if(points[i][0] == self.maxX):
                return Directions.RIGHT
            if(points[i][0] == self.minX):
                return Directions.LEFT
            if(points[i][1] == self.maxY):
                return Directions.UP
            if(points[i][1] == self.minY):
                return Directions.DOWN
        return Directions.NONE

    def getCorner(self, dirs: List[Directions]):
        retX = 0
        retY = 0
        for i in range(0, len(dirs)):
            if (dirs[i] == Directions.RIGHT):
                retX = self.maxX
            elif(dirs[i] == Directions.LEFT):
                retX = self.minX
            elif(dirs[i] == Directions.UP):
                retY = self.maxY
            elif(dirs[i] == Directions.DOWN):
                retY = self.minY

        return (retX, retY)

    def region(self, point: Tuple[float, float]):
        top = 8 if point[1] > self.maxY else 0
        bottom = 4 if point[1] < self.minY else 0
        right = 2 if point[0] > self.maxX else 0
        left = 1 if point[0] < self.minX else 0
        return top | bottom | right | left

    def isSurrounding(self, points:List[Tuple[float, float]]):
        reg = self.region(points[0])
        count = 0
        for i in range(1, len(points)):
            if(reg == Directions.UP.value | Directions.RIGHT.value):
                if(self.region(points[i]) == Directions.DOWN.value | Directions.RIGHT.value):
                    count += 1
                elif(self.region(points[i]) == Directions.UP.value | Directions.LEFT.value):
                    count -= 1
            elif(reg == Directions.LEFT.value | Directions.UP.value):
                if(self.region(points[i]) == Directions.UP.value | Directions.RIGHT.value):
                    count += 1
                elif(self.region(points[i]) == Directions.DOWN.value | Directions.LEFT.value):
                    count -= 1
            elif(reg == Directions.DOWN.value | Directions.LEFT.value):
                if(self.region(points[i]) == Directions.UP.value | Directions.LEFT.value):
                    count += 1
                elif(self.region(points[i]) == Directions.DOWN.value | Directions.RIGHT.value):
                    count -= 1
            elif(reg == Directions.RIGHT.value | Directions.DOWN.value):
                if(self.region(points[i]) == Directions.DOWN.value | Directions.LEFT.value):
                    count += 1
                elif(self.region(points[i]) == Directions.UP.value | Directions.RIGHT.value):
                    count -= 1
            reg = self.region(points[i])
        # print("count: ", count)
        return (count != 0) and (self.region(points[len(points) - 1]) & self.region(points[0]) != 0)

#
# tool = ClippingTool(-1, 1, -1, 1)
# print(tool.clipLineCohenSutherland((0.1, 0.8), (0.7, 1.4)))
# print(tool.clipLineCohenSutherland((0.3, 0.7), (1.4, 0.9)))
# print(tool.clipLineCohenSutherland((0.4, 0.2), (1.2, 0.7)))