import json
import math
import time
from rgbmatrix import FrameCanvas
from renderer import Renderer
from scipy.interpolate import griddata
import numpy as np


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


class DataProvider:
	def __init__(self) -> None:
		self.keep_alive = True
		self.data: str | None = None
		self.last_date_timestamp: float | None = None

	def store_data(self, text: str) -> None:
		self.last_date_timestamp = time.monotonic()
		self.data = text

	def collect_data(self) -> str | None:
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

	def __init__(self, data_provider: DataProvider) -> None:
		self.data: np.ndarray | None = None
		json_string = data_provider.collect_data()
		if (json_string is not None):
			sensor_data: list[list[float]] = json.loads(json_string, object_hook=as_sensor_data)
			self.data = sensor_data_to_32_32_colored(sensor_data)

	def get_red(self, row: int, column: int) -> int:
		if self.data is None:
			return 0
		value = self.data[row][column]
		final_value = 255 * (value / 100)
		if final_value < 0:
			final_value = 0
		if final_value > 255:
			final_value = 255
		return int(final_value)

	def get_blue(self, row: int, column: int) -> int:
		if self.data is None:
			return 0
		value = self.data[row][column]
		final_value = 255 - (255 * (value / 100))
		if final_value < 0:
			final_value = 0
		if final_value > 255:
			final_value = 255
		return int(final_value)

	def get_green(self, row: int, column: int) -> int:
		return 0


class HeatvisionRenderer(Renderer):
	""" This will show a 32x32 pixel array in the middle of the display with colors from blue to 
		red """

	MATRIX_WIDTH = 64
	MATRIX_HEIGHT = 32

	ARRAY_WIDTH = 32
	ARRAY_HEIGHT = 32

	def __init__(self) -> None:
		self.startx = (HeatvisionRenderer.MATRIX_WIDTH / 2) - (HeatvisionRenderer.ARRAY_WIDTH / 2) 
		self.starty = (HeatvisionRenderer.MATRIX_HEIGHT / 2) - (HeatvisionRenderer.ARRAY_HEIGHT / 2) 
		self.data_provider = DataProvider()

	def render(self, offscreen_canvas: FrameCanvas) -> None:
		colorizer = HeatColorizer(self.data_provider)
		for row in range(0, HeatvisionRenderer.ARRAY_HEIGHT):
			for column in range(0, HeatvisionRenderer.ARRAY_WIDTH):
				mirrored_x = HeatvisionRenderer.MATRIX_WIDTH - 1 - column
				offscreen_canvas.SetPixel(
					self.startx + mirrored_x, 
					self.starty + row, 
					colorizer.get_red(row, column), 
					colorizer.get_green(row, column),
					colorizer.get_blue(row, column),
				)
	
	def receive_heatvision_data(self, text: str) -> None:
		self.data_provider.store_data(text)
