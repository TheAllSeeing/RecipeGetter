from tensorflow import keras
import requests
from bs4 import BeautifulSoup as BS
from model import predict, train_model


def get_html(url: str) -> str:
    """
    get_html(url: str) -> str

    Takes a webpage url and returns its contents as a string
    """
    # Probably via an extra package, e.g requests
    return requests.get(url).text


def get_paragraphs(html_page: str) -> str:
    """
    get_paragraphs(html_page: str) -> str:

    Takes an HTML string and extracts from it a list of the text paragraphs it contains.
    """
    soup = BS(html_page)
    # Irrelevant elements
    blacklist = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style']
    base_text = soup.find_all(text=True)
    filtered_lines = [str(line) for line in base_text if line.parent.name not in blacklist]
    paragraphs = ''.join(filtered_lines).split('\n')
    trimmed = [p for p in paragraphs if p != '']  # Trim empty space when there were multiple newlines in a row.
    return trimmed


def classify(paragraph: str) -> int:
    """
    Classify a paragraph as instructions (1), ingredients (0) or neither (-1)
    """
    paragraph_class = predict(paragraph, load=False)

    if paragraph_class > 0.85:
        return 1
    if paragraph_class < 0.15:
        return 0
    return -1


def get_recipe_json(url: str) -> str:
    """
    get_recipe_json(url: str) -> str

    Takes the url to a recipe webpage and extracts a matching json of ingredients list and instructions string.

    An example webpage can be found at https://www.loveandlemons.com/homemade-pasta-recipe/
    An example output may look like so:
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
    # Extract the relevant paragraphs from the webpage
    inputs = get_paragraphs(get_html(url))

    # Iterate over the paragraphs and keep them in appropriate variables
    ingredients = []
    instructions = ''

    for paragraph in inputs:
        # get paragraph type - 1 if it's an ingredient, 0 if it's an instruction and -1 if it is neither
        paragraph_type = classify(paragraph)

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
    json += '\n\n\tinstructions: "'  # Declare instrcutions member, two indentation levels
    json += instructions  # Add instructions. Sadly noi way to properly line-wrap and indent this properly, but a compiler would deal
    json += '"'  # Close instructions quotation
    json += '\n}'  # Closing brace
    return json


if __name__ == '__main__':
    print(get_recipe_json('https://www.loveandlemons.com/homemade-pasta-recipe/'))
