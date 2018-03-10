import events
import logging

logger = logging.getLogger(__name__)

def lambda_handler(event, context):
    logger.info("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.echo-sdk-ams.app.{0}".format(AWS_ALEXA_SKILLS_KIT_ID)):
        raise ValueError("Invalid Application ID")

    # if event['session']['new']:
    #     events.on_session_started({'requestId': event['request']['requestId']},
    #                        event['session'])

    request_type = event['request']['type']

    if request_type == "LaunchRequest":
        return events.on_launch(event['request'], event['session'])
    elif request_type == "IntentRequest":
        return events.on_intent(event['request'], event['session'])
    # elif request_type == "SessionEndedRequest":
    #     return on_session_ended(event['request'], event['session'])
