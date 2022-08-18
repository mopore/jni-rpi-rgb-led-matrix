from rgbmatrix import FrameCanvas
from renderer import Renderer


class HeatColorizer:

	def __init__(self, max: int) -> None:
		self.red: float = 0
		self.green: float = 0
		self.blue: float = 0
		self.max: int = max

	def get_red(self) -> int:
		return int(self.red)

	def get_blue(self) -> int:
		return int(self.blue)

	def get_green(self) -> int:
		return int(self.green)

	def update(self, row: int, column: int) -> None:
		red_share = column / self.max
		self.red = 255 * red_share
		blue_share = 1 - (column / self.max)
		self.blue = 255 * blue_share


class HeatvisionRenderer(Renderer):
	""" This will show a 32x32 pixel array in the middle of the display with colors from blue to 
		red """

	CANVAS_WIDTH = 64
	CANVAS_HEIGHT = 32

	ARRAY_WIDTH = 32
	ARRAY_HEIGHT = 32

	def __init__(self) -> None:
		self.startx = (HeatvisionRenderer.CANVAS_WIDTH / 2) - (HeatvisionRenderer.ARRAY_WIDTH / 2) 
		self.starty = (HeatvisionRenderer.CANVAS_HEIGHT / 2) - (HeatvisionRenderer.ARRAY_HEIGHT / 2) 
		self.colorizer = HeatColorizer(32)

	def render(self, offscreen_canvas: FrameCanvas) -> None:
		for row in range(0, HeatvisionRenderer.ARRAY_HEIGHT):
			for column in range(0, HeatvisionRenderer.ARRAY_WIDTH):
				self.colorizer.update(row, column)
				offscreen_canvas.SetPixel(
					self.startx + column, 
					self.starty + row, 
					self.colorizer.get_red(), 
					self.colorizer.get_green(), 
					self.colorizer.get_blue()
				)
	
	def receive_heatvision_data(self, text: str) -> None:
		print(f"Data received: {text}")
