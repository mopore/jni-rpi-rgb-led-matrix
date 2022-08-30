from typing import Callable
import paho.mqtt.client as mqtt
import time


class MqttBridge():

    def __init__(self, mqtt_server: str = "192.168.199.119"):
        mqtt_client = mqtt.Client("CHANGE_ME_LATER")
        mqtt_client.connect(mqtt_server)
        print(f"Connected to MQTT({mqtt_server})...")
        mqtt_client.loop_start()
        mqtt_client.on_message = self.on_message
        self.mqtt_client = mqtt_client
        self.topic_cbs: dict[str, Callable[[str, str], None]] = {}

    def on_message(self, client, userdata, message: mqtt.MQTTMessage) -> None:
        topic: str = str(message.topic)
        message_text: str = message.payload.decode("UTF-8")
        cb = self.topic_cbs[topic]
        if cb is not None:
            cb(topic, message_text)

    def publish(self, topic: str, message: str) -> None:
        self.mqtt_client.publish(topic, message)
    
    def subscribe_with_cb(self, topic: str, cb: Callable[[str, str], None]):
        self.mqtt_client.subscribe(topic)
        self.topic_cbs[topic] = cb

    def stop(self) -> None:
        self.mqtt_client.disconnect()


message_received = False


def main():
    print("Starting...")
    mqtt_client = MqttBridge("localhost")

    def local_callback(topic: str, message: str) -> None:
        global message_received
        print(f"Topic: {topic}, Message: {message}")
        message_received = True
    
    mqtt_client.subscribe_with_cb("test/lala", local_callback)
    time.sleep(1)
    mqtt_client.publish("test/lala", "test")
    while not message_received:
        print("Waiting for message to be received...")
        time.sleep(1)
    
    mqtt_client.stop()
    print("All done")

    
if __name__ == '__main__':
    main()
