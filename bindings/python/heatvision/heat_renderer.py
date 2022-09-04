from rgbmatrix import FrameCanvas
from renderer import Renderer
import numpy as np
from heat_colorizer import HeatColorizer
from data_collector import DataCollector, MqttDataCollector, MqttBridge
from level_interpolate import json_to_interpolated_array


class HeatvisionRenderer(Renderer):
    """This will show a 32x32 pixel array in the middle of the display with colors from blue to
    red"""

    TOTAL_WIDTH = 64
    TOTAL_HEIGHT = 32
    CANVAS_WIDTH = 32
    CANVAS_HEIGHT = 32

    def __init__(self, mqtt_bridge: MqttBridge) -> None:
        self.startx = (self.TOTAL_WIDTH / 2) - (self.CANVAS_WIDTH / 2)
        self.starty = (self.TOTAL_HEIGHT / 2) - (self.CANVAS_HEIGHT / 2)
        self.collector: DataCollector = MqttDataCollector(mqtt_bridge)

    def render(self, offscreen_canvas: FrameCanvas) -> None:
        json_string = self.collector.release()
        data32x32: np.ndarray | None = json_to_interpolated_array(json_string)
        colorizer = HeatColorizer(data32x32)
        for row in range(0, self.CANVAS_HEIGHT):
            for column in range(0, self.CANVAS_WIDTH):
                mirrored_x = self.CANVAS_WIDTH - 1 - column
                x_value = self.startx + mirrored_x
                y_value = self.starty + row
                red_value = colorizer.get_red(row, column)
                green_value = colorizer.get_green(row, column)
                blue_value = colorizer.get_blue(row, column)
                offscreen_canvas.SetPixel(
                    x_value, y_value, red_value, green_value, blue_value
                )
