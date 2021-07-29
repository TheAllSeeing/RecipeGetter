import requests
import classifier
import nlp_utils as utils
import trashbot
from bs4 import BeautifulSoup as BS
from typing import List
from nlp_utils import clean_paragraphs

CONFIDENCE_THRESHOLD_TRASH = 0.8
CONFIDENCE_THRESHOLD_INGREDIENT = 0.9
CONFIDENCE_THRESHOLD_INSTRUCTION = 0.68


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
    soup = BS(html_page, features='html.parser')
    # Irrelevant elements
    blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style']
    base_text = soup.find('main').find_all(text=True)
    if not base_text:
        base_text = soup.find_all(text=True)
    filtered_lines = [str(line) for line in base_text if line.parent.name not in blacklist]
    trimmed = [p for p in filtered_lines if
               p not in ['\n', ' ', '']]  # Trim empty space when there were multiple newlines in a row.
    return trimmed


def classify(paragraphs: List[str]) -> List[int]:
    """
    :param paragraphs: a paragraph from a recipe page
    :return: integer classification of the paragraph as ingredient (0), instruction (1) or neither (2)
    """
    classifications = classifier.predict(paragraphs)
    trash_guesses = trashbot.predict(paragraphs)

    results = []

    for classification, trash_guess, paragraph in zip(classifications, trash_guesses, paragraphs):

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
    instructions = ''

    classifications = classify(inputs)
    for paragraph_type, paragraph in zip(classifications, inputs):
        # get paragraph type - 1 if it's an ingredient, 0 if it's an instruction and -1 if it is neither

        # Add to appropriate variable or ignore if irrelevant
        if paragraph_type == -1:
            continue
        elif paragraph_type == 1:
            instructions += '\n' + paragraph
        elif paragraph_type == 0:
            ingredients.append(paragraph)

    # Compose JSON
    json = '{\n'  # Opening brace
    json += "\n\tingredients: ["  # ingredients member, one indentation level
    json += ',\n\t\t'.join(ingredients)  # Ingredient list in the ingredients member, two indentations member
    json += '\n\t]'  # Close off ingredients list (one indentation level)
    json += '\n\n\tinstructions: "'  # Declare instructions member, two indentation levels
    # Add instructions. Sadly no way to properly line-wrap and indent this properly, but a parser would not care.
    json += instructions
    json += '"'  # Close instructions quotation
    json += '\n}'  # Closing brace
    return json


if __name__ == '__main__':
    print(get_recipe_json('https://www.loveandlemons.com/homemade-pasta-recipe/'))
