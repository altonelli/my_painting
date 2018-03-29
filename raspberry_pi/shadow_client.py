"""
Connection between the Raspberry Pi and the AWS IoT Shadow endpoint.
"""
import os
import logging
import time
import json
import argparse

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient

from lights import Light

# Shadow JSON schema:
#
# Name: my_painting
# {
#	"state": {
#		"desired":{
#			"brightness":<int>,
#           "power_state":<str>
#		},
#       "reported":{
#           "brightness":<int>,
#           "power_state":<str>
#		}
#	 }
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

# topic strings
update_topic = "$aws/things/{0}/shadow/update".format(thingName)
update_docs_topic = "$aws/things/{0}/shadow/update/documents".format(thingName)

# Logger information
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


class MyPaintingMQTTClient():
    """
    Client to maintain a connection between the Raspberry Pi and the IoT
    Shadow. Updates LED lights through a Light object.
    """
    def __init__(self):
        self.light = Light()

        self._get_shadow_client()

    def _get_shadow_client(self):
        """
        Creates, configures, and sets AWSIoTMQTTClient to communicate
        with AWS IoT Thing.

        Args:
            None
        Returns:
            AWSIoTMQTTClient
        """
        self.shadowClient = AWSIoTMQTTClient(clientId)

        self.shadowClient.configureEndpoint(host, port)
        self.shadowClient.configureCredentials(rootCAPath,
                                               privateKeyPath,
                                               certificatePath)
        self.shadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
        self.shadowClient.configureConnectDisconnectTimeout(10)
        self.shadowClient.configureMQTTOperationTimeout(1)
        
        return self.shadowClient

    def _subscribe_update_callback(self, client, userdata, message):
        """
        Callback after subscribe to update documents topic. Retrieves the
        payload from the MQTTMessage and checks if Light object needs to
        be updated. If Lights object needs to be updated, updates the lights
        and sends an update to the IoT shadow. Will except ValueError and
        exceptions and log if payload is missing.

        Client and Userdata may be deprecated in the future.

        Args:
            client: string
            userdata: string
            message: MQTTMessage instance
        """
        logger.info('Message recieved from {} topic'.format(message.topic))
        payload = message.payload
        try:
            payload_dict = json.loads(payload)
            light_data = payload_dict['current']['state']['desired']
            if self.light.needs_updating(light_data):
                self.light.update_lights(light_data)
                reported_payload = {
                                       'state': {
                                           'reported': self.light.current_settings()
                                       }
                                   }
                JSON_payload = json.dumps(reported_payload)
                self.shadowClient.publish(update_topic, JSON_payload, 0)
        except ValueError:
            logger.error('Value error')
            logger.info(payload)
        except Exception as e:
            logger.error(e.message)

    def run_app(self, set_desired_state=False):
        """
        Connects to IoT Shadow through MQTT connection. Updates state of
        shadow with current light settings to update topic. Subscribes to
        update/documents topic of thing shadow from update/documents topic
        and handles callback with _subscribe_update_callback.

        Args:
            set_desired: boolean to send update to desired state
        """
        self.shadowClient.connect()
        start_payload = {
                            'state': {
                                'reported': self.light.current_settings(),
                                'desired': self.light.current_settings()
                            }
                        }
        JSON_payload = json.dumps(start_payload)
        self.shadowClient.publish(update_topic, JSON_payload, 0)
        self.shadowClient.subscribe(update_docs_topic, 1,
                                    self._subscribe_update_callback)
        while True:
            pass


def main():
    """
    Starts shadow client and subscribes to shadow.

    Args:
        None
    """
    my_painting_mqtt_client = MyPaintingMQTTClient()
    my_painting_mqtt_client.run_app()


if __name__ == '__main__':
    main()
