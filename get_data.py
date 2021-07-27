import json
import numpy as np

# Prior, Download dataset json from https://eightportions.com/datasets/Recipes/ to dataset.json

JSON_PATH = 'dataset.json'
DATA_SIZE = 40_000


def get_raw_json():
    with open(JSON_PATH) as datafile:
        return datafile.read()


def get_json_dict():
    return json.loads(get_raw_json())


def get_data_lists():
    instructions = []
    ingredients = []
    neither = []
    with open('instructions.txt', 'r') as datafile:
        instructions += datafile.readlines()
    with open('ingredients.txt', 'r') as datafile:
        ingredients += datafile.readlines()
    with open('neither.txt', 'r') as datafile:
        neither += datafile.readlines()
    return instructions, ingredients, neither


def get_data_lists() -> Tuple[List[str], List[str], List[str]]:
    instructions = []
    ingredients = []
    irrelevants = []

    with open('instructions.txt', 'r') as datafile:
        instructions += datafile.readlines()
    with open('ingredients.txt', 'r') as datafile:
        ingredients += datafile.readlines()
    with open('neither.txt', 'r') as datafile:
        irrelevants += datafile.readlines()

    recipes = get_json_dict()
    for item in recipes:
        if item:  # JSON contains a few empty recipes for some reason. this check the item is not empty.
            instructions += item['directions']
            ingredients += item['ingredients']

    return list(set(instructions))[:DATA_SIZE], list(set(ingredients))[:DATA_SIZE], irrelevants


def save_to_tsv(instructions, ingredients, irrelevants):
    dataset = []

    # Ignore tabs and newlines to not interrupt the tsv format (the tokenizer does not care about them anyway)
    clean = lambda lst: [str(item).replace('\t', ' ').replace('\n', ' ') for item in lst]
    ingredients = clean(ingredients)
    instructions = clean(instructions)
    irrelevants = clean(irrelevants)

    for i in range(DATA_SIZE):
        dataset.append([ingredients[i], '1,0,0'])
        dataset.append([instructions[i], '0,1,0'])

    for item in irrelevants[:20_000]:
        dataset.insert(0, [item, '0,0,1'])
    for item in irrelevants[20_000:]:
        dataset.append([item, '0,0,1'])

    with open('dataset.tsv', 'w+') as f:
        for item in dataset.keys():
            f.write(f"{item}\t{dataset[item]}\n")


if __name__ == '__main__':
    save_to_tsv(*get_data_lists())
