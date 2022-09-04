from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
from typing import Callable
import time


class AwsButtonListener():

    TOPIC_BUTTON1 = "space_operation/buttons/button1"
    
    def __init__(self, cb: Callable[[str, str], None] ) -> None:
        host = "a6ygioa4gqbri-ats.iot.eu-central-1.amazonaws.com"
        rootCAPath = "root-CA.crt"
        certificatePath = "space_operations.cert.pem"
        privateKeyPath = "space_operations.private.key"
        clientId = "test_space_operations_pub"  # client id must be in policy as client.
        port = 8883

        # Init AWSIoTMQTTClient
        mqtt_client = AWSIoTMQTTClient(clientId)
        mqtt_client.configureEndpoint(host, port)
        mqtt_client.configureCredentials(rootCAPath, privateKeyPath, certificatePath)

        # AWSIoTMQTTClient connection configuration
        mqtt_client.configureAutoReconnectBackoffTime(1, 32, 20)
        mqtt_client.configureOfflinePublishQueueing(-1)  # Infinite offline Publish queueing
        mqtt_client.configureDrainingFrequency(2)  # Draining: 2 Hz
        mqtt_client.configureConnectDisconnectTimeout(10)  # 10 sec
        mqtt_client.configureMQTTOperationTimeout(5)  # 5 sec

        # Connect and subscribe to AWS IoT
        print("Trying to conenct...")
        mqtt_client.connect()
        print("Should be connected.")

        def customCallback(client, userdata, message):
            topic = message.topic
            message_text = str(message.payload) 
            cb(topic, message_text)

        mqtt_client.subscribe(self.TOPIC_BUTTON1, 1, customCallback)
        print(f"Subscribed to '{self.TOPIC_BUTTON1}'")
        self.mqtt_client = mqtt_client
        
    def disconnect(self) -> None:
        print("Disconnecting...")
        self.mqtt_client.disconnect()


message_counter = 0
listener: AwsButtonListener | None = None


def main() -> None:
    global listener

    def topic_callback(topic: str, message: str) -> None:
        global listener
        global message_counter
        print(f"Received message on topic '{topic}'")
        message_counter += 1

    listener = AwsButtonListener(topic_callback)
    print("Waiting for messages...")
     
    while message_counter < 2:
        time.sleep(0.1)
    listener.disconnect()
    print("All done")


if __name__ == "__main__":
    main()
