from renderer import Renderer
from rgbmatrix import FrameCanvas, graphics
from space_operation.aws_button_listener import AwsButtonListener


class SpaceOperationRenderer(Renderer):

	TEXT_ORANGE_COLOR = graphics.Color(255, 128, 0)

	def __init__(self):
		self.textColor = self.TEXT_ORANGE_COLOR
		self.font = graphics.Font()
		self.font.LoadFont("../../fonts/5x8.bdf")
		self.textColor = self.TEXT_ORANGE_COLOR
		self.text = "Space OP"

		# Remember to start "start.sh" in space_operation folder to download AWS IoT SDK
		def topic_callback(topic: str, message: str) -> None:
			global listener
			global message_counter
			print(f"Received message on topic '{topic}'")

		self.listener = AwsButtonListener(topic_callback) 
	
	def render(self, offscreen_canvas: FrameCanvas) -> None:
		height = offscreen_canvas.height
		width = offscreen_canvas.width
		for x in range(width):
			for y in range(height):
				offscreen_canvas.SetPixel(x, y, 10, 10, 10)
		graphics.DrawText(offscreen_canvas, self.font, 10, 20, self.textColor, self.text)

	def exit(self) -> None:
		self.listener.disconnect()
