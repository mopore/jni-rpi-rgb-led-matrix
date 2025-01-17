from typing import Protocol
from rgbmatrix import FrameCanvas, graphics
from PIL import Image, ImageSequence
import time


class Renderer(Protocol):

	def render(self, offscreen_canvas: FrameCanvas) -> None:
		...
	
	def exit(self) -> None:
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
		# This is an artificial slow down!!!
		time.sleep(frame.info['duration'] / 1000)
		offscreen_canvas.SetImage(frame) 
		self.frameIndex += 1
		if self.frameIndex >= self.framesLength:
			self.frameIndex = 0 

	def exit(self) -> None:
		pass


class RunTextRenderer(Renderer):

	TEXT_ORANGE_COLOR = graphics.Color(255, 128, 0)
	SIXTY_HERTZ = 0.0167

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
		time.sleep(self.SIXTY_HERTZ)
	
	def exit(self) -> None:
		pass
