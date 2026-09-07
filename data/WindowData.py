from dataclasses import dataclass

@dataclass
class WindowData:
    x_min: float
    y_min: float
    x_max: float
    y_max: float
    angle: float = 0.0

    def width(self):
        return self.x_max - self.x_min

    def height(self):
        return self.y_max - self.y_min

    def center(self):
        return self.width() / 2, self.height() / 2,