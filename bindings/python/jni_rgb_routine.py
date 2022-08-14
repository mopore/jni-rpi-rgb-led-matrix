import time
from rgbmatrix import RGBMatrix, RGBMatrixOptions
import threading
import paho.mqtt.client as mqtt
import renderer


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

        self.renderer_counter = 0
		self.renderers: list[renderer.Renderer] = [
            renderer.AnimatedGifRenderer(RendererShellThread.SHOOTER_PATH),
            renderer.RunTextRenderer("Ey!!!"),
            renderer.HeatDisplayRenderer()
        ]

        threading.Thread(target=self.run).start()

    def run(self) -> None:
        offscreen_canvas = self.matrix.CreateFrameCanvas()
        frame_counter = 0
        while self.keep_running:
            offscreen_canvas.Clear()
            self.renderers[self.renderer_counter].render(offscreen_canvas)
            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)
            frame_counter += 1
            if frame_counter % 100 == 0:
                self.renderer_counter += 1
                if self.renderer_counter == 3:
                    self.renderer_counter = 0
                print(f"Switching renderer at Frame No. {frame_counter}")
        print("No more running :(")


class MqttBridge():

    TOPIC_COMMAND_NAME = "test/zero/command"

    def __init__(self, shell: RendererShellThread):
        MQTT_SERVER_IP = "192.168.199.119"
        mqtt_client = mqtt.Client("CHANGE_ME_LATER")
        mqtt_client.connect(MQTT_SERVER_IP)
        print(f"Connected to MQTT({MQTT_SERVER_IP})...")
        print(f"Publish 'exit' to topic {MqttBridge.TOPIC_COMMAND_NAME}")
        mqtt_client.loop_start()
        mqtt_client.subscribe(MqttBridge.TOPIC_COMMAND_NAME)
        mqtt_client.on_message = self.on_message
        self.shell = shell
        self.mqtt_client = mqtt_client

    def on_message(self, client, userdata, message: mqtt.MQTTMessage) -> None:
        topic: str = str(message.topic)
        command: str = message.payload.decode("UTF-8")
        if topic == MqttBridge.TOPIC_COMMAND_NAME:
            print(f"Received command: {command}")
            if command == "exit":
                self.mqtt_client.disconnect()
                self.mqtt_client.loop_stop()
                self.shell.keep_running = False


def main():
    shell = RendererShellThread()

    mqtt_bridge = MqttBridge(shell)
    while shell.keep_running:
        time.sleep(0.1)
    print("All done.")
                

if __name__ == '__main__':
    main()
