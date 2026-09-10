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
        code0 = self.region(point0)
        code1 = self.region(point1)
        if(code0 == 0 and code1 == 0): return point0, point1
        if(code0 & code1 != 0): return (0,0), (0,0)

        slope = 0 if(point0[0] == point1[0] and point0[1] == point1[1]) else (point1[1] - point0[1])/(point1[0] - point0[0])

        slopeTL = (self.maxY - point0[1])/(self.minX - point0[0])
        slopeTR = (self.maxY - point0[1])/(self.maxX - point0[0])
        slopeBL = (self.minY - point0[1])/(self.minX - point0[0])
        slopeBR = (self.minY - point0[1])/(self.maxX - point0[0])

        intersection = 0
        if(slopeTL < slope and slope < slopeTR):
            intersection |= 8
        if(slopeTR < slope and slope < slopeBR):
            intersection |= 2
        if(slopeBR < slope and slope < slopeBL):
            intersection |= 4
        if(slopeBL < slope)

        if(code0 == 0):
            new0 = point0
        else:
            if(code0 & 8 != 0):
                if()
        new1 = point1

        intersections = code0 & code1

        print("\n", intersections, "\n")

        if(intersections & 8 != 0):
            topIntersection = (self.maxY - point1[1])/slope + point1[0]
            if(code0 & 8): new0 = (topIntersection, self.maxY)
            else: new1 = (topIntersection, self.maxY)
        if(intersections & 4 != 0):
            bottomIntersection = (self.minY - point1[1])/slope + point1[0]
            if(code0 & 4): new0 = (bottomIntersection, self.minY)
            else: new1 = (bottomIntersection, self.minY)
        if(intersections & 2 != 0):
            rightIntersection = (self.maxX - point1[0]) * slope + point1[1]
            print(rightIntersection)
            if(code0 & 8): new0 = (self.maxX, rightIntersection)
            else: new1 = (self.maxX, rightIntersection)
        if(intersections & 1 != 0):
            leftIntersection = (self.minX - point1[0]) * slope + point1[1]
            if(code0 & 8): new0 = (self.minX, leftIntersection)
            else: new1 = (self.minX, leftIntersection)

        print("new0:", new0, "new1: ", new1)
        return new0, new1 # 0,0;50,0;50,50;0,50  100,200;200,100;100,0;0,100

    def clipPolygon(self, points: List[Tuple[float,float]]):
        newLines = []
        for i in range(0, len(points)):
            if(i < len(points)- 1):
                n1, n2 = self.clipLine(points[i], points[i + 1])
            else:
                n1, n2 = self.clipLine(points[i], points[0])

            if not (n1[0] == 0 and n1[1] == 0 and n2[0] == 0 and n2[1] == 0):
                print("cand: ", n1, n2)
                if(len(newLines) > 0): print(newLines[i - 1][0] != n1[0], newLines[i - 1][1] != n1[1])
                if(len(newLines) == 0) or (newLines[i - 1][0] != n1[0] and newLines[i - 1][1] != n1[1]):
                    newLines.append(n1)
                    print("add ", n1)
                newLines.append(n2)
                print("add ", n2, "_")

        return newLines

    def outOfBounds(self, point: Tuple[float,float]):
        return point[0] < self.maxX and point[0] > self.minX and point[1] < self.maxY and point[1] > self.minY

    def region(self, point: Tuple[float,float]):
        top = 8 if point[1] > self.maxY else 0
        bottom = 4 if point[1] < self.minY else 0
        right = 2 if point[0] > self.maxX else 0
        left = 1 if point[0] < self.minX else 0
        return top | bottom | right | left
