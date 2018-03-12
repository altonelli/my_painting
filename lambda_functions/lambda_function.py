import os

import events

alexa_id = os.environ.get('AWS_ALEXA_SKILLS_KIT_ID')

def lambda_handler(event, context):
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])
    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    if (event['session']['application']['applicationId'] !=
            "amzn1.ask.skill.{0}".format(alexa_id)):
        print("amzn1.ask.skill.{0}".format(alexa_id))
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
