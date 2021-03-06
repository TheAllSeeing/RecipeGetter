import requests
import classifier
from bs4 import BeautifulSoup
from typing import List
from utils import clean_paragraphs

CONFIDENCE_THRESHOLD_INGREDIENT = 0.9
"""Minimum model confidence in ingredient classification to go into JSON"""
CONFIDENCE_THRESHOLD_INSTRUCTION = 0.68
"""Minimum model confidence in instruction classification to go into JSON"""


def get_html(url: str) -> str:
    """
    get_html(url: str) -> str

    :param url: any valid URL
    :return: the HTML contents of the corresponding webpage, as a string
    """
    # Probably via an extra package, e.g requests
    return requests.get(url).text


def get_paragraphs(html_page: str) -> List[str]:
    """
    get_paragraphs(html_page: str) -> str

    Strips an HTML webpage of scripts, style amd metadata and returns a list of the  text paragraphs that remain

    :param html_page: a string containing a web page's HTML code
    :return: A list of the textual paragraphs in the page's main body
    """
    soup = BeautifulSoup(html_page, features='html.parser')
    # Irrelevant elements
    main_soup = soup.find('main')
    if main_soup:  # If main tag exists
        soup = main_soup
    for span in soup.find_all('span'):
        span.replace_with_children()
    return clean_paragraphs(soup.find_all(text=True))


def classify(paragraphs: List[str]) -> List[int]:
    """
    :param paragraphs: a paragraph from a recipe page
    :return: integer classification of the paragraph as ingredient (0), instruction (1) or neither (2)
    """
    classifications = classifier.predict(paragraphs)

    results = []

    for classification, paragraph in zip(classifications, paragraphs):

        # Common Phrases
        if paragraph.startswith('Step ') and len(paragraph) == 6:
            results.append(1)
        elif paragraph.startswith('(function() {'):
            results.append(2)
        # Model Classifications
        elif classification[1] > CONFIDENCE_THRESHOLD_INSTRUCTION:
            results.append(1)
        elif classification[0] > CONFIDENCE_THRESHOLD_INGREDIENT:
            results.append(0)
        # Default Class
        else:
            results.append(2)

    return results


def get_recipe_json(url: str) -> str:
    """
    get_recipe_json(url: str) -> str


    Takes the url to a recipe webpage and extracts a matching json of ingredients list and instructions string.

    An example webpage can be found at https://www.loveandlemons.com/homemade-pasta-recipe/
    An example output may look like so (this one is for a cheese toast):
    {
        ingredients: [
            2 slices of bread

            1 box of butter

            1 slice of yellow cheese
        ]

        instructions: "Spread some butter over one slice of bread.
            Put the slice of cheese over the butter
            Close the sandwich with the second slice
            Put the sandwich in the toaster and wait 3 minutes
    }

    :param url: the url where the recipe is located
    :return: a JSON string containing the recipe's ingredient list and instructions
    """
    # Extract the relevant paragraphs from the webpage.
    # Catch ConnectionError (no internet) if it rises and if so give an appropriate message and exit
    try:
        inputs = get_paragraphs(get_html(url))
    except requests.exceptions.ConnectionError:
        print("Could not retrieve the web page. Please make sure you are connected to the Internet.")
        return ''

    # Iterate over the paragraphs and keep them in appropriate variables
    ingredients = []
    instructions = []

    classifications = classify(inputs)
    for paragraph_type, paragraph in zip(classifications, inputs):
        # get paragraph type - 1 if it's an ingredient, 0 if it's an instruction and -1 if it is neither

        # Add to appropriate variable or ignore if irrelevant
        if paragraph_type == 2:
            continue
        elif paragraph_type == 1:
            instructions.append(paragraph)
        elif paragraph_type == 0:
            ingredients.append(paragraph)

    # Compose JSON
    json = '{\n'  # Opening brace
    json += "\n\tingredients: [\n\t\t"  # ingredients member, one indentation level
    json += ',\n\t\t'.join(ingredients)  # Ingredient list in the ingredients member, two indentations member
    json += '\n\t]'  # Close off ingredients list (one indentation level)
    json += '\n\n\tinstructions: "'  # Declare instructions member, two indentation levels
    json += '\n\n\t\t'.join(instructions)
    json += '"'  # Close instructions quotation
    json += '\n}'  # Closing brace
    return json


if __name__ == '__main__':
    TEST_URL = 'https://www.allrecipes.com/recipe/204952/san-diego-grilled-chicken/'
    print(get_recipe_json('https://www.seriouseats.com/fresh-egg-pasta'))
    get_paragraphs(get_html('https://www.bettycrocker.com/recipes/lemon-lime-checkerboard-cake/9ba32e15-746f-485d-a41a-3a66d3c8557b'))