#!/usr/bin/env python3
from typing import List, Tuple
from sys import argv, exit

import requests
from bs4 import BeautifulSoup as BS


def get_soup(url: str) -> BS:
    return BS(requests.get(url).text, features='html.parser')


def simply_scrape(simply_url: str) -> Tuple[List[str], List[str], List[str]]:
    # Get the URL HTML and construct a soup around it
    soup = get_soup(simply_url)
    # Get the needed sections of the HTML
    ingredients_section = soup.find_all(id='section--ingredients_1-0')[0]
    instructions_section = soup.find_all(id='section--instructions_1-0')[0]
    # Construct a soup around them
    ingredient_soup = BS(str(ingredients_section), features='html.parser')
    instruction_soup = BS(str(instructions_section), features='html.parser')
    # Get their text
    ingredients_list = ingredient_soup.find_all(text=True)
    instruction_list = instruction_soup.find_all(text=True)
    # Filter irrelevants
    ingredients_list = list(filter(lambda ing: ing not in ['\n', 'Ingredients'], ingredients_list))
    instruction_list = list(filter(lambda inst: inst not in ['\n', 'Instructions'], instruction_list))
    # Throw remaining text on the webpage to irrelevant list
    all_text = soup.find_all(text=True)
    irrelevant_list = [line for line in all_text if line not in instruction_list and line not in ingredients_list]
    # Return results
    return ingredients_list, instruction_list, irrelevant_list


def lemon_scrape(loveandlemons_url: str) -> Tuple[List[str], List[str], List[str]]:
    # Get the URL HTML and construct a soup around it
    soup = get_soup(loveandlemons_url)
    # Get the needed sectiyyons of the HTML
    try:
        ingredients_section = soup.find_all('div', {'class': 'wprm-recipe-ingredients-container'})[0]
        instructions_section = soup.find_all('div', {'class': 'wprm-recipe-instructions-container'})[0]
    except IndexError:
        print(loveandlemons_url)
        return [], [], []
    # Construct a soup around them
    ingredient_soup = BS(str(ingredients_section), features='html.parser')
    instruction_soup = BS(str(instructions_section), features='html.parser')
    # Get their text
    ingredients_list = ingredient_soup.find_all(text=True)
    instruction_list = instruction_soup.find_all(text=True)
    # Filter irrelevants
    ingredients_list = list(filter(lambda ing: ing not in [', ', ' ', ',', 'Ingredients'], ingredients_list))
    instruction_list = list(filter(lambda inst: inst not in [', ', ' ', ',', 'Instructions'], instruction_list))
    # Throw remaining text on the webpage to irrelevant list
    all_text = soup.find_all(text=True)
    irrelevant_list = [line for line in all_text if line not in instruction_list and line not in ingredients_list]
    # Return results
    return ingredients_list, instruction_list, irrelevant_list


def allrecipe_scrape(allrecipes_url: str) -> Tuple[List[str], List[str], List[str]]:
    # Get the URL HTML and construct a soup around it
    soup = get_soup(allrecipes_url)
    # Get the needed sectiyyons of the HTML
    ingredients_section = soup.find_all('ul', {'class': 'ingredients-section'})[0]
    instructions_section = soup.find_all('ul', {'class': 'instructions-section'})[0]
    # Construct a soup around them
    ingredient_soup = BS(str(ingredients_section), features='html.parser')
    instruction_soup = BS(str(instructions_section), features='html.parser')
    # Get their text
    ingredients_list = ingredient_soup.find_all(text=True)
    instruction_list = instruction_soup.find_all(text=True)
    # Filter irrelevants
    ingredients_list = list(filter(lambda ing: ing not in ['\n', ' ', '\t', ' ,', 'Ingredients'], ingredients_list))
    instruction_list = list(filter(lambda inst: inst not in ['\n', ' ', '\t', ' ,', 'Instructions'], instruction_list))
    # Throw remaining text on the webpage to irrelevant list
    all_text = soup.find_all(text=True)
    irrelevant_list = [line for line in all_text if line not in instruction_list and line not in ingredients_list]
    irrelevant_list = list(filter(lambda inst: inst not in ['\n', ' ', 'Instructions'], irrelevant_list))
    # Return results
    return ingredients_list, instruction_list, irrelevant_list


