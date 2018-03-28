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
        # Client configurations
        self.shadowClient.configureEndpoint(host, port)
        self.shadowClient.configureCredentials(rootCAPath,
                                               privateKeyPath,
                                               certificatePath)
        self.shadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
        self.shadowClient.configureConnectDisconnectTimeout(10)
        self.shadowClient.configureMQTTOperationTimeout(1)
        # Set online/offline callbacks before connecting
        self.shadowClient.onOnline = self._on_online
        self.shadowClient.onOffline = self._on_offline
        return self.shadowClient

    def _update_subscribe_callback(self, client, userdata, message):
        """
        Callback after subscribe to udate documents topic. Retrieves the
        payload from the MQTTMessage and checks if Light object needs to
        be updated. If Lights object needs to be updated, updates the lights
        and sends an update to the IoT shadow. Will except ValueError and
        exceptions and log.

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
        Connects to IoT Shadow through MQTT connection. Updates "reported"
        state of shadow with current settings. Updates "desired" state if
        set_desired is True. Gets Shadow state from update/documents topic
        handles callback with _update_subscribe_callback.

        Args:
            set_desired: boolean to send update to desired state
        """
        self.shadowClient.connect()
        start_payload = {
                            'state': {
                                'reported': self.light.current_settings()
                            }
                        }
        # Only update the desired state if true
        if set_desired_state:
            start_payload['state']['desired'] = self.light.current_settings()
        JSON_payload = json.dumps(start_payload)
        self.shadowClient.publish(update_topic, JSON_payload, 0)
        self.shadowClient.subscribe(update_docs_topic, 1,
                                    self._update_subscribe_callback)
        while True:
            pass

    def _on_online(self):
        """
        Logs when connection is online.

        Args:
            None
        """
        logger.info("ONLINE")

    def _on_offline(self):
        """
        Logs when connection is offline.

        Args:
            None
        """
        logger.info("OFFLINE")


def main(set_desired_state):
    """
    Starts shadow client and starts listening to shadow.

    Args:
        None
    """
    my_painting_mqtt_client = MyPaintingMQTTClient()
    # set desired state upon initial start up.
    my_painting_mqtt_client.run_app(set_desired_state)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decide to update desired '
                                                 'state upon start up')
    parser.add_argument('--set_desired', dest='set_desired', action='store_true')
    args = parser.parse_args()
    set_desired_state = args.set_desired
    main(set_desired_state)
