import time

from PIL import Image, ImageSequence
from rgbmatrix import graphics, RGBMatrix, RGBMatrixOptions

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


class RunTextRenderer:
    def __init__(self, text: str):
        self.text = text
        self.font = graphics.Font()
        self.font.LoadFont("../../fonts/7x13.bdf")
        # Text color should be blue
        self.textColor = graphics.Color(0, 0, 255)
        self.pos = 64
        
    def render(self, offscreen_canvas) -> None:
        len = graphics.DrawText(offscreen_canvas, self.font, self.pos, 20, self.textColor, 
        self.text)
        self.pos -= 1
        if (self.pos + len < 0):
            self.pos = offscreen_canvas.width
        time.sleep(0.05)


def main():
    options = RGBMatrixOptions()
    options.rows = 32
    options.cols = 64
    options.chain_length = 1
    options.parallel = 1
    options.hardware_mapping = 'adafruit-hat'
    options.led_rgb_sequence = 'RBG'
    matrix = RGBMatrix(options=options)

    offscreen_canvas = matrix.CreateFrameCanvas()
    
    frame_counter = 0
    renderer1 = AnimatedGifRenderer(SHOOTER_PATH)
    renderer2 = RunTextRenderer("Ey!!!")
    selectedRenderer = renderer1

    while True:
        offscreen_canvas.Clear()
        selectedRenderer.render(offscreen_canvas)
        offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
        frame_counter += 1
        if frame_counter % 100 == 0:
            print(f"Switching renderer at Frame No. {frame_counter}")
            if selectedRenderer == renderer1:
                selectedRenderer = renderer2
            else:
                selectedRenderer = renderer1
                

if __name__ == '__main__':
    main()
