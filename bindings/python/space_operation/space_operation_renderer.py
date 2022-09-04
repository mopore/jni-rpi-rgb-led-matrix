from renderer import Renderer
import time
from rgbmatrix import FrameCanvas, graphics


class SpaceOperationRenderer(Renderer):

	TEXT_ORANGE_COLOR = graphics.Color(255, 128, 0)

	def __init__(self):
		self.text = "Space Operation"
		self.font = graphics.Font()
		self.font.LoadFont("../../fonts/7x13.bdf")
		self.textColor = self.TEXT_ORANGE_COLOR
		self.pos = 64

	def render(self, offscreen_canvas: FrameCanvas) -> None:
		len = graphics.DrawText(offscreen_canvas, self.font, self.pos, 20, self.textColor, 
		self.text)
		self.pos -= 1
		if (self.pos + len < 0):
			self.pos = offscreen_canvas.width
		time.sleep(0.05)