def get_scraper(site_name: str) -> callable:
    if site_name == 'simply':
        return simply_scrape
    elif site_name == 'lemon':
        return lemon_scrape
    elif site_name == 'allrecipe':
        return allrecipe_scrape
    else:
        print("Unrecognized site: " + site_name)
        return None


def save(site: str, urls: List[str]):
    scraper = get_scraper(site)

    if scraper is None:
        return
    for url in urls:
        ingredients, instructions, irrelevants = scraper(url)
        with open('ingredients.txt', 'a') as ingredients_file:
            for line in ingredients:
                ingredients_file.write(line)
        with open('instructions.txt', 'a') as instructions_file:
            for line in instructions:
                instructions_file.write(line)
        with open('neither.txt', 'a') as neither_file:
            for line in irrelevants:
                neither_file.write(line)


if __name__ == '__main__':
    # site = argv[1]
    # urls = argv[2:]
    # save(site, urls)

    SIMPLY_RECIPES = ["https://www.simplyrecipes.com/philly-cheesesteak-recipe-5188498". "https://www.simplyrecipes.com/kentucky-hot-brown-5180178". "https://www.simplyrecipes.com/shakshuka-with-feta-olives-and-peppers-5114919". "https://www.simplyrecipes.com/recipes/steak_salad". "https://www.simplyrecipes.com/tex-mex-chopped-chicken-salad-with-cilantro-lime-dressing-5179994". "https://www.simplyrecipes.com/recipes/classic_rack_of_lamb/". "https://www.simplyrecipes.com/spicy-tofu-stir-fry-recipe-5115374". "https://www.simplyrecipes.com/easy-homemade-grenadine-recipe-5180859". "https://www.simplyrecipes.com/recipes/bread_and_butter_pickles/". "https://www.simplyrecipes.com/nashville-hot-chicken-recipe-5191597". "https://www.simplyrecipes.com/nashville-hot-chicken-recipe-5191597". "https://www.simplyrecipes.com/garden-walk-cocktail-recipe-5180844". "https://www.simplyrecipes.com/frozen-margarita-5192682". "https://www.simplyrecipes.com/pisco-sour-recipe-5192022". "https://www.simplyrecipes.com/recipes/angel_food_cake/". "https://www.simplyrecipes.com/recipes/how_to_make_the_best_detox_smoothie/". "https://www.simplyrecipes.com/recipes/creamy_polenta_with_white_beans_and_roasted_broccoli/". "https://www.simplyrecipes.com/recipes/chicken_and_dumplings/". "https://www.simplyrecipes.com/recipes/pot_roast/". "https://www.simplyrecipes.com/recipes/glazed_oxtails/"]
    LEMON_RECIPES = ['https://www.allrecipes.com/recipe/15985/grandmas-corn-pudding/','https://www.allrecipes.com/recipe/9316/grandmas-five-cup-salad/','https://www.allrecipes.com/recipe/247225/tomato-avocado-sandwich/','https://www.allrecipes.com/recipe/147360/fried-green-tomato-sandwich/','https://www.allrecipes.com/recipe/19163/luscious-slush-punch/','https://www.allrecipes.com/recipe/223400/old-school-mac-n-cheese/',,'https://www.allrecipes.com/recipe/238840/quick-crispy-parmesan-chicken-breasts/','https://www.allrecipes.com/recipe/239930/taco-meat/','https://www.allrecipes.com/recipe/276647/instant-pot-chicken-and-dumplings/','https://www.allrecipes.com/recipe/174517/angel-hair-pasta-with-lemon-and-chicken/','https://www.allrecipes.com/recipe/174525/shrimp-with-garlic-cream-sauce-over-linguine/','https://www.allrecipes.com/recipe/284442/broken-lasagna-pasta/','https://www.loveandlemons.com/black-beans-recipe/','https://www.loveandlemons.com/veggie-noodles/','https://www.loveandlemons.com/grilled-corn-on-the-cob/','https://www.loveandlemons.com/guacamole-recipe/','https://www.loveandlemons.com/polenta-recipe/','https://www.loveandlemons.com/grilled-vegetables/','https://www.loveandlemons.com/corn-salsa/','https://www.loveandlemons.com/homemade-salsa-recipe/']
    ALLRECIPE_RECIPES = ['']

    save('simply', SIMPLY_RECIPES)
