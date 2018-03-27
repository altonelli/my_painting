"""
Behaviors the skill will take based on the intent of the request. Calls on
shadow updater to update IoT shadow accordingly and response builders to
build a response message. If using sessions, session data should be
handled here.
"""
import response_builders
import shadow_connection

# Not using session data or reprompt texts, so these are standard defaults.
# These should be set in the behaviors functions as they are based on behavior of intent.
session_attributes = {}
should_end_session = True
reprompt_text = None

def get_help_response():
    """
    Builds a help/welcome response.

    Args:
        None
    Returns:
        Python dict of response message
    """
    card_title = "Welcome"
    speech_output = "Please give a command for your painting lights."

    response = response_builders.build_response(session_attributes,
        response_builders.build_speechlet_response(card_title,
        speech_output, reprompt_text, should_end_session))
    return response

def update_power_state(intent):
    """
    Updates power state of IoT shadow. Builds a response confirming the update
    or requesting the user repeat the query if state is not "ON" or "OFF".

    Args:
        intent: Python dict of intent
    Returns:
        Python dict of response message
    """
    card_title = "Power"

    power_state = intent.get('slots',{}).get('PowerState',{}).get('value')
    if power_state and (power_state.upper() == 'ON' or \
                        power_state.upper() == 'OFF'):
        speech_output = "OK."
        new_value_dict = {"power_state":power_state.upper()}
        shadow_connection.update_shadow(new_value_dict)
    else:
        speech_output = "I did not understand that. Please repeat your request."

    response = response_builders.build_response(session_attributes,
        response_builders.build_speechlet_response(card_title,
        speech_output, reprompt_text, should_end_session))
    return response

def update_brightness(intent):
    """
    Updates brightness of IoT shadow. Builds a response confirming the update
    or requesting the user repeat the query if 0 <= brightness <= 100. If the
    requested brightness is zero, the power state of the shadow will be
    updated to "OFF" and the brightness will not be changed.

    Args:
        intent: Python dict of intent
    Returns:
        Python dict of response message
    """
    card_title = "Brightness"

    brightness = intent.get('slots',{}).get('Brightness',{}).get('value')

    if brightness:
        brightness = int(brightness)
        if brightness > 0 and brightness <= 100:
            speech_output = "Setting brightness to {}.".format(brightness)
            new_value_dict = {"brightness":brightness}
            shadow_connection.update_shadow(new_value_dict)
        elif brightness == 0:
            speech_output = "Turning off."
            new_value_dict = {"power_state":"OFF"}
            shadow_connection.update_shadow(new_value_dict)
        else:
            speech_output = "I'm sorry that value is not in the proper range. "\
                "Please give me a number between 0 and 100."
    else:
        speech_output = "I did not understand that. Please repeat your request."

    response = response_builders.build_response(session_attributes,
        response_builders.build_speechlet_response(card_title,
        speech_output, reprompt_text, should_end_session))
    return response

def handle_session_end_request():
    """
    Builds a response with a blank message and no session data. If using
    session data this function would specifically have session_attributes = {}
    and should_end_session = True.

    Args:
        None
    Returns:
        Python dict of response message
    """
    speech_output = None
    response = response_builders.build_response(session_attributes,
        response_builders.build_speechlet_response(card_title,
        speech_output, reprompt_text, should_end_session))
    return response
