import response_builders
import shadow_updater

session_attributes = {}
should_end_session = True
reprompt_text = None

def get_help_response():
    card_title = "Welcome"
    speech_output = "Please give a command for your painting lights."

    response = response_builders.build_response(session_attributes,
        response_builders.build_speechlet_response(card_title,
        speech_output, reprompt_text, should_end_session))
    return response

def update_power_state(intent):
    card_title = "Power"

    power_state = intent.get('slots',{}).get('PowerState',{}).get('value')
    if power_state and (power_state.upper() == 'ON' or power_state.upper() == 'OFF'):
        speech_output = "Yes my lord."
        new_value_dict = {"power_state":power_state.upper()}
        shadow_updater.update_shadow(new_value_dict)
    else:
        speech_output = "I did not understand that. Please repeat your request."

    response = response_builders.build_response(session_attributes,
        response_builders.build_speechlet_response(card_title,
        speech_output, reprompt_text, should_end_session))
    return response

def update_brightness(intent):
    card_title = "Brightness"

    brightness = intent.get('slots',{}).get('Brightness',{}).get('value')

    if brightness:
        brightness = int(brightness)
        if brightness > 0 and brightness <= 100:
            speech_output = "Yes my lord."
            new_value_dict = {"brightness":brightness}
            shadow_updater.update_shadow(new_value_dict)
        elif brightness == 0:
            speech_output = "Yes my lord."
            new_value_dict = {"power_state":"OFF"}
            shadow_updater.update_shadow(new_value_dict)
        else:
            speech_output = "I'm sorry that value is not in the proper range. "\
                "Please give me a number between 0 and 100."
    else:
        speech_output = "I did not understand that. Please repeat your request."

    response = response_builders.build_response(session_attributes,
        response_builders.build_speechlet_response(card_title,
        speech_output, reprompt_text, should_end_session))
    return response

def update_mode(intent):
    card_title = "Mode"

    mode = intent.get('slots',{}).get('Mode',{}).get('value')

    if mode and mode.upper() in {"STILL", "STATIC", "WAVE"}:
        if mode.upper() == "STILL":
            mode = "STATIC"
        speech_output = "Yes my lord."
        new_value_dict = {"mode":mode.upper()}
        shadow_updater.update_shadow(new_value_dict)
    else:
        speech_output = "I did not understand that. Please repeat your request."

    response = response_builders.build_response(session_attributes,
        response_builders.build_speechlet_response(card_title,
        speech_output, reprompt_text, should_end_session))
    return response