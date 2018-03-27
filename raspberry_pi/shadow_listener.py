import os
import logging
import time
import json

from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTShadowClient

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
    def __init__(self):
        self.light = Light()

        self._get_shadow_client()
        self.is_connected = False

        self.deviceShadowHandler = self.shadowClient.createShadowHandlerWithName(thingName, True)


    def _get_shadow_client(self):
        self.shadowClient = AWSIoTMQTTShadowClient(clientId)
        self.shadowClient.configureEndpoint(host, port)
        self.shadowClient.configureCredentials(rootCAPath,
                                               privateKeyPath,
                                               certificatePath)
        self.shadowClient.configureAutoReconnectBackoffTime(1, 32, 20)
        self.shadowClient.configureConnectDisconnectTimeout(10)
        self.shadowClient.configureMQTTOperationTimeout(5)
        self.shadowClient.onOnline = self._on_online
        self.shadowClient.onOffline = self._on_offline
        return self.shadowClient

    def _update_shadow_callback(self, payload, response_status, token):
        logger.info(response_status)
        try:
            payload_dict = json.loads(payload)
            light_data = payload_dict['state']['reported']
            print('reported_power_state: {}'.format(light_data.get('power_state')))
            print('reported_brightness: {}'.format(light_data.get('brightness')))
            print('reported_mode: {}'.format(light_data.get('mode')))
        except:
            pass

    # Shadow callback from AWS IOT ShadowGet
    def _get_shadow_callback(self, payload, response_status, token):
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
        except:
            # self._reconnect()
            pass

    def run_app(self, first_time=False):
        self.shadowClient.connect()
        self.is_connected = True
        start_payload = {
                            'state': {
                                'reported': self.light.current_settings()
                            }
                        }
        if first_time:
            start_payload['state']['desired'] = self.light.current_settings()
        JSON_payload = json.dumps(start_payload)
        self.deviceShadowHandler.shadowUpdate(JSON_payload,
                                              self._update_shadow_callback,
                                              10)
        while self.is_connected:
            self.deviceShadowHandler.shadowGet(self._get_shadow_callback, 10)
            time.sleep(1)

    def _on_online(self):
        print("ON ONLINE")

    def _on_offline(self):
        print("ON OFFLINE")
        self._reconnect()

    def _reconnect(self):
        self.shadowClient.disconnect()
        self.is_connected = False

        self.shadowClient.connect()
        self.run_app()


def main():
    my_painting_shadow_client = MyPaintingShadowClient()
    my_painting_shadow_client.run_app(first_time=True)


if __name__ == '__main__':
    main()
