'''
/*
 * Copyright 2010-2017 Amazon.com, Inc. or its affiliates. All Rights Reserved.
 *
 * Licensed under the Apache License, Version 2.0 (the "License").
 * You may not use this file except in compliance with the License.
 * A copy of the License is located at
 *
 *  http://aws.amazon.com/apache2.0
 *
 * or in the "license" file accompanying this file. This file is distributed
 * on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either
 * express or implied. See the License for the specific language governing
 * permissions and limitations under the License.
 */
 '''

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time

message_counter = 0


def customCallback(client, userdata, message):
    global message_counter
    print("Received a new message: ")
    print(message.payload)
    print("from topic: ")
    print(message.topic)
    print("--------------\n\n")
    message_counter += 1


host = "a6ygioa4gqbri-ats.iot.eu-central-1.amazonaws.com"
rootCAPath = "root-CA.crt"
certificatePath = "space_operations.cert.pem"
privateKeyPath = "space_operations.private.key"
clientId = "test_space_operations_pub"  # client id must be in policy as client.
topic = "space_operation/buttons/button1"
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
mqtt_client.subscribe(topic, 1, customCallback)
print(f"Subscribed to '{topic}' and waiting for 2x messages...")

while message_counter < 2:
    time.sleep(0.1)
mqtt_client.disconnect()
print("All done")
