"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import pymongo
#import twilio

uri = 'mongodb://cwmason:Capstone2017@ec2-34-201-51-167.compute-1.amazonaws.com'
client = None


# --------------- Helpers that build all of the responses ----------------------

def build_speechlet_response(title, output, reprompt_text, should_end_session):
    return {
        'outputSpeech': {
            'type': 'PlainText',
            'text': output
        },
        'card': {
            'type': 'Simple',
            'title': "SessionSpeechlet - " + title,
            'content': "SessionSpeechlet - " + output
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
def load_client():
    return client['saucybot']


def can_recipe_be_made(intent, session):
    """ Checks if the recipe is in the Cookbook
        Checks if the Pantry contains all necessary ingredients
    """
    db = load_client()

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Recipe' in intent['slots']:
        requested_recipe = intent['slots']['Recipe']['value']

        #missing_flag = False
        missing_ingredients = checkPantry(requested_recipe, db)

        #recipe_ingredients = ['spaghetti','meatballs']
        #pantry_ingredients = ['spaghetti','red sauce','meatballs','basil']

        '''for x in recipe_ingredients:
            if x not in pantry_ingredients:
                missing_flag = True
                missing_ingredients.append(x)

        if missing_flag:
            speech_output = "You are missing some ingredients. "
            for x in missing_ingredients:
                speech_output += x + ", "
            speech_output = speech_output[:-2]  # cut trailing comma
            reprompt_text = speech_output
        '''
        if missing.pop() == "Recipe not in Cookbook":
            print 'Hello'
        else:
            speech_output = "You have all the ingredients to make that recipe."
            reprompt_text = "You have all the ingredients to make that recipe."

    else:
        speech_output = "Please specify a recipe."
        reprompt_text = "You need to specify a recipe that you would like to make."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_welcome_response():
    """ If we wanted to initialize the session to have some attributes we could
    add those here
    """

    session_attributes = {}
    card_title = "Welcome"
    speech_output = "Welcome to the Alexa Skills Kit sample. " \
                    "Please tell me your favorite color by saying, " \
                    "my favorite color is red"
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "Please tell me your favorite color by saying, " \
                    "my favorite color is red."
    should_end_session = False
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def handle_session_end_request():
    card_title = "Session Ended"
    speech_output = "Thank you for trying the Alexa Skills Kit sample. " \
                    "Have a nice day! "
    # Setting this to true ends the session and exits the skill.
    should_end_session = True
    return build_response({}, build_speechlet_response(
        card_title, speech_output, None, should_end_session))


def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def set_color_in_session(intent, session):
    """ Sets the color in the session and prepares the speech to reply to the
    user.
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Color' in intent['slots']:
        favorite_color = intent['slots']['Color']['value']
        session_attributes = create_favorite_color_attributes(favorite_color)
        speech_output = "I now know your favorite color is " + \
                        favorite_color + \
                        ". You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
        reprompt_text = "You can ask me your favorite color by saying, " \
                        "what's my favorite color?"
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "Please try again."
        reprompt_text = "I'm not sure what your favorite color is. " \
                        "You can tell me your favorite color by saying, " \
                        "my favorite color is red."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_color_from_session(intent, session):
    session_attributes = {}
    reprompt_text = None

    if session.get('attributes', {}) and "favoriteColor" in session.get('attributes', {}):
        favorite_color = session['attributes']['favoriteColor']
        speech_output = "Your favorite color is " + favorite_color + \
                        ". Goodbye."
        should_end_session = True
    else:
        speech_output = "I'm not sure what your favorite color is. " \
                        "You can say, my favorite color is red."
        should_end_session = False

    # Setting reprompt_text to None signifies that we do not want to reprompt
    # the user. If the user does not respond or says something that is not
    # understood, the session will end.
    return build_response(session_attributes, build_speechlet_response(
        intent['name'], speech_output, reprompt_text, should_end_session))


# --------------- Events ------------------

def on_session_started(session_started_request, session):
    """ Called when the session starts """

    print("on_session_started requestId=" + session_started_request['requestId']
          + ", sessionId=" + session['sessionId'])
    client = pymongo.MongoClient(uri)
    return client


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

    # Dispatch to your skill's intent handlers
    if intent_name == "MyColorIsIntent":
        return set_color_in_session(intent, session)
    elif intent_name == "WhatsMyColorIntent":
        return get_color_from_session(intent, session)
    elif intent_name == "AMAZON.HelpIntent":
        return get_welcome_response()
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session, mongo_client):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    mongo_client.close()


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
        db1 = on_session_started({'requestId': event['request']['requestId']},
                           event['session'])

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'], client)


# ------------------ Database Methods --------------------------

def addIngredient(ing, db):
    return db.pantry.insert({'ingredient': ing})


def removeIngredient(ing, db):
    return db.pantry.remove({'ingredient': ing})


def ingredientSearch(ingredient, db):
    return bool(db.pantry.find_one({'ingredient': ingredient}))


def recipeSearch(recipe, db):
    return bool(db.cookbook.find_one({'name': recipe}))


def recipeIngredients(recipe, db):
    # Returns None if recipe not in cookbook, list of its ingredients if it is
    try:
        ings = list(db.cookbook.find({'name': recipe})).pop()
        ingredients = ings['ingredients']
    except:
        return None
    return ingredients


def checkPantry(recipe, db):
    # Returns list of None if you have everything for recipe
    # Returns list containing string 'Recipe not in Cookbook' if not in cookbook
    # Returns list of missing ingredients if those exist
    missing = []
    ingredients = recipeIngredients(recipe, db)
    if ingredients is None:
        missing.append('Recipe not in Cookbook')
        return missing
    for item in ingredients:
        if (ingredientSearch(item, db)) == False:
            missing.append(item)
    return missing


def searchCookbookOn(tags, db):
    # Search cookbook based on whatever list of tags are specified by user
    # Either returns a list of recipe names or empty list if none match the tag
    recipes = []
    recs = db.cookbook.find({'tags': {'$in': tags}})
    for item in recs:
        recipes.append(item['name'])
    return recipes


def searchCookbookAll(db):
    # For the 'what can I make' scenario. Looks at all available ingredients
    # and either returns list of recipes to make or None
    recipes = []
    try:
        recs = db.cookbook.find({})
        for item in recs:
            if len(checkPantry(item['name'], db)) == 0:
                recipes.append(item['name'])
    except:
        print ('Something wrong in try/except #1')
        return None
    return recipes
