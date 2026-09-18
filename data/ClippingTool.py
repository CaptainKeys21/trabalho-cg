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

    def clipLineCohenSutherlandDirectional(self, point0: Tuple[float, float], point1: Tuple[float, float], dir: Directions):
        region0 = self.region(point0)
        region1 = self.region(point1)
        # if (region0 | region1 == 0 or (not(region0 & region1 == 0) and region0 & dir.value == 0)): return (point0, point1)

        current0 = point0
        current1 = point1

        slope = 0 if (point1[0] - point0[0] == 0) else (point1[1] - point0[1])/(point1[0] - point0[0])

        if(region0 & dir.value > 0):
            if(dir == Directions.UP):
                current0 = (current0[0], self.maxY) if (slope == 0) else  (current0[0] + (self.maxY - current0[1])/slope, self.maxY)
            elif(dir == Directions.DOWN):
                current0 = (current0[0], self.minY) if (slope == 0) else  (current0[0] + (self.minY - current0[1])/slope, self.minY)
            elif(dir == Directions.LEFT):
                current0 = (self.minX, current0[1] + (self.minX - current0[0]) * slope)
            elif(dir == Directions.RIGHT):
                current0 = (self.maxX, current0[1] + (self.maxX - current0[0]) * slope)

        elif(region1 & dir.value > 0):
            if(dir == Directions.UP):
                current1 = (current1[0], self.maxY) if (slope == 0) else (current1[0] + (self.maxY - current1[1])/slope, self.maxY)
            elif(dir == Directions.DOWN):
                current1 = (current1[0], self.minY) if (slope == 0) else (current1[0] + (self.minY - current1[1])/slope, self.minY)
            elif(dir == Directions.LEFT):
                current1 = (self.minX, current1[1] + (self.minX - current1[0]) * slope)
            elif(dir == Directions.RIGHT):
                current1 = (self.maxX, current1[1] + (self.maxX - current1[0]) * slope)
        return current0, current1


    def clipLineLiangBarsky(self, point0: Tuple[float,float], point1: Tuple[float,float]):
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


    def clipLineLiangBarskyDirectional(self, point0: Tuple[float,float], point1: Tuple[float,float], dir: Directions):
        deltaX = point1[0] - point0[0]
        deltaY = point1[1] - point0[1]
        p = [-deltaX, deltaX, -deltaY, deltaY]
        q = [point0[0] - self.minX, self.maxX - point0[0], point0[1] - self.minY, self.maxY - point0[1]]
        ent = 0
        ex = 1

        i = 0
        if(dir == Directions.RIGHT):
            i = 1
        elif(dir == Directions.DOWN):
            i = 2
        elif(dir == Directions.UP):
            i = 3

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
        edges = [Directions.RIGHT, Directions.UP, Directions.LEFT, Directions.DOWN]
        for i in range(0, len(points)):
            newLines.append(points[i])

        for i in range(0, 4):
            # print(edges[i])
            intermediary = []
            for j in range(0, len(newLines)):
                if(j == len(newLines) - 1):
                    vert0 = newLines[j]
                    vert1 = newLines[0]
                else:
                    vert0 = newLines[j]
                    vert1 = newLines[j + 1]
                # print()
                if(self.region(vert0) & edges[i].value == 0):
                    if(self.region(vert1) & edges[i].value == 0):
                        # print("BOTH IN: ", vert0, vert1, end=' ')
                        # print("ADDED: ", vert1)
                        intermediary.append(vert1)
                    else:
                        newV0, newV1 = self.clipLineLiangBarskyDirectional(vert0, vert1, edges[i])
                        intermediary.append(newV1)
                        # print("SECOND OUT: ", vert0, vert1, end=' ')
                        # print("ADDED: ", newV1)
                elif(self.region(vert1) & edges[i].value == 0):
                    newV0, newV1 = self.clipLineLiangBarskyDirectional(vert0, vert1, edges[i])
                    intermediary.append(newV0)
                    intermediary.append(vert1)
                    # print("FIRST OUT: ", vert0, vert1, end=' ')
                    # print("ADDED: ", newV0, newV1)
                # else:
                    # print("BOTH OUT: ", vert0, vert1, end=' ')
                    # print("ADDED: NONE")
            newLines = []
            for k in range(len(intermediary)):
                newLines.append(intermediary[k])

        if(len(newLines) == 0):
            if(self.isSurrounding(points)):
                newLines.append((self.minX, self.maxY))
                newLines.append((self.minX, self.minY))
                newLines.append((self.maxX, self.minY))
                newLines.append((self.maxX, self.maxY))
        # print(newLines)
        return newLines

    def contains(self, points: List[Tuple[float, float]], point: Tuple[float, float]):
        length = len(points)
        for i in range(0, length):
            if(points[i][0] == point[0] and points[i][1] == point[1]):
                return True

        return False

    def intersectionWith(self, points: List[Tuple[float, float]]):
        for i in range(0, len(points)):
            reg = self.region(points[i])
            if(reg & Directions.RIGHT.value > 0):
                return Directions.RIGHT
            if(reg & Directions.LEFT.value > 0):
                return Directions.LEFT
            if(reg & Directions.UP.value > 0):
                return Directions.UP
            if(reg & Directions.DOWN.value > 0):
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