import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions
from heat_renderer import HeatvisionRenderer
import threading
import paho.mqtt.client as mqtt
import renderer

ONE_SECOND = 1


class RendererShellThread:

    SHOOTER_PATH = "./shooter.gif"
    ROCKET_PATH = "./rocket_launch_vertical.gif"

    def __init__(self):
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
        self.heatvision_renderer = HeatvisionRenderer()
        self.renderers: list[renderer.Renderer] = [
            #  self.heatvision_renderer,
            #  renderer.AnimatedGifRenderer(self.SHOOTER_PATH),
            # renderer.RunTextRenderer("Ey!!!"),
            renderer.AnimatedGifRenderer(self.ROCKET_PATH),
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

    def handle_message(self, topic: str, text: str) -> None:
        self.heatvision_renderer.receive_heatvision_data(text)


class MqttBridge():

    TOPIC_COMMAND_NAME = "jniHome/services/heatvision1/command"
    HEATVISION_TOPIC_NAME = "jniHome/services/heatvision1/data"

    def __init__(self, shell: RendererShellThread):
        MQTT_SERVER_IP = "192.168.199.119"
        mqtt_client = mqtt.Client("CHANGE_ME_LATER")
        mqtt_client.connect(MQTT_SERVER_IP)
        print(f"Connected to MQTT({MQTT_SERVER_IP})...")
        print(f"Publish 'exit' to topic {MqttBridge.TOPIC_COMMAND_NAME}")
        mqtt_client.loop_start()
        mqtt_client.subscribe(MqttBridge.TOPIC_COMMAND_NAME)
        mqtt_client.subscribe(MqttBridge.HEATVISION_TOPIC_NAME)
        mqtt_client.on_message = self.on_message
        self.shell = shell
        self.mqtt_client = mqtt_client

    def on_message(self, client, userdata, message: mqtt.MQTTMessage) -> None:
        topic: str = str(message.topic)
        message_text: str = message.payload.decode("UTF-8")
        if topic == MqttBridge.TOPIC_COMMAND_NAME:
            print(f"Received command: {message_text}")
            if message_text == "exit":
                self.mqtt_client.disconnect()
                self.mqtt_client.loop_stop()
                self.shell.keep_running = False
        else:
            self.shell.handle_message(topic, message_text)


def main():
    shell = RendererShellThread()

    mqtt_bridge = MqttBridge(shell)
    while shell.keep_running:
        time.sleep(0.1)
    print("All done.")


if __name__ == '__main__':
    main()
