import behaviors


def on_session_started(session_started_request, session):
    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])

def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """
    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    return behaviors.get_help_response()

def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """
    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent['name']

    if intent_name == "PowerStateIntent":
        return behaviors.update_power_state(intent)
    elif intent_name == "BrightnessIntent":
        return behaviors.update_brightness(intent)
    elif intent_name == "ModeIntent":
        return behaviors.update_mode(intent)
    elif intent_name == "AMAZON.HelpIntent":
        return behaviors.get_help_response()
    elif intent_name == "AMAZON.CancelIntent" or \
        intent_name == "AMAZON.StopIntent":
        return behaviors.handle_session_end_request()

def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])