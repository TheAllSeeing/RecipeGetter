import json
import numpy as np

# Prior, Download dataset json from https://eightportions.com/datasets/Recipes/ to dataset.json

JSON_PATH = 'dataset.json'
DATA_SIZE = 55_000


def get_raw_json():
    with open(JSON_PATH) as datafile:
        return datafile.read()


def get_json_dict():
    return json.loads(get_raw_json())


def get_data_lists():
    recipes = get_json_dict()
    instructions = []
    ingredients = []
    for item in recipes:
        if item:  # JSON contains a few empty recipes for some reason. this check the item is not empty.
            instructions += item['directions']
            ingredients += item['ingredients']
    # Total size of instructions is 69458
    # Total size of ingredients is 199030
    # I don't really want to try and deal with imbalanced classes in training, so I'll trim them to 67000
    # I could have really done it while getting them from the recipe dictionaries, but in this case it was pretty
    # negligible in time

    return list(set(instructions))[:DATA_SIZE], list(set(ingredients))[:DATA_SIZE]


def save_to_tsv(instructions, ingredients):
    instructions, ingredients = get_data_lists()
    dataset = {}
    for i in range(DATA_SIZE):
        # Ignore tabs and newlines to not interrupt the tsv format (the tokenizer does not care about them anyway)
        dataset[ingredients[i].replace('\t', ' ').replace('\n', '')] = 0
        dataset[instructions[i].replace('\t', ' ').replace('\n', '')] = 1
    with open('dataset.tsv', 'w+') as f:
        for item in dataset.keys():
            f.write(f"{item}\t{dataset[item]}\n")


if __name__ == '__main__':
    save_to_tsv(*get_data_lists())
