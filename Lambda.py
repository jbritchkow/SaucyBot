"""
This sample demonstrates a simple skill built with the Amazon Alexa Skills Kit.
The Intent Schema, Custom Slots, and Sample Utterances for this skill, as well
as testing instructions are located at http://amzn.to/1LzFrj6

For additional samples, visit the Alexa Skills Kit Getting Started guide at
http://amzn.to/1LGWsLG
"""

from __future__ import print_function
import pymongo
#from twilio.rest import Client

# For Twilio
#account_sid = "ACdeabec075c0137d4fb10755551afd4e4"
#auth_token = "d9756d7b452e88b2f1ba8532aeb508fb"
#twilio_client = Client(account_sid, auth_token)

# For MongoDB
uri = 'mongodb://cwmason:Capstone2017@ec2-34-201-51-167.compute-1.amazonaws.com'
mongo_client = None

# set this to true if Alexa is asking user to set a reminder
# false if Alexa is iterating through a list
# this way we can split the YES intent
reminderFlag = True


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


def set_session_attributes(index, length, arr):
    return {"curIndex": index, "length": length, "arr": arr}


# --------------- Functions that control the skill's behavior ------------------
def load_client():
    global mongo_client
    return mongo_client['saucybot']


def yes_handler(intent, session):
    """ Handler for when the user responds with Yes
        So far, this is only for sending a reminder
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if session.get('attributes', {}) and "reminder" in session.get('attributes', {}):
        requested_ingredient = session['attributes']['reminder']
        speech_output = "Okay, sending reminder."
        reprompt_text = "Reminder sent."
#        message = twilio_client.api.account.messages.create(to="+12154506570", from_="+12242315628", body="Remember to buy " + requested_ingredient + " at the store!")
    else:
        speech_output = "I don't understand what you mean."
        reprompt_text = speech_output

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def no_handler(intent, session):
    """ Handler for when the user responds with No
        So far, this is only for sending a reminder
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    speech_output = "Okay. Any other requests?"
    reprompt_text = speech_output

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def do_i_have_ingredient(intent, session):
    """ Checks the Pantry for given ingredient
    """

    db = load_client()
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Ingredient' in intent['slots']:
        requested_ingredient = intent['slots']['Ingredient']['value']
        hasIngredient = ingredientSearch(requested_ingredient, db)
        if hasIngredient:
            speech_output = "You have " + requested_ingredient + "."
            reprompt_text = speech_output
        else:
            speech_output = "You do not have " + requested_ingredient + ". "
            speech_output += "Would you like to set a reminder?"
            reprompt_text = "Would you like to set a reminder?"
            session_attributes = {"reminder": requested_ingredient}
    else:
        speech_output = "Please specify an ingredient."
        reprompt_text = "You need to specify an ingredient that you would like to check."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def picked_up_ingredient(intent, session):
    """ Adds an ingredient to the pantry
    """

    db = load_client()
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Ingredient' in intent['slots']:
        requested_ingredient = intent['slots']['Ingredient']['value']
        addIngredient(requested_ingredient,db)
        speech_output = requested_ingredient + "was added to the pantry."
        reprompt_text = requested_ingredient + "was successfully added to your pantry."
    else:
        speech_output = "Please specify an ingredient."
        reprompt_text = "You need to specify an ingredient that you just picked up."
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def out_of_ingredient(intent, session):
    """ Removes and ingredient from the Pantry
    """

    db = load_client()
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Ingredient' in intent['slots']:
        requested_ingredient = intent['slots']['Ingredient']['value']
        removeIngredient(requested_ingredient, db)
        speech_output = requested_ingredient + " was removed from the pantry."
        reprompt_text = requested_ingredient + " was successfully removed from your pantry."
    else:
        speech_output = "Please specify an ingredient."
        reprompt_text = "You need to specify an ingredient that you ran out of."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_recipes_from_tag(intent, session):
    """ Filters all recipes in the cookbook by the specified tag
        Returns list of all recipes that contain that tag
    """

    db = load_client()
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Tag' in intent['slots']:
        tag = intent['slots']['Tag']['value']
        recipes = searchCookbookOn([tag], db)
        numResults = len(recipes)

        if numResults == 0:
            speech_output = "There are no recipes with that tag."
            reprompt_text = speech_output
        else:
            session_attributes = set_session_attributes(0, numResults, recipes)
            speech_output = "The first result is " + recipes[0] + ". Use commands select, next, previous, start over, or stop to navigate the list."
            reprompt_text = "Possible commands are select, next, previous, start over, or stop."
    else:
        speech_output = "Please specify a tag."
        reprompt_text = "You need to specify a tag to filter the recipes."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def get_all_possible_recipes(intent, session):
    """ Returns all of the recipes that can be made in the individual's 
        cookbook given their current ingredients
    """
    db = load_client()
    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    recipes = searchCookbookAll(db)
    numResults = len(recipes)

    if recipes is None:
        speech_output = 'Cannot find recipes in your Cook book'
        reprompt_text = speech_output
    elif numResults == 0:
        speech_output = 'You do not have the ingredients to make anything in your Cook book'
        reprompt_text = speech_output
    else:
        session_attributes = set_session_attributes(0, numResults, recipes)
        speech_output = "The first result is " + recipes[0] + ". Use commands select, next, previous, start over, or stop to navigate the list."
        reprompt_text = "Possible commands are select, next, previous, start over, or stop."

    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def next_handler(intent, session):
    """ Handler for going to the next iteration in a list
        stores list, length of list, and current index in session attributes
        uses these attributes to navigate the list
    """

    card_title = intent['name']
    should_end_session = False

    if session.get('attributes', {}) and "arr" in session.get('attributes', {}):
        curIndex = session['attributes']['curIndex']
        curIndex += 1  # increment since we are going to the next item in list
        length = session['attributes']['length']
        arr = session['attributes']['arr']

        if curIndex >= length:  # end of list
            curIndex -= 1  # reset the index
            speech_output = "That was the last item."
            reprompt_text = "Possible commands are select, previous, start over, or stop."
        else:
            curItem = arr[curIndex]
            speech_output = curItem
            reprompt_text = "Possible commands are select, next, previous, start over, or stop."
    else:
        raise RuntimeError("Couldn't find list to iterate through")

    session_attributes = set_session_attributes(curIndex, length, arr)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def previous_handler(intent, session):
    """ Handler for going to the previous iteration in a list
        stores list, length of list, and current index in session attributes
        uses these attributes to navigate the list
    """

    card_title = intent['name']
    should_end_session = False

    if session.get('attributes', {}) and "arr" in session.get('attributes', {}):
        curIndex = session['attributes']['curIndex']
        curIndex -= 1  # decrement since we are going to the previous item in list
        length = session['attributes']['length']
        arr = session['attributes']['arr']

        if curIndex < 0:  # beginning of list
            curIndex += 1  # reset the index
            speech_output = "That was the first item."
            reprompt_text = "Possible commands are select, next, start over, or stop."
        else:
            curItem = arr[curIndex]
            speech_output = curItem
            reprompt_text = "Possible commands are select, next, previous, start over, or stop."
    else:
        raise RuntimeError("Couldn't find list to iterate through")

    session_attributes = set_session_attributes(curIndex, length, arr)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


