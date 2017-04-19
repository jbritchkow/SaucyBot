import pymongo
import json

###################################
## Saucybot Alexa Skill Group
## CS495-Capstone Computing 
## Jason Britchkow Cody Connell 
## Connor Mason    Margaret Tiedt 
###################################

uri = 'mongodb://cwmason:Capstone2017@ec2-34-201-51-167.compute-1.amazonaws.com'

def lambda_handler(event, context):
    client = pymongo.MongoClient(uri)
    db1 = client['saucybot']
    #for d in db1.pantry.find():
    #    print (d)
    #isThere = ingredientSearch('milk', db1)
    #print 'Ingredient there: ',isThere
    #rec = recipeSearch('ghnocchi', db1)
    #print 'Recipe there: ', rec
    #ingredients = recipeIngredients('chicken noodle soup', db1)
    #for x in ingredients:
    #    print (x)
    #addIngredient('noodles', db1)
    #removeIngredient('alexa sauce', db1)
    #checkPantry('chocolate cake', db1)
    #possible = []
    possible = searchCookbookAll(db1)
    #if possible is None:
    #    return 'Failed'
    #possible = searchCookbookOn(['italian', 'cheesy'], db1)
    for x in possible:
        print (x)
    c.close()
    return 'All done!'
    #raise Exception('Something went wrong')

def addIngredient(ing, db):
    return db.pantry.insert({'ingredient': ing})
    
def removeIngredient(ing, db):
    return db.pantry.remove({'ingredient': ing})

def ingredientSearch(ingredient, db):
    return bool(db.pantry.find_one({'ingredient': ingredient}))  
    
def recipeSearch(recipe, db):
    return bool(db.cookbook.find_one({'name': recipe}))
    
def recipeIngredients(recipe, db):
    #Returns None if recipe not in cookbook, list of its ingredients if it is
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
    #For the 'what can I make' scenario. Looks at all available ingredients
    #and either returns list of recipes to make or None
    recipes = []
    try:
        recs = db.cookbook.find({})
        for item in recs:
            if len(checkPantry(item['name'], db)) == 0:
                recipes.append(item['name'])
    except:
        print 'Something wrong in try/except #1'
        return None
    return recipes
