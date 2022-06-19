import time

from PIL import Image, ImageSequence
from rgbmatrix import RGBMatrix, RGBMatrixOptions

RGB_MODE_NAME = 'RGB'
SHOOTER_PATH = "./shooter.gif"


class AnimatedGifRenderer:
    def __init__(self, path: str):
        self.frames = self.load_gif_frames(path)
        self.framesLength = len(self.frames)
        self.frameIndex = 0

    def load_gif_frames(self, path: str):
        """Returns an iterable of gif frames."""
        frames = []
        with Image.open(path) as gif:
            for frame in ImageSequence.Iterator(gif):
                frame = frame.convert(RGB_MODE_NAME).resize((64, 32))
                frames.append(frame)
            return frames

    def render(self, offscreen_canvas) -> None:
        frame = self.frames[self.frameIndex]
        time.sleep(frame.info['duration'] / 1000)
        offscreen_canvas.SetImage(frame) 
        self.frameIndex += 1
        if self.frameIndex >= self.framesLength:
            self.frameIndex = 0 


def main():
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = 'adafruit-hat'
    matrix = RGBMatrix(options=options)

    offscreen_canvas = matrix.CreateFrameCanvas()
    
    frame_counter = 0
    renderer = AnimatedGifRenderer(SHOOTER_PATH)
    while True:
        offscreen_canvas.Clear()
        renderer.render(offscreen_canvas)
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
        frame_counter += 1
        if frame_counter % 10 == 0:
            print(f"Frame counter is at: {frame_counter}")


if __name__ == '__main__':
    main()
