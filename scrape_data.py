"""
This script allowes easy retrieval of data for training and testing from recipe sites. Currently
https://www.allrecipes.com/, https://www.simplyrecipes.com/, https://www.loveandlemons.com/ and https://www.foodnetwork.com/
are supported.

The script's save(str) function receives a valid url and a site name ("allrecipe", "simply", "lemon", "network"), and
writes ingredient, instruction and irrelevant data to datafiles/ingredients.txt, datafiles/instructions.txt and
datafiles/neither.txt, respectively.

This is done via scraping functions that process thw website HTML code using knowledge gained from prior inspection of
the website pages. This will not work for all pages, specifically not for old pages that use a different template,
but is generally reliable. URLs for pages that the function can't scraped will be printed during save() run.

To re-generate the data files generated by this script, one can run the reset() functions
URLs for valid sites can be added to a corresponding file in the scrapeurls directory, and they will be considered
when running reset().
"""
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup, element
from utils import DATAFILES, clean_paragraphs

URL_FILES = ['scrapeurls/' + filename for filename in ['simply.txt', 'allrecipes.txt', 'lemon.txt', 'network.txt']]
"""The files where the list of URLs I got my data from are found, in case of rescraping."""

def get_soup(url: str) -> BeautifulSoup:
    """
    gets a bs4 BeautifulSop object from a given url
    :param url: the url of the webpage to generate a soup from
    :return: the BeautifulSoup corrresponding to the webpage
    """
    return BeautifulSoup(requests.get(url).text, features='html.parser')


def simply_scrape(simply_url: str) -> Tuple[List[str], List[str], List[str]]:
    """
    Scrapes model data from a https://www.simplyrecipes.com/ recipe,
    :param simply_url: a www.simplyrecipes.com recipe url
    :return: An `(ingridient, instruction, irrelevant)` tuple from the data found on the page.
    """
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
    """
    Scrapes model data from a https://www.loveandlemons.com/ recipe,
    :param loveandlemons_url: a www.loveandlemons.com recipe url
    :return: An `(ingridient, instruction, irrelevant)` tuple from the data found on the page.
    """
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
    """
    Scrapes model data from a https://www.allrecipes.com/ recipe,
    :param allrecipes_url: a www.allrecipes.com recipe url
    :return: An `(ingridient, instruction, irrelevant)` tuple from the data found on the page.
    """
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
    """
    Scrapes model data from a https://www.foodnetwork.com/ recipe,
    :param foodnetwork_url: a www.foodnetwork.com recipe url
    :return: An `(ingridient, instruction, irrelevant)` tuple from the data found on the page.
    """
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
    """
    Get a scraper function by site name
    :param site_name: name of the site to scrape. Either "simply", "lemon", "allrecipes" or "network"
    :return: a function that can take a page from a corresponding site and return the ingridients, instructions,
    and irrelevant data found in its contents.
    """
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
    """
    Writes ingridient, instruciton and irrelevant data from recipe webpages to datafiles/ingridients.txt, datafiles/instrucitons.txt and
    datafiles/neither.txt, respectively.
    Prints progress through the urls (e.g 7/85 when saving data from the 7th url out of 85).
    :param site: the sote the recipe webpage is on. Either "simply", "lemon", "allrecipes" or "network",
    :param urls: a list of urls from the site to save the contents of.
    """
    scraper = get_scraper(site)
    if scraper is None:
        return
    # For each URL:
    for i, url in enumerate(urls, 1):
        # Print progress
        print('\r' + str(i) + '/' + str(len(urls)))
        # Iterates over [ingredients, instructions, neither], and appends each file the
        for lst, filename in zip(scraper(url), DATAFILES):
            with open(filename, 'a') as datafile:
                for line in lst:
                    datafile.write(line + '\n')

def reset():
    """
    Re-generates data files written by save(), by urls found in the scrapeurl directory (under simply.txt,
    allrecipes.txt, lemon.txt and network.txt). URLs can be added manually so this function will use them as well.
    """
    # Clears all data files.
    for filename in DATAFILES:
        open(filename, 'w+').close()

    # Runs save on the list of URLs in each site.
    for filename in URL_FILES:
        with open(filename) as urlfile:
            site = urlfile.name.split('/')[-1][:-4]
            save(site, clean_paragraphs(urlfile.readlines()))

if __name__ == '__main__':
    reset()