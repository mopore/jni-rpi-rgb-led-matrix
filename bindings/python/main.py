import time
import threading
import renderer
import subprocess
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from heatvision.heat_renderer import HeatvisionRenderer
from heatvision.mqtt_bridge import MqttBridge
from space_operation.space_operation_renderer import SpaceOperationRenderer


ONE_SECOND = 1
TOPIC_COMMAND_NAME = "jniHome/services/matrixDisplay/command"
IP_TEST_RIG = "192.168.199.247"

EXIT_COMMAND_NAME = "exit"


def test_running_on_test_rig() -> bool:
    testing_rig = False
    try:
        subprocess.check_output([f"ip a | grep {IP_TEST_RIG}"], shell=True, text=True)
        testing_rig = True
    except subprocess.CalledProcessError as e:
        pass  # We expect an error if IP not matched 
    return testing_rig


class RendererShellThread:

    SIXTY_HERTZ = 0.0167
    SHOOTER_PATH = "./shooter.gif"
    ROCKET_PATH = "./rocket_launch_vertical.gif"

    def __init__(self, mqtt_bridge: MqttBridge):
        self.keep_running = True

        options = RGBMatrixOptions()
        options.rows = 32
        options.cols = 64
        options.chain_length = 1
        options.parallel = 1
        options.hardware_mapping = "adafruit-hat"

        if test_running_on_test_rig():
            options.led_rgb_sequence = "RBG"
        else:
            options.led_rgb_sequence = "RGB"

        self.matrix = RGBMatrix(options=options)
        self.selected_renderer_index = 0
        self.heatvision_renderer = HeatvisionRenderer(mqtt_bridge)
        self.space_operation = SpaceOperationRenderer()
        self.renderers: list[renderer.Renderer] = [
            self.space_operation
            # self.heatvision_renderer,
            # renderer.AnimatedGifRenderer(self.SHOOTER_PATH),
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
            frame_start = time.monotonic()

            offscreen_canvas.Clear()
            self.renderers[self.selected_renderer_index].render(offscreen_canvas)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            frame_counter += 1
            
            frame_stop = time.monotonic()
            rendering_time = frame_stop - frame_start
            # Slow down to 60Hz if necessary
            time_to_pause = self.SIXTY_HERTZ - rendering_time
            if time_to_pause > 0:
                time.sleep(time_to_pause)

            # FPS metrics
            time_after_last_metrics = frame_stop - fps_last_timestamp
            if time_after_last_metrics > ONE_SECOND:
                secs_per_scene += 1
                fps_now = frame_counter - fps_last_frame
                print(f"FPS: {fps_now} ", end="\r")
                fps_last_timestamp = time.monotonic()
                fps_last_frame = frame_counter

        print("No more running :(")
    
    def exit(self) -> None:
        self.keep_running = False        
        for r in self.renderers:
            r.exit()


def main():
    mqtt_bridge = MqttBridge()
    shell = RendererShellThread(mqtt_bridge)

    def exit_listener(topic: str, message: str) -> None:
        print(f"Exit listener triggered. '{topic}' '{message}'")
        if topic == TOPIC_COMMAND_NAME:
            if message == "exit":
                shell.exit()
                mqtt_bridge.stop()

    mqtt_bridge.subscribe_with_cb(TOPIC_COMMAND_NAME, exit_listener)
    print(
        f"On topic '{TOPIC_COMMAND_NAME}' post '{EXIT_COMMAND_NAME}' to stop processing."
    )

    while shell.keep_running:
        time.sleep(0.1)
    print("All done.")


if __name__ == "__main__":
    main()
