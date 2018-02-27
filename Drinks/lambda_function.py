"""
This is an Alexa Skill for mixed drinks.
Authors:
- Galina Belolipetski
- Saad siddiqui
- Jose Canahui
"""

from __future__ import print_function

from botocore.vendored import requests
from pprint import pprint

# Helper function: Given a drink, get the ingredients in an array
def getIngredients(requestedDrink):
    ingredientsList = []
    for index in range (1, 12):
        if (requestedDrink["strIngredient%s" % (str(index))] == ""):
            return ingredientsList
        else: #Get this to list things as ing1, ing2, ing3, and ing4
            measurement = requestedDrink["strMeasure%s" % str(index)]
            ingname = requestedDrink["strIngredient%s" % str(index)]
            if (measurement == "\n"):
                ingredient = ingname
            else:
                if "\n" in measurement:
                    ingredient = measurement[:len(measurement) - 1] + \
                    " of " + ingname
                else:
                    ingredient = measurement + " of " + ingname
            ingredientsList.append(ingredient)
    #print("INGREDIENTS: " + ingredientsList)
    return ingredientsList

#Listing the ingredients
def listIngredients(requestedDrink):
    #print("Here are the ingredients you need to make ", requestedDrink["strDrink"])
    drinkIngredients = getIngredients(requestedDrink)
    ingReport = ""
    for index in range(0, len(drinkIngredients)):
        if index == len(drinkIngredients) - 1:
            ingReport = ingReport + " and " + drinkIngredients[index] +"."
        else:
            if index == len(drinkIngredients):
                ingReport = ingReport + drinkIngredients[index]
            else:
                ingReport = ingReport + drinkIngredients[index] + ", "
    return ingReport

#Listing the instructions
def listInstructions(requestedDrink):
    #print("Here are the instructions you need to make ", requestedDrink["strDrink"])
    instructions = requestedDrink["strInstructions"]
    return instructions

#Returns one drink when
def multipleDrinksFound(drinksArray):
    #print("We found multiple drinks with that name. Here they are!")
    for drink in drinksArray:
        print(drink["strDrink"])
    specificDrink = raw_input("Which drink did you want to see?\n")
    for drink in drinksArray:                   # For each drink
        if drink["strDrink"] == specificDrink:  # If the drink is found
            return drink
    return None                                 # If not found, return None

def getDrinkInformation(drink):
    if (drink == None):                                 # Drink given was null
        return "You need to specify which drink you want to make."

    DRINK = None #Global variable to hold the drink that is being instructed on
    drink.replace(" ", "_")
    response = requests.get("http://www.thecocktaildb.com/api/json/v1/1/search.php?s=%s" % (drink))
    json_res = response.json()
    drinksArray = json_res["drinks"]
    if (drinksArray == None):                           # No options
        return "Sorry, but we couldn't find that drink."
    #elif len(drinksArray) > 1:                          # More than 1 option
    #    DRINK = multipleDrinksFound(drinksArray)
    else:                                               # Only 1 option
        DRINK = drinksArray[0]

    return listIngredients(DRINK) + " " + listInstructions(DRINK)





# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': title,
            'content': output
        },
        'reprompt': {
            'outputSpeech': {
                'type': 'PlainText',
                'text': reprompt_text
            }
        },
        'shouldEndSession': should_end_session
    }


def build_response(session_attributes, speechlet_response):
    return {
        'version': '1.0',
        'sessionAttributes': session_attributes,
        'response': speechlet_response
    }


# --------------- Functions that control the skill's behavior ------------------

def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Bartender Skill. " \
                    "What do you want to make?"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me what drink you would like to make?"
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you. Enjoy your drink responsibly."
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def search_bartender(intent, session):
    """ Requests the DB to find the drink and get a recipe.
    """

    card_title = "Recipe"
    session_attributes = {}
    should_end_session = True

    # If the slot is filled, else if the slot is not filled (with a drink name)
    if 'Drink' in intent['slots'] and 'value' in intent['slots']['Drink']:
        speech_output = getDrinkInformation(intent['slots']['Drink']['value'])
        reprompt_text = "That drink is not available. Please try another drink."
    else:
        speech_output = "I'm not sure what drink you want me to look up. " \
                        "Please try again."
        reprompt_text = "I'm not sure what drink you want me to look up. " \
                        "You can ask me for a specific drink by saying, " \
                        "A blue margarita. "
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])


def on_launch(launch_request, session):
    """ Called when the user launches the skill without specifying what they
    want
    """

    print("on_launch requestId=" + launch_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # Dispatch to your skill's launch
    return get_welcome_response()


def on_intent(intent_request, session):
    """ Called when the user specifies an intent for this skill """

    print("on_intent requestId=" + intent_request['requestId'] +
          ", sessionId=" + session['sessionId'])

    intent = intent_request['intent']
    intent_name = intent_request['intent']['name']

    # Drinks intents
    if intent_name == "LookUpRecipe":
        return search_bartender(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    # add cleanup logic here


# --------------- Main handler ------------------

def lambda_handler(event, context):
    """ Route the incoming request based on type (LaunchRequest, IntentRequest,
    etc.) The JSON body of the request is provided in the event parameter.
    """
    print("event.session.application.applicationId=" +
          event['session']['application']['applicationId'])

    """
    Uncomment this if statement and populate with your skill's application ID to
    prevent someone else from configuring a skill that sends requests to this
    function.
    """
    # if (event['session']['application']['applicationId'] !=
    #         "amzn1.echo-sdk-ams.app.[unique-value-here]"):
    #     raise ValueError("Invalid Application ID")

    if event['session']['new']:
        on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'])
