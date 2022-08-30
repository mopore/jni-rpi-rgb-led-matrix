import json
import math
import time
from rgbmatrix import FrameCanvas
from renderer import Renderer
from scipy.interpolate import griddata
import numpy as np

MAX_COLOR = 255
VALUE_RANGE = 100
MINTEMP = 20.0  # low range of the sensor (this will be blue on the screen)
MAXTEMP = 32.0  # high range of the sensor (this will be red on the screen)


def map_value(x, out_min, out_max):
	if x < MINTEMP:
		x = MINTEMP
	if x > MAXTEMP:
		x = MAXTEMP
	return (x - MINTEMP) * (out_max - out_min) / (MAXTEMP - MINTEMP) + out_min


def as_sensor_data(dict) -> list[list[float]]:
	data_array = dict["sensor_data"]
	return data_array


def sensor_data_to_32_32_colored(sensor_data: list[list[float]]) -> np.ndarray:
	pixels = []
	for row in sensor_data:
		pixels = pixels + row
	pixels = [map_value(p, 0, VALUE_RANGE - 1) for p in pixels]

	# pylint: disable=invalid-slice-index
	points = [(math.floor(ix / 8), (ix % 8)) for ix in range(0, 64)]
	grid_x, grid_y = np.mgrid[0:7:32j, 0:7:32j]
	# pylint: enable=invalid-slice-index

	# perform interpolation
	bicubic = griddata(points, pixels, (grid_x, grid_y), method="cubic")
	return bicubic


class JsonDataCollector:
	def __init__(self) -> None:
		self.keep_alive = True
		self.data: str | None = None
		self.last_date_timestamp: float | None = None

	def store(self, text: str) -> None:
		self.last_date_timestamp = time.monotonic()
		self.data = text

	def release(self) -> str | None:
		if self.data is not None:
			if self.last_date_timestamp is not None:
				time_passed = time.monotonic() - self.last_date_timestamp
				if time_passed > 1:
					self.data = None
					self.last_date_timestamp = None
			else:
				self.data = None
		return self.data


class HeatColorizer:

	def __init__(self, collector: JsonDataCollector) -> None:
		self.data: np.ndarray | None = None
		json_string = collector.release()
		if (json_string is not None):
			sensor_data: list[list[float]] = json.loads(json_string, object_hook=as_sensor_data)
			self.data = sensor_data_to_32_32_colored(sensor_data)

	def get_red(self, row: int, column: int) -> int:
		if self.data is None:
			return 0
		value = self.data[row][column]
		final_value = MAX_COLOR * (value / 100)
		if final_value < 0:
			final_value = 0
		if final_value > MAX_COLOR:
			final_value = MAX_COLOR
		return int(final_value)

	def get_blue(self, row: int, column: int) -> int:
		if self.data is None:
			return 0
		value = self.data[row][column]
		final_value = MAX_COLOR - (MAX_COLOR * (value / 100))
		if final_value < 0:
			final_value = 0
		if final_value > MAX_COLOR:
			final_value = MAX_COLOR
		return int(final_value)

	def get_green(self, row: int, column: int) -> int:
		return 0


class HeatvisionRenderer(Renderer):
	""" This will show a 32x32 pixel array in the middle of the display with colors from blue to 
		red """

	TOTAL_WIDTH = 64
	TOTAL_HEIGHT = 32

	CANVAS_WIDTH = 32
	CANVAS_HEIGHT = 32

	def __init__(self) -> None:
		self.startx = (self.TOTAL_WIDTH / 2) - (self.CANVAS_WIDTH / 2) 
		self.starty = (self.TOTAL_HEIGHT / 2) - (self.CANVAS_HEIGHT / 2) 
		self.data_provider = JsonDataCollector()

	def render(self, offscreen_canvas: FrameCanvas) -> None:
		colorizer = HeatColorizer(self.data_provider)
		for row in range(0, self.CANVAS_HEIGHT):
			for column in range(0, self.CANVAS_WIDTH):
				mirrored_x = self.CANVAS_WIDTH - 1 - column
				x_value = self.startx + mirrored_x
				y_value = self.starty + row
				red_value = colorizer.get_red(row, column)
				green_value = colorizer.get_green(row, column)
				blue_value = colorizer.get_blue(row, column)
				offscreen_canvas.SetPixel(x_value, y_value, red_value, green_value, blue_value)
	
	def receive_heatvision_data(self, text: str) -> None:
		self.data_provider.store(text)
