import time
from PIL import Image, ImageSequence
from rgbmatrix import FrameCanvas, graphics, RGBMatrix, RGBMatrixOptions
from typing import Protocol
import threading


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
        # Text color should be blue
        self.textColor = RunTextRenderer.TEXT_ORANGE_COLOR
        self.pos = 64
        
    def render(self, offscreen_canvas: FrameCanvas) -> None:
        len = graphics.DrawText(offscreen_canvas, self.font, self.pos, 20, self.textColor, 
        self.text)
        self.pos -= 1
        if (self.pos + len < 0):
            self.pos = offscreen_canvas.width
        time.sleep(0.05)


class RendererShellThread:
    
    SHOOTER_PATH = "./shooter.gif"

    def __init__(self):
        self.keep_running = True

        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat'
        options.led_rgb_sequence = 'RBG'
        self.matrix = RGBMatrix(options=options)

        self.renderer1 = AnimatedGifRenderer(RendererShellThread.SHOOTER_PATH)
        self.renderer2 = RunTextRenderer("Ey!!!")
        self.selectedRenderer = self.renderer1

        threading.Thread(target=self.run).start()


    def run(self) -> None:
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        frame_counter = 0
        while self.keep_running:
            offscreen_canvas.Clear()
            self.selectedRenderer.render(offscreen_canvas)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            frame_counter += 1
            if frame_counter % 100 == 0:
                print(f"Switching renderer at Frame No. {frame_counter}")
                if self.selectedRenderer == self.renderer1:
                    self.selectedRenderer = self.renderer2
                else:
                    self.selectedRenderer = self.renderer1
        print("No more running :(")


def main():
    shell = RendererShellThread()
    print("MainThread: Will wait 10 seconds...")
    time.sleep(10)
    print("Waited ein will stop Shell Render Thread")
    shell.keep_running = False
                

if __name__ == '__main__':
    main()
