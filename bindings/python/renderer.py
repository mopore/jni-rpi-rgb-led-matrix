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


class HeatDisplayRenderer(Renderer):

	def render(self, offscreen_canvas: FrameCanvas) -> None:
		for i in range(0, offscreen_canvas.width):
			offscreen_canvas.SetPixel(i, (offscreen_canvas.height / 2), 255, 255, 255)
