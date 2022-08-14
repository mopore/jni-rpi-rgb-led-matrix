from typing import Protocol
from rgbmatrix import FrameCanvas, graphics
from PIL import Image, ImageSequence
import time


class Renderer(Protocol):

	def render(self, offscreen_canvas: FrameCanvas) -> None:
		...


class AnimatedGifRenderer(Renderer):

	RGB_MODE_NAME = 'RGB'

	def __init__(self, path: str):
		self.frames = self.load_gif_frames(path)
		self.framesLength = len(self.frames)
		self.frameIndex = 0

	def load_gif_frames(self, path: str):
		"""Returns an iterable of gif frames."""
		frames = []
		with Image.open(path) as gif:
			for frame in ImageSequence.Iterator(gif):
				frame = frame.convert(
					AnimatedGifRenderer.RGB_MODE_NAME).resize((64, 32))
				frames.append(frame)
			return frames

	def render(self, offscreen_canvas: FrameCanvas) -> None:
		frame = self.frames[self.frameIndex]
		time.sleep(frame.info['duration'] / 1000)
		offscreen_canvas.SetImage(frame) 
		self.frameIndex += 1
		if self.frameIndex >= self.framesLength:
			self.frameIndex = 0 


class RunTextRenderer(Renderer):

	TEXT_ORANGE_COLOR = graphics.Color(255, 128, 0)

	def __init__(self, text: str):
		self.text = text
		self.font = graphics.Font()
		self.font.LoadFont("../../fonts/7x13.bdf")
		self.textColor = RunTextRenderer.TEXT_ORANGE_COLOR
		self.pos = 64

	def render(self, offscreen_canvas: FrameCanvas) -> None:
		len = graphics.DrawText(offscreen_canvas, self.font, self.pos, 20, self.textColor, 
		self.text)
		self.pos -= 1
		if (self.pos + len < 0):
			self.pos = offscreen_canvas.width
		time.sleep(0.05)


class HeatColorizer:

	def __init__(self, max: int) -> None:
		self.red: float = 0
		self.green: float = 0
		self.blue: float = 0
		self.max: int = 0

	def get_red(self) -> int:
		return int(self.red)

	def get_blue(self) -> int:
		return int(self.blue)

	def get_green(self) -> int:
		return int(self.green)

	def update(self, row: int, column: int) -> None:
		red_share = row / self.max
		self.red = 255 * red_share
		blue_share = self.max - (row / self.max)
		self.blue = 255 * blue_share


class HeatDisplayRenderer(Renderer):
	""" This will show a 32x32 pixel array in the middle of the display with colors from blue to 
		red """

	CANVAS_WIDTH = 64
	CANVAS_HEIGHT = 32

	ARRAY_WIDTH = 32
	ARRAY_HEIGHT = 32

	def __init__(self) -> None:
		self.startx = (HeatDisplayRenderer.CANVAS_WIDTH / 2) - (HeatDisplayRenderer.ARRAY_WIDTH / 2) 
		self.starty = (HeatDisplayRenderer.CANVAS_HEIGHT / 2) - (HeatDisplayRenderer.ARRAY_HEIGHT / 2) 
		self.colorizer = HeatColorizer(32)

	def render(self, offscreen_canvas: FrameCanvas) -> None:
		for row in range(0, HeatDisplayRenderer.ARRAY_HEIGHT):
			for column in range(0, HeatDisplayRenderer.ARRAY_WIDTH):
				self.colorizer.update(row, column)
				offscreen_canvas.SetPixel(
					self.startx + column, 
					self.starty + row, 
					self.colorizer.get_red(), 
					self.colorizer.get_green(), 
					self.colorizer.get_blue()
				)