def start_over_handler(intent, session):
    """ Handler for going to the first iteration in a list
        stores list, length of list, and current index in session attributes
        uses these attributes to navigate the list
    """

    card_title = intent['name']
    should_end_session = False

    if session.get('attributes', {}) and "arr" in session.get('attributes', {}):
        curIndex = 0  # go to first element of list since we are starting over
        length = session['attributes']['length']
        arr = session['attributes']['arr']

        curItem = arr[curIndex]
        speech_output = curItem
        reprompt_text = "Possible commands are select, next, previous, start over, or stop."
    else:
        raise RuntimeError("Couldn't find list to iterate through")

    session_attributes = set_session_attributes(curIndex, length, arr)
    return build_response(session_attributes, build_speechlet_response(
        card_title, speech_output, reprompt_text, should_end_session))


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
        missing_ingredients = checkPantry(requested_recipe, db)

        if missing_ingredients is None:
            speech_output = "Recipe not in Cookbook"
            reprompt_text = speech_output
        elif len(missing_ingredients) >= 1:
            speech_output = "You are missing some ingredients. "
            missing_ingredients_string = ""
            for x in missing_ingredients:
                speech_output += x + ", "
                missing_ingredients_string += x + ", "
            speech_output = speech_output[:-2]
            speech_output += "Would you like to set a reminder for these ingredients?"
            reprompt_text = "Would you like to set a reminder for these ingredients?"
            session_attributes = {"reminder": missing_ingredients_string}
        else:
            speech_output = "You have all the ingredients to make that recipe."
            reprompt_text = speech_output

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
    speech_output = "Welcome to Saucy bot. " \
                    "What can I do to help? "
    # If the user either does not reply to the welcome message or says something
    # that is not understood, they will be prompted again with this text.
    reprompt_text = "options include: add or remove ingredient, " \
                    "list recipes based on tag, " \
                    "and what can I make. An option to list all recipes you have the ingredients for"
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

