from dataclasses import dataclass

@dataclass
class ViewportData:
    x_min: float
    y_min: float
    x_max: float
    y_max: float

    def width(self):
        return self.x_max - self.x_min

    def height(self):
        return self.y_max - self.y_min