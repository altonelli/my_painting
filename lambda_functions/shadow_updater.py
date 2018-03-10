
from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
import os
import logging
import time
import json

logger = loggin.getLogger(__name__)

clientId = os.environ.get('AWS_IOT_MQTT_CLIENT_ID')
thingName = os.environ.get("AWS_IOT_MY_THING_NAME")
host = os.environ.get("AWS_IOT_MQTT_HOST")
port = os.environ.get("AWS_IOT_MQTT_PORT_UPDATE")

def shadow_update_callback(payload, response_status, token):
    if response_status == "timeout":
        logger.info("Update request " + token + " time out!")

    if response_status == "accepted":
        payloadDict = json.loads(payload)
        logger.info("Update request with token: " + token + " accepted!")
        logger.info("PowerState: " + str(payloadDict["state"]["desired"]["power_sate"]))
        logger.info("Brightness: " + str(payloadDict["state"]["desired"]["brightness"]))
        logger.info("Mode: " + str(payloadDict["state"]["desired"]["mode"]))

    if response_status == "rejected":
        logger.info("Update request " + token + " rejected!")

def update_shadow(new_value_dict):
    topic = "$aws/things/{}/shadow/update".format(thingName)
    payload_dict = {
        "state": {
            "desired" : new_value_dict
        }
    }
    JSON_payload = json.dumps(payload_dict)

    shadow_client = AWSIoTMQTTShadowClient(clientId)
    shadow_client.configureEndpoint(host, port)
    shadow_client.connect()
    myMQTTClient.publish(topic, JSON_payload, 0)
    # shandow_handler = shadow_client.createShadowHandlerWithName(thingName, False)
    # shandow_handler.shadowUpdate(JSON_payload, shadow_update_callback, 5)
    myMQTTClient.disconnect()


    # myMQTTClient.connect()
    # myMQTTClient.publish("myTopic", "myPayload", 0)
    # myMQTTClient.subscribe("myTopic", 1, customCallback)
    # myMQTTClient.unsubscribe("myTopic")
    # myMQTTClient.disconnect()

