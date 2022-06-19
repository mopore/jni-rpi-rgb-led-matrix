import time

from PIL import Image, ImageSequence
from rgbmatrix import RGBMatrix, RGBMatrixOptions

RGB_MODE_NAME = 'RGB'
SHOOTER_PATH = "./shooter.gif"


def load_gif_frames():
    """Returns an iterable of gif frames."""
    frames = []
    with Image.open(SHOOTER_PATH) as gif:
        for frame in ImageSequence.Iterator(gif):
            frame = frame.convert(RGB_MODE_NAME).resize((64, 32))
            frames.append(frame)
        return frames


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
    while True:
        for frame in load_gif_frames():
            
            offscreen_canvas.Clear()

            offscreen_canvas.SetImage(frame) 

            offscreen_canvas = matrix.SwapOnVSync(offscreen_canvas)
            time.sleep(frame.info['duration'] / 1000)
            frame_counter += 1
            if frame_counter % 10 == 0:
                print(f"Frame counter is at: {frame_counter}")


if __name__ == '__main__':
    main()
