import time
from typing import Protocol
from heatvision.mqtt_bridge import MqttBridge


class DataCollector(Protocol):
    def release(self) -> str | None:
        ...


class MqttDataCollector(DataCollector):

    TOPIC_DATA_NAME = "jniHome/services/heatvision1/data"
    
    def __init__(self, mqtt_bridge: MqttBridge) -> None:
        self.keep_alive = True
        self.data: str | None = None
        self.last_date_timestamp: float | None = None

        def handle_message(topic: str, message: str) -> None:
            self.store(message)

        mqtt_bridge.subscribe_with_cb(self.TOPIC_DATA_NAME, handle_message)

    def store(self, text: str) -> None:
        self.last_date_timestamp = time.monotonic()
        self.data = text

    def release(self) -> str | None:
        if self.data is not None:
            if self.last_date_timestamp is not None:
                time_passed = time.monotonic() - self.last_date_timestamp
                if time_passed > 1:
                    self.data = None
                    self.last_date_timestamp = None
            else:
                self.data = None
        return self.data
