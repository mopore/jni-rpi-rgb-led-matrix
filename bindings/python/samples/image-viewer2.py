import time
from samplebase import SampleBase
from PIL import Image


class ImageViewer(SampleBase):
    def __init__(self, *args, **kwargs):
        super(ImageViewer, self).__init__(*args, **kwargs)
        self.parser.add_argument("-i", "--image", help="The image to display", default="../../../examples-api-use/runtext.ppm")

    def run(self):
        if not 'image' in self.__dict__:
            self.image = Image.open(self.args.image).convert('RGB')

        print(f"Matrix width: {self.matrix.width}, height: {self.matrix.height}")
        self.image = self.image.resize((self.matrix.width, self.matrix.height), Image.ANTIALIAS)

        double_buffer = self.matrix.CreateFrameCanvas()
        img_width, img_height = self.image.size
        print(f"Image width: {img_width}, height: {img_height}")

        # let's scroll
        xpos = 0
        while True:
            #  xpos += 
            #  if (xpos > img_width):
            #      xpos = 0

            double_buffer.SetImage(self.image, -xpos)
            #  double_buffer.SetImage(self.image, -xpos + img_width)

            double_buffer = self.matrix.SwapOnVSync(double_buffer)
            time.sleep(0.01)

# Main function
# e.g. call with
#  sudo ./image-scroller.py --chain=4
# if you have a chain of four
if __name__ == "__main__":
    viewer = ImageViewer()
    if (not viewer.process()):
        viewer.print_help()