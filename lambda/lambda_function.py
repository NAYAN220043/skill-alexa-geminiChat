# -*- coding: utf-8 -*-

import logging
import ask_sdk_core.utils as ask_utils
import requests
import json
import os
from dotenv import load_dotenv
from ask_sdk_core.skill_builder import SkillBuilder
from ask_sdk_core.dispatch_components import AbstractRequestHandler
from ask_sdk_core.dispatch_components import AbstractExceptionHandler
from ask_sdk_core.handler_input import HandlerInput

from ask_sdk_model import Response

load_dotenv()
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')
# API Endpoint URL
url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash-latest:generateContent?key={}".format(GOOGLE_API_KEY)

# Headers for the request
headers = {
    'Content-Type': 'application/json',
}

# Data (payload) for the POST request
data = {
    "contents": [{
        "role": "user",
        "parts": [{
            "text": ""
        }]
    }]
}

class LaunchRequestHandler(AbstractRequestHandler):
    """Handler for Skill Launch."""
    def can_handle(self, handler_input):
        return ask_utils.is_request_type("LaunchRequest")(handler_input)

    def handle(self, handler_input):
        data["contents"][0]["parts"][0]["text"] = "You will be my AI assistant. I will give you commands, and we will interact as I guide and train you."
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            text = (response_data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Text not found"))
            speak_output = text + " How can I help you?"
            response_text = {
                "role": "model",
                "parts": [{
                    "text": text
                }]
            }
            data["contents"].append(response_text)
        else:
            speak_output = "Error in the request."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )


class ChatIntentHandler(AbstractRequestHandler):
    """Handler for Chat Intent."""
    def can_handle(self, handler_input):
        return ask_utils.is_intent_name("ChatIntent")(handler_input)

    def handle(self, handler_input):
        query = handler_input.request_envelope.request.intent.slots["query"].value
        query_text = {
            "role": "user",
            "parts": [{
                "text": query
            }]
        }
        data["contents"].append(query_text)
        response = requests.post(url, json=data, headers=headers)
        if response.status_code == 200:
            response_data = response.json()
            text = (response_data.get("candidates", [{}])[0]
                .get("content", {})
                .get("parts", [{}])[0]
                .get("text", "Text not found"))
            speak_output = text
            response_text = {
                "role": "model",
                "parts": [{
                    "text": text
                }]
            }
            data["contents"].append(response_text)
        else:
            speak_output = "I couldn't get a response for your request."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask("Do you have any other questions?")
                .response
        )


class CancelOrStopIntentHandler(AbstractRequestHandler):
    """Single handler for Cancel and Stop Intent."""
    def can_handle(self, handler_input):
        return (ask_utils.is_intent_name("AMAZON.CancelIntent")(handler_input) or
                ask_utils.is_intent_name("AMAZON.StopIntent")(handler_input))

    def handle(self, handler_input):
        speak_output = "Goodbye!"

        return (
            handler_input.response_builder
                .speak(speak_output)
                .response
        )


class CatchAllExceptionHandler(AbstractExceptionHandler):
    """Generic error handling to capture any syntax or routing errors."""
    def can_handle(self, handler_input, exception):
        return True

    def handle(self, handler_input, exception):
        logger.error(exception, exc_info=True)

        speak_output = "Sorry, I had trouble doing what you asked. Please try again."

        return (
            handler_input.response_builder
                .speak(speak_output)
                .ask(speak_output)
                .response
        )

# The SkillBuilder object acts as the entry point for your skill
sb = SkillBuilder()

sb.add_request_handler(LaunchRequestHandler())
sb.add_request_handler(ChatIntentHandler())
sb.add_request_handler(CancelOrStopIntentHandler())
sb.add_exception_handler(CatchAllExceptionHandler())

lambda_handler = sb.lambda_handler()
