from typing import List, Tuple, Dict

# Prior, Download dataset json from https://eightportions.com/datasets/Recipes/ to dataset.json

JSON_PATH = 'datafiles/dataset.json'
DATA_SIZE = 60_000


def get_raw_json() -> str:
    with open(JSON_PATH) as datafile:
        return datafile.read()


def get_json_dict() -> Dict[str, List[str]]:
    with open('datafiles/dataset.json', 'r') as datafile:
        return eval(datafile.read().replace('null', 'None'))

def get_manual_data() -> Tuple[List[str], List[str]]:
    instructions = []
    ingredients = []
    with open('datafiles/instructions.txt', 'r') as datafile:
        instructions += datafile.readlines()
    with open('datafiles/ingredients.txt', 'r') as datafile:
        ingredients += datafile.readlines()
    return instructions, ingredients


def get_data_lists() -> Tuple[List[str], List[str]]:
    instructions = set()
    ingredients = set()
    irrelevants = set()

    with open('datafiles/instructions.txt', 'r') as datafile:
        instructions = set(datafile.readlines())
    with open('datafiles/ingredients.txt', 'r') as datafile:
        ingredients = set(datafile.readlines())

    recipes = get_json_dict()
    i = 0
    while len(instructions) < DATA_SIZE or len(ingredients) < DATA_SIZE:
        item = recipes[i]
        if item:  # JSON contains a few empty recipes for some reason. this check the item is not empty.
            if len(instructions) < DATA_SIZE:
                instructions = instructions.union(item['directions'])
            if len(ingredients) < DATA_SIZE:
                ingredients = ingredients.union(item['ingredients'])
        i += 1

    return list(instructions)[:DATA_SIZE], list(ingredients)[:DATA_SIZE]


def save_to_tsv(instructions, ingredients):
    dataset = []

    # Ignore tabs and newlines to not interrupt the tsv format (the tokenizer does not care about them anyway)
    clean = lambda lst: [str(item).replace('\t', ' ').replace('\n', ' ') for item in lst]
    ingredients = clean(ingredients)
    instructions = clean(instructions)

    for i in range(DATA_SIZE):
        dataset.append([ingredients[i], '1,0'])
        dataset.append([instructions[i], '0,1'])

    with open('datafiles/dataset.tsv', 'w+') as f:
        for i, item in enumerate(dataset, 1):
            f.write(f"{item[0]}\t{item[1]}\n")
            print(f'{i}/{len(dataset)}')


if __name__ == '__main__':
    save_to_tsv(*get_data_lists())
