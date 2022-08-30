import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from heat_renderer import HeatvisionRenderer
import threading
from mqtt_bridge import MqttBridge
import renderer

ONE_SECOND = 1
TOPIC_COMMAND_NAME = "jniHome/services/heatvision1/command"

EXIT_COMMAND_NAME = "exit"


class RendererShellThread:

    SHOOTER_PATH = "./shooter.gif"
    ROCKET_PATH = "./rocket_launch_vertical.gif"

    def __init__(self, mqtt_bridge: MqttBridge):
        self.keep_running = True

        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = 'adafruit-hat'
        options.led_rgb_sequence = 'RGB'
        #  options.led_rgb_sequence = 'RBG'
        self.matrix = RGBMatrix(options=options)

        self.selected_renderer_index = 0
        self.heatvision_renderer = HeatvisionRenderer(mqtt_bridge)
        self.renderers: list[renderer.Renderer] = [
            self.heatvision_renderer,
            #  renderer.AnimatedGifRenderer(self.SHOOTER_PATH),
            # renderer.RunTextRenderer("Ey!!!"),
            # renderer.AnimatedGifRenderer(self.ROCKET_PATH),
        ]
        threading.Thread(target=self.run).start()
    
    def run(self) -> None:
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        frame_counter = 0
        fps_last_timestamp = time.monotonic()
        fps_last_frame = frame_counter
        secs_per_scene = 0
        while self.keep_running:
            offscreen_canvas.Clear()
            self.renderers[self.selected_renderer_index].render(offscreen_canvas)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            frame_counter += 1
            timepassed = time.monotonic() - fps_last_timestamp
            if timepassed > ONE_SECOND:
                secs_per_scene += 1
                fps_now = frame_counter - fps_last_frame
                print(f"FPS: {fps_now} ", end="\r")
                fps_last_timestamp = time.monotonic()
                fps_last_frame = frame_counter
            if secs_per_scene > 5:
                print(f"Switching renderer at Frame No. {frame_counter}")
                self.selected_renderer_index += 1
                if self.selected_renderer_index == len(self.renderers):
                    self.selected_renderer_index = 0
                secs_per_scene = 0
         
        print("No more running :(")


def main():
    mqtt_bridge = MqttBridge()
    shell = RendererShellThread(mqtt_bridge)
    
    def exit_listener(topic: str, message: str) -> None:
        print("Exit listener triggered. '{topic}' '{message}'")
        if topic == TOPIC_COMMAND_NAME:
            if message == "exit":
                mqtt_bridge.stop()
                shell.keep_running = False
    
    mqtt_bridge.subscribe_with_cb(TOPIC_COMMAND_NAME, exit_listener)
    print(f"On topic '{TOPIC_COMMAND_NAME}' post '{EXIT_COMMAND_NAME}' to stop processing.")
            
    while shell.keep_running:
        time.sleep(0.1)
    print("All done.")


if __name__ == '__main__':
    main()