"""
def create_favorite_color_attributes(favorite_color):
    return {"favoriteColor": favorite_color}


def set_color_in_session(intent, session):
     Sets the color in the session and prepares the speech to reply to the
    user.
    

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
"""


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
    if intent_name == "IWantToMakeIntent":
        return can_recipe_be_made(intent, session)
    elif intent_name == "FilterOnTagsIntent":
        return get_recipes_from_tag(intent, session)
    elif intent_name == "WhatCanIMake":
        return get_all_possible_recipes(intent, session)
    elif intent_name == "IngredientSearch":
        return do_i_have_ingredient(intent, session)
    elif intent_name == "RemoveIngredient":
        return out_of_ingredient(intent, session)
    elif intent_name == "AddIngredient":
        return picked_up_ingredient(intent, session)
    elif intent_name == "Reminder":
        pass
    elif intent_name == "SelectItemIntent":
        pass
    elif intent_name == "AMAZON.HelpIntent":
        pass
    elif intent_name == "AMAZON.NextIntent":
        return next_handler(intent, session)
    elif intent_name == "AMAZON.NoIntent":
        return no_handler(intent, session)
    elif intent_name == "AMAZON.PreviousIntent":
        return previous_handler(intent, session)
    elif intent_name == "AMAZON.RepeatIntent":
        pass
    elif intent_name == "AMAZON.StartOverIntent":
        return start_over_handler(intent, session)
    elif intent_name == "AMAZON.YesIntent":
        return yes_handler(intent, session)
    elif intent_name == "AMAZON.CancelIntent" or intent_name == "AMAZON.StopIntent":
        return handle_session_end_request()
    else:
        raise ValueError("Invalid intent")


def on_session_ended(session_ended_request, session, m_client):
    """ Called when the user ends the session.

    Is not called when the skill returns should_end_session=true
    """
    print("on_session_ended requestId=" + session_ended_request['requestId'] +
          ", sessionId=" + session['sessionId'])
    m_client.close()


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
    global mongo_client

    if event['session']['new']:
        mongo_client = pymongo.MongoClient(uri)

    if event['request']['type'] == "LaunchRequest":
        return on_launch(event['request'], event['session'])
    elif event['request']['type'] == "IntentRequest":
        return on_intent(event['request'], event['session'])
    elif event['request']['type'] == "SessionEndedRequest":
        return on_session_ended(event['request'], event['session'], mongo_client)


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
        return None
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
