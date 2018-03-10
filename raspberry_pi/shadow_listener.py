from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient
from lights import Light
import os
import logging
import time
import json

# Shadow JSON schema:
#
# Name: MyPainting
# {
#	"state": {
#		"desired":{
#			"brightness":<int>,
#           "mode":<str>,
#           "power_state":<str>
#		}
#	}
# }

# Set variables from env

host = os.environ.get("AWS_IOT_MQTT_HOST")
port = os.environ.get("AWS_IOT_MQTT_PORT")
rootCAPath = os.environ.get("AWS_IOT_ROOT_CA_FILENAME")
certificatePath = os.environ.get("AWS_IOT_CERTIFICATE_FILENAME")
privateKeyPath = os.environ.get("AWS_IOT_PRIVATE_KEY_FILENAME")
publicKeyPath = os.environ.get("AWS_IOT_PUBLIC_KEY_FILENAME")
thingName = os.environ.get("AWS_IOT_MY_THING_NAME")
clientId = os.environ.get("AWS_IOT_MQTT_CLIENT_ID")

# Logger information
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)

# Get lights ready
light = Light()

# Shadow callback from AWS IOT
def shadow_callback(payload, response_status, token):
    logger.info(response_status)
    payload_dict = json.loads(payload)
    if light.needs_updating():
        light.update_lights()

def main():
     # Get lights ready
    light = Light()

    shadowClient = None

    shadowClient = AWSIoTMQTTShadowClient(clientId)
    shadowClient.configureEndpoint(host, port)
    shadowClient.configureCredentials(rootCAPath,
                                      privateKeyPath,
                                      certificatePath)
    shadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
    shadowClient.configureMQTTOperationTimeout(10)
    shadowClient.configureMQTTOperationTimeout(5)
    shadowClient.connect()

    deviceShadowHandler = shadowClient.createShadowHandlerWithName(thingName, True)

    deviceShadowHandler.shadowRegisterDeltaCallback(shadow_callback)

if __name__ == '__main__':
    main()




