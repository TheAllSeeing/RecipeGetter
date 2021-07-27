import requests
from bs4 import BeautifulSoup as BS
from typing import List

from model import load_model, preprocess_data

CONFIDENCE_THRESHOLD = 0.97
"""Minimum model confidence in classification required for a paragraph to go into the threshold. 

    It is assumed the model will be at least a little insecure about irrelevant texts (e.g 'Contact Us')
"""

MODEL = load_model()


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
    :return: integer classification of the paragraph as instruction (1), ingredient (0) or neither (-1)
    """
    predictions = MODEL.predict(preprocess_data(paragraphs))

    def prediction_to_code(prediction):
        if prediction[0] > CONFIDENCE_THRESHOLD:
            return 0
        if prediction[1] > CONFIDENCE_THRESHOLD:
            return 1
        return -1

    return [prediction_to_code(prediction) for prediction in predictions]


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
