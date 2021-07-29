#!/usr/bin/env python3
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup as BS, element
from nlp_utils import DATAFILES, clean_paragraphs

URL_FILES = ['scrapeurls/' + filename for filename in ['simply.txt', 'allrecipes.txt', 'lemon.txt', 'network.txt']]

def get_soup(url: str) -> BS:
    return BS(requests.get(url).text, features='html.parser')


def simply_scrape(simply_url: str) -> Tuple[List[str], List[str], List[str]]:
    # Get the URL HTML and construct a soup around it
    soup = get_soup(simply_url)

    [s.extract() for s in soup.find_all('figcaption')]
    [s.extract() for s in soup.find_all(attrs={'class': 'feedback-block'})]
    [s.extract() for s in soup.find_all(attrs={'class': 'nutrition-info'})]
    # Get the needed sections of the HTML
    ingredients_section = soup.find(id='section--ingredients_1-0')
    instructions_section = soup.find(id='mntl-sc-block_3-0')

    # If the page didn't fit the template and bs4 could not locate such sections, exit and return empty lists.
    if not ingredients_section or not instructions_section:
        print(simply_url)
        return [], [], []

    # Get their text
    ingredients_list = ingredients_section.find_all(text=True)
    instruction_list = instructions_section.find_all(text=True)
    # Filter irrelevants
    ingredients_list = clean_paragraphs(ingredients_list)
    instruction_list = clean_paragraphs(instruction_list)
    # Throw remaining text on the webpage to irrelevant list
    all_text = get_soup(simply_url).find_all(text=True)
    irrelevant_list = [line for line in all_text if line not in instruction_list and line not in ingredients_list]
    irrelevant_list = clean_paragraphs(irrelevant_list)
    # Return results
    return ingredients_list, instruction_list, irrelevant_list


def lemon_scrape(loveandlemons_url: str) -> Tuple[List[str], List[str], List[str]]:
    # Get the URL HTML and construct a soup around it
    soup = get_soup(loveandlemons_url)
    # Get the needed sectiyyons of the HTML
    ingredients_section = soup.find('div', {'class': 'wprm-recipe-ingredients-container'})
    instructions_section = soup.find('div', {'class': 'wprm-recipe-instructions-container'})

    # If the page didn't fit the template and bs4 could not locate such sections, exit and return empty lists.
    if not ingredients_section or not instructions_section:
        print(loveandlemons_url)
        return [], [], []

    # Get their text
    ingredients_list = ingredients_section.find_all(text=True)
    instruction_list = instructions_section.find_all(text=True)
    # Filter irrelevants
    ingredients_list = clean_paragraphs(ingredients_list)
    instruction_list = clean_paragraphs(instruction_list)
    # Throw remaining text on the webpage to irrelevant list
    all_text = soup.find_all(text=True)
    irrelevant_list = [line for line in all_text if line not in instruction_list and line not in ingredients_list]
    irrelevant_list = clean_paragraphs(irrelevant_list)
    # Return results
    return ingredients_list, instruction_list, irrelevant_list


def allrecipe_scrape(allrecipes_url: str) -> Tuple[List[str], List[str], List[str]]:

    # Get the URL HTML and construct a soup around it
    soup = get_soup(allrecipes_url)
    # Get the needed sectiyyons of the HTML
    ingredients_section = soup.find('ul', {'class': 'ingredients-section'})
    instructions_section = soup.find('ul', {'class': 'instructions-section'})

    # If the page didn't fit the template and bs4 could not locate such sections, exit and return empty lists.
    if not ingredients_section or not instructions_section:
        print(allrecipes_url)
        return [], [], []

    # Get their text
    ingredients_list = ingredients_section.find_all(text=True)
    instruction_list = instructions_section.find_all(text=True)
    # Filter irrelevants
    ingredients_list = clean_paragraphs(ingredients_list)
    instruction_list = clean_paragraphs(instruction_list)
    # Throw remaining text on the webpage to irrelevant list
    all_text = soup.find_all(text=True)
    irrelevant_list = [line for line in all_text if line not in instruction_list and line not in ingredients_list]
    irrelevant_list = clean_paragraphs(irrelevant_list)
    # Return results
    return ingredients_list, instruction_list, irrelevant_list

def network_scrape(foodnetwork_url: str) -> Tuple[List[str], List[str], List[str]]:
    soup = get_soup(foodnetwork_url)
    ingredients_section = soup.find('div', {'class': 'o-Ingredients__m-Body'})
    instructions_section = soup.find('div', {'class': 'o-Method__m-Body'})

    # If the page didn't fit the template and bs4 could not locate such sections, exit and return empty lists.
    if not ingredients_section or not instructions_section:
        print(foodnetwork_url)
        return [], [], []

    # Get their text
    ingredients_list = ingredients_section.find_all(text=True)
    instruction_list = instructions_section.find_all(text=True)
    # Filter irrelevants
    ingredients_list = clean_paragraphs(ingredients_list)
    instruction_list = clean_paragraphs(instruction_list)
    # Throw remaining text on the webpage to irrelevant list
    all_text = soup.find_all(text=True)
    irrelevant_list = [line for line in all_text if line not in instruction_list and line not in ingredients_list]
    irrelevant_list = clean_paragraphs(irrelevant_list)
    # Return results
    return ingredients_list, instruction_list, irrelevant_list


def get_scraper(site_name: str) -> callable:
    if site_name == 'simply':
        return simply_scrape
    elif site_name == 'lemon':
        return lemon_scrape
    elif site_name == 'allrecipes':
        return allrecipe_scrape
    elif site_name == 'network':
        return network_scrape
    else:
        print("Unrecognized site: " + site_name)
        return None


def save(site: str, urls: List[str]):
    scraper = get_scraper(site)
    if scraper is None:
        return
    for i, url in enumerate(urls, 1):
        print('\r' + str(i) + '/' + str(len(urls)))
        # Iterates over [ingredients, instructions, neither]
        for lst, filename in zip(scraper(url), DATAFILES):
            with open(filename, 'a') as datafile:
                for line in lst:
                    datafile.write(line + '\n')


def reset():
    for filename in DATAFILES:
        open(filename, 'w+').close()

    for filename in URL_FILES:
        with open(filename) as urlfile:
            site = urlfile.name.split('/')[-1][:-4]
            save(site, clean_paragraphs(urlfile.readlines()))


if __name__ == '__main__':
    # site = argv[1]
    # urls = argv[2:]
    # save(site, urls)
    # save('simply', SIMPLY_RECIPES)
    # save('allrecipe', ALLRECIPE_RECIPES)
    # save('lemon', LEMON_RECIPES)
    #
    reset()
