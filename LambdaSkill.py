# --------------- Functions that control the skill's behavior ------------------

def can_recipe_be_made(intent, session):
    """ Checks if the recipe is in the Cookbook
        Checks if the Pantry contains all necessary ingredients
    """

    card_title = intent['name']
    session_attributes = {}
    should_end_session = False

    if 'Recipe' in intent['slots']:
        requested_recipe = intent['slots']['Recipe']['value']
        
        """
        #check mongodb for recipe
        MongoClientURI mongoClientURI = new MongoClientURI(mongoURl);
        MongoClient mongoClient = new MongoClient(mongoClientURI);
        MongoDatabase db = mongoClient.getDatabase(mongoDB);
        """
        missing_flag = False
        missing_ingredients = []
        recipe_ingredients = ['spaghetti','meatballs']
        pantry_ingredients = ['spaghetti','red sauce','meatballs','basil']
        
        for x in recipe_ingredients:
            if x not in pantry_ingredients:
                missing_flag = True
                missing_ingredients.append(x)
                
        if missing_flag:
            speech_output = "You are missing some ingredients. "
            for x in missing_ingredients:
                speech_output += x + ", "
            speech_output = speech_output[:-2] #cut trailing comma        
            reprompt_text = speech_output

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
