"""
Connection between the Raspberry Pi and the AWS IoT Shadow endpoint.
"""
import os
import logging
import time
import json
import argparse

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient, AWSIoTMQTTShadowClient

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
get_topic = "$aws/things/{0}/shadow/get".format(thingName)
update_topic = "$aws/things/{0}/shadow/update".format(thingName)

# Logger information
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
streamHandler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
streamHandler.setFormatter(formatter)
logger.addHandler(streamHandler)


class MyPaintingShadowClient():
    """
    Client to maintain a connection between the Raspberry Pi and the IoT
    Shadow. Updates LED lights through a Light object.
    """
    def __init__(self):
        self.light = Light()

        self._get_shadow_client()

        self.deviceShadowHandler = self.shadowClient.createShadowHandlerWithName(thingName, True)

    def _get_shadow_client(self):
        """
        Creates, configures, and sets AWSIoTMQTTShadowClient to communicate
        with AWS IoT Thing Shadow.

        Args:
            None
        Returns:
            AWSIoTMQTTShadowClient
        """
        self.shadowClient = AWSIoTMQTTShadowClient(clientId)
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

    def _update_shadow_callback(self, payload, response_status, token):
        """
        Callback after updating shadow. Logs new reported state from payload.
        If there is no payload, will except ValueError and exceptions and log.

        Args:
            payload: JSON dict of shadow state
            response_status: string
            token: string
        """
        logger.info(response_status)
        try:
            payload_dict = json.loads(payload)
            light_data = payload_dict['state']['reported']
            logger.info('reported_power_state: {}'.format(light_data.get('power_state')))
            logger.info('reported_brightness: {}'.format(light_data.get('brightness')))
            logger.info('reported_mode: {}'.format(light_data.get('mode')))
        except ValueError:
            logger.error('Value error')
            logger.info(payload)
        except Exception as e:
            logger.error(e.message)

    def _get_shadow_callback(self, payload, response_status, token):
        """
        Callback after getting shadow. Checks if Light object needs to be
        updated based off of the payload. Updates the lights and sends an
        update to the IoT shadow if Lights object needs to be updates. If
        there is no payload, will except ValueError and exceptions and log.

        Args:
            payload: JSON dict of shadow state
            response_status: string
            token: string
        """
        logger.info(response_status)
        try:
            payload_dict = json.loads(payload)
            light_data = payload_dict['state']['desired']
            if self.light.needs_updating(light_data):
                self.light.update_lights(light_data)
                reported_payload = {
                                       'state': {
                                           'reported': self.light.current_settings()
                                       }
                                   }
                JSON_payload = json.dumps(reported_payload)
                self.deviceShadowHandler.shadowUpdate(JSON_payload,
                                                      self._update_shadow_callback,
                                                      10)
        except ValueError:
            logger.error('Value error')
            logger.info(payload)
        except Exception as e:
            logger.error(e.message)

    def run_app(self, set_desired=False):
        """
        Connects to IoT Shadow through MQTT connection. Updates "reported"
        state of shadow with current settings. Updates "desired" state if
        set_desired is True. Gets Shadow state every one second and handles
        callback with _get_shadow_callback.

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
        if set_desired:
            start_payload['state']['desired'] = self.light.current_settings()
        JSON_payload = json.dumps(start_payload)
        self.deviceShadowHandler.shadowUpdate(JSON_payload,
                                              self._update_shadow_callback,
                                              10)
        while True:
            self.deviceShadowHandler.shadowGet(self._get_shadow_callback, 10)
            # self.shadowClient.subscribe(get_topic, 1, customCallback)
            time.sleep(1)

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

    def _reconnect(self):
        """
        Reestablishes MQTT connection.

        Args:
            None
        """
        self.shadowClient.disconnect()
        self.shadowClient.connect()


def main(set_desired):
    """
    Starts shadow client and starts listening to shadow.

    Args:
        None
    """
    my_painting_shadow_client = MyPaintingShadowClient()
    # set desired state upon initial start up.
    my_painting_shadow_client.run_app(set_desired)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Decide to update desired '
                                                 'state upon start up')
    parser.add_argument('--set_desired', dest='set_desired', action='store_true')
    args = parser.parse_args()
    set_desired = args.set_desired
    main(set_desired)
