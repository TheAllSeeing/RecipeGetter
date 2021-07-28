from typing import List, Tuple, Dict

# Prior, Download dataset json from https://eightportions.com/datasets/Recipes/ to dataset.json

JSON_PATH = 'dataset.json'
DATA_SIZE = 60_000


def get_raw_json() -> str:
    with open(JSON_PATH) as datafile:
        return datafile.read()


def get_json_dict() -> Dict[str, List[str]]:
    with open('dataset.json', 'r') as datafile:
        return eval(datafile.read().replace('null', 'None'))

def get_manual_data() -> Tuple[List[str], List[str], List[str]]:
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
    instructions = set()
    ingredients = set()
    irrelevants = set()

    with open('instructions.txt', 'r') as datafile:
        instructions = set(datafile.readlines())
    with open('ingredients.txt', 'r') as datafile:
        ingredients = set(datafile.readlines())
    with open('neither.txt', 'r') as datafile:
        irrelevants = datafile.readlines()

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

    return list(instructions)[:DATA_SIZE], list(ingredients)[:DATA_SIZE], list(irrelevants)[:DATA_SIZE]


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
        # dataset.append([irrelevants[i], '0,0,1'])

    with open('dataset.tsv', 'w+') as f:
        for item in dataset:
            f.write(f"{item[0]}\t{item[1]}\n")


if __name__ == '__main__':
    save_to_tsv(*get_data_lists())
