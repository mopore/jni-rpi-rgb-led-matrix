import numpy as np


MAX_COLOR = 255


class HeatColorizer:

    def __init__(self, data32x32: np.ndarray | None) -> None:
        self.data32x32 = data32x32

    def get_red(self, row: int, column: int) -> int:
        if self.data32x32 is None:
            return 0
        value = self.data32x32[row][column]
        final_value = MAX_COLOR * (value / 100)
        if final_value < 0:
            final_value = 0
        if final_value > MAX_COLOR:
            final_value = MAX_COLOR
        return int(final_value)

    def get_blue(self, row: int, column: int) -> int:
        if self.data32x32 is None:
            return 0
        value = self.data32x32[row][column]
        final_value = MAX_COLOR - (MAX_COLOR * (value / 100))
        if final_value < 0:
            final_value = 0
        if final_value > MAX_COLOR:
            final_value = MAX_COLOR
        return int(final_value)

    def get_green(self, row: int, column: int) -> int:
        return 0
