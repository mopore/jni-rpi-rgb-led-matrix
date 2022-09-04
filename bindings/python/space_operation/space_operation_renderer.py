from renderer import Renderer
import time
from rgbmatrix import FrameCanvas, graphics


class SpaceOperationRenderer(Renderer):

	TEXT_ORANGE_COLOR = graphics.Color(255, 128, 0)

	def __init__(self):
		self.textColor = self.TEXT_ORANGE_COLOR
		self.font = graphics.Font()
		self.font.LoadFont("../../fonts/5x8.bdf")
		self.textColor = self.TEXT_ORANGE_COLOR
		self.text = "Space Operation"
	
	def render(self, offscreen_canvas: FrameCanvas) -> None:
		height = offscreen_canvas.height()
		width = offscreen_canvas.width() 
		for x in width:
			for y in height:
				offscreen_canvas.SetPixel(x, y, 50, 50, 50)
		graphics.DrawText(offscreen_canvas, self.font, 20, 20, self.textColor, 
		self.text)
