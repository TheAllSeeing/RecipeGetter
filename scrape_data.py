#!/usr/bin/env python3
from typing import List, Tuple
import requests
from bs4 import BeautifulSoup as BS, element


def blacklist_filter(line: element.Tag) -> bool:
    """
    A predicate used to filter out irrelevant lines often found in ingredient and instructions
    sections. This will include titles, blank lines and spaces, and all assoetments of HTML/CSS/JS code.

    :param line: a text line found in an WHTML section via bs4
    :return: True if this line seems relevant, False otherwise.
    """
    blacklist_self = ['\n', ' ', '\t', ' ,', 'Ingredients', 'Instructions', 'Method', 'Directions', 'Advertisement']
    blacklist_parent = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style', 'img']
    return str(line) not in blacklist_self and line.parent.name not in blacklist_parent


def cleaner_map(line: str) -> str:
    return line.replace('\n', ' ').replace('\t', ' ')


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
    # Get their text
    ingredients_list = ingredients_section.find_all(text=True)
    instruction_list = instructions_section.find_all(text=True)
    # Filter irrelevants
    ingredients_list = list(map(cleaner_map, filter(blacklist_filter, ingredients_list)))
    instruction_list = list(map(cleaner_map, filter(blacklist_filter, instruction_list)))
    # Throw remaining text on the webpage to irrelevant list
    all_text = get_soup(simply_url).find_all(text=True)
    irrelevant_list = [line for line in all_text if line not in instruction_list and line not in ingredients_list]
    irrelevant_list = list(map(cleaner_map, filter(blacklist_filter, irrelevant_list)))
    # Return results
    return ingredients_list, instruction_list, irrelevant_list


def lemon_scrape(loveandlemons_url: str) -> Tuple[List[str], List[str], List[str]]:
    # Get the URL HTML and construct a soup around it
    soup = get_soup(loveandlemons_url)
    # Get the needed sectiyyons of the HTML
    ingredients_section = soup.find('div', {'class': 'wprm-recipe-ingredients-container'})
    instructions_section = soup.find('div', {'class': 'wprm-recipe-instructions-container'})
    if not ingredients_section or not instructions_section:
        print(loveandlemons_url)
        return [], [], []
    # Get their text
    ingredients_list = ingredients_section.find_all(text=True)
    instruction_list = instructions_section.find_all(text=True)
    # Filter irrelevants
    ingredients_list = list(map(cleaner_map, filter(blacklist_filter, ingredients_list)))
    instruction_list = list(map(cleaner_map, filter(blacklist_filter, instruction_list)))
    # Throw remaining text on the webpage to irrelevant list
    all_text = soup.find_all(text=True)
    irrelevant_list = [line for line in all_text if line not in instruction_list and line not in ingredients_list]
    irrelevant_list = list(map(cleaner_map, filter(blacklist_filter, irrelevant_list)))
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
def reset():
    open('ingredients.txt', 'w+').close()
    open('instructions.txt', 'w+').close()
    open('neither.txt', 'w+').close()

    SIMPLY_RECIPES = ["https://www.simplyrecipes.com/philly-cheesesteak-recipe-5188498",  "https://www.simplyrecipes.com/kentucky-hot-brown-5180178",  "https://www.simplyrecipes.com/shakshuka-with-feta-olives-and-peppers-5114919",  "https://www.simplyrecipes.com/recipes/steak_salad",  "https://www.simplyrecipes.com/tex-mex-chopped-chicken-salad-with-cilantro-lime-dressing-5179994",  "https://www.simplyrecipes.com/recipes/classic_rack_of_lamb/",  "https://www.simplyrecipes.com/spicy-tofu-stir-fry-recipe-5115374",  "https://www.simplyrecipes.com/easy-homemade-grenadine-recipe-5180859",  "https://www.simplyrecipes.com/recipes/bread_and_butter_pickles/",  "https://www.simplyrecipes.com/nashville-hot-chicken-recipe-5191597",  "https://www.simplyrecipes.com/nashville-hot-chicken-recipe-5191597",  "https://www.simplyrecipes.com/garden-walk-cocktail-recipe-5180844",  "https://www.simplyrecipes.com/frozen-margarita-5192682",  "https://www.simplyrecipes.com/pisco-sour-recipe-5192022",  "https://www.simplyrecipes.com/recipes/angel_food_cake/",  "https://www.simplyrecipes.com/recipes/how_to_make_the_best_detox_smoothie/",  "https://www.simplyrecipes.com/recipes/creamy_polenta_with_white_beans_and_roasted_broccoli/",  "https://www.simplyrecipes.com/recipes/chicken_and_dumplings/",  "https://www.simplyrecipes.com/recipes/pot_roast/",  "https://www.simplyrecipes.com/recipes/glazed_oxtails/"]
    ALLRECIPE_RECIPES = ['https://www.allrecipes.com/recipe/15985/grandmas-corn-pudding/',     'https://www.allrecipes.com/recipe/9316/grandmas-five-cup-salad/',     'https://www.allrecipes.com/recipe/247225/tomato-avocado-sandwich/',     'https://www.allrecipes.com/recipe/147360/fried-green-tomato-sandwich/',     'https://www.allrecipes.com/recipe/19163/luscious-slush-punch/',     'https://www.allrecipes.com/recipe/223400/old-school-mac-n-cheese/',     'https://www.allrecipes.com/recipe/238840/quick-crispy-parmesan-chicken-breasts/',     'https://www.allrecipes.com/recipe/239930/taco-meat/',     'https://www.allrecipes.com/recipe/276647/instant-pot-chicken-and-dumplings/',     'https://www.allrecipes.com/recipe/174517/angel-hair-pasta-with-lemon-and-chicken/',     'https://www.allrecipes.com/recipe/174525/shrimp-with-garlic-cream-sauce-over-linguine/',     'https://www.allrecipes.com/recipe/284442/broken-lasagna-pasta/', 'https://www.allrecipes.com/recipe/84745/steffs-shepherd-pie/', 'https://www.allrecipes.com/recipe/254247/personal-shepherds-pies/', 'https://www.allrecipes.com/recipe/25202/beef-stroganoff-iii/', 'https://www.allrecipes.com/recipe/23260/simple-hamburger-stroganoff/', 'https://www.allrecipes.com/recipe/234799/poor-mans-stroganoff/', 'https://www.allrecipes.com/recipe/241630/creamy-beef-tips-with-egg-noodles/', 'https://www.allrecipes.com/recipe/241630/creamy-beef-tips-with-egg-noodles/', 'https://www.allrecipes.com/recipe/262065/beef-stroganoff-casserole/', 'https://www.allrecipes.com/recipe/240773/quick-and-easy-hamburger-stroganoff/', 'https://www.allrecipes.com/gallery/chuck-roast-ideas/', 'https://www.allrecipes.com/recipe/260697/mississippi-pot-roast/', 'https://www.allrecipes.com/recipe/266830/instant-pot-barbacoa/', 'https://www.allrecipes.com/recipe/219448/healthier-beef-stroganoff-iii/', 'https://www.allrecipes.com/recipe/236322/chicago-inspired-italian-beef-sandwich/', 'https://www.allrecipes.com/recipe/221360/kates-easy-german-sauerbraten/', 'https://www.allrecipes.com/recipe/220059/chef-johns-classic-beef-stroganoff/', 'https://www.allrecipes.com/recipe/219046/rich-and-creamy-beef-stroganoff/', 'https://www.allrecipes.com/recipe/16311/simple-beef-stroganoff/', 'https://www.allrecipes.com/recipe/217935/sopa-de-fideos/', 'https://www.allrecipes.com/recipe/99873/apple-curry-turkey-pita/', 'https://www.allrecipes.com/recipe/244326/greek-farro-salad/', 'https://www.allrecipes.com/recipe/60037/california-melt/', 'https://www.allrecipes.com/recipe/215280/refreshing-lentil-salad/', 'https://www.allrecipes.com/recipe/158440/sophies-shepherds-pie/', 'https://www.allrecipes.com/recipes/17123/main-dish/beef/beef-stroganoff/', 'https://www.allrecipes.com/recipe/83637/green-bean-and-potato-salad/', 'https://www.allrecipes.com/recipe/91478/bbq-tuna-fritters/', 'https://www.allrecipes.com/recipe/233968/lemon-chicken-orzo-soup/', 'https://www.allrecipes.com/recipe/222119/healthier-sloppy-joes-ii/', 'https://www.allrecipes.com/recipe/241407/raw-beet-salad/', 'https://www.allrecipes.com/recipe/241443/tuna-artichoke-salad/', 'https://www.allrecipes.com/recipe/16715/vegetarian-chickpea-sandwich-filling/', 'https://www.allrecipes.com/recipe/220123/black-bean-breakfast-bowl/', 'https://www.allrecipes.com/recipe/233429/farm-fresh-zucchini-cranberry-nut-muffins/', 'https://www.allrecipes.com/recipe/21014/good-old-fashioned-pancakes/', 'https://www.allrecipes.com/recipe/158727/bacon-for-the-family-or-a-crowd/', 'https://www.allrecipes.com/recipe/23539/strawberry-oatmeal-breakfast-smoothie/', 'https://www.allrecipes.com/recipe/90295/moms-apple-fritters/', 'https://www.allrecipes.com/recipe/258117/quick-crispy-home-fries/', 'https://www.allrecipes.com/recipe/221988/eggs-benedict-casserole/', 'https://www.allrecipes.com/recipe/245713/bacon-and-egg-tacos/', 'https://www.allrecipes.com/recipe/233747/breakfast-cups/', 'https://www.allrecipes.com/recipe/190276/easy-shakshuka/', 'https://www.allrecipes.com/recipe/274974/lemon-ricotta-cornmeal-waffles/', 'https://www.allrecipes.com/recipe/256825/warm-berry-compote/', 'https://www.allrecipes.com/recipe/274464/slow-cooker-mediterranean-chicken-and-vegetables/', 'https://www.allrecipes.com/recipe/228498/slow-cooker-baby-back-ribs/', 'https://www.allrecipes.com/recipe/58312/slow-cooker-chai/', 'https://www.allrecipes.com/recipe/174543/slow-cooker-butter-chicken/', 'https://www.allrecipes.com/recipe/219782/meadowwood-tapioca-pudding/', 'https://www.allrecipes.com/recipe/274531/creamy-slow-cooker-steel-cut-oats/', 'https://www.allrecipes.com/recipe/275943/slow-cooker-chicken-bone-broth/', 'https://www.allrecipes.com/recipe/276968/slow-cooked-stew-meat-chili/', 'https://www.allrecipes.com/recipe/256610/grandmas-hungarian-stuffed-cabbage-slow-cooker-variation/', 'https://www.allrecipes.com/recipe/276451/slow-cooker-turkey-meatballs-in-tomato-sauce/', 'https://www.allrecipes.com/recipe/277492/slow-cooker-vegan-leek-and-potato-soup/', 'https://www.allrecipes.com/recipe/35781/california-italian-wedding-soup/', 'https://www.allrecipes.com/recipe/212931/chicken-sotanghon/', 'https://www.allrecipes.com/recipe/53887/cindys-awesome-clam-chowder/', 'https://www.allrecipes.com/recipe/276720/west-african-style-peanut-stew-with-chicken/', 'https://www.allrecipes.com/recipe/151046/fabulous-roasted-cauliflower-soup/', 'https://www.allrecipes.com/recipe/273157/instant-pot-turkey-chili/', 'https://www.allrecipes.com/recipe/263694/homemade-miso-soup/', 'https://www.allrecipes.com/recipe/232665/asparagus-lemon-and-mint-soup/', 'https://www.allrecipes.com/recipe/261790/caldo-verde-portuguese-sausage-kale-soup/', 'https://www.allrecipes.com/recipe/279294/chicken-taco-soup-for-two/', 'https://www.allrecipes.com/recipe/233603/bacon-wrapped-jalapeno-poppers/', 'https://www.allrecipes.com/recipe/262928/simply-the-best-deviled-eggs/', 'https://www.allrecipes.com/recipe/266759/vegan-spinach-artichoke-dip/', 'https://www.allrecipes.com/recipe/69225/strawberry-bruschetta/', 'https://www.allrecipes.com/recipe/163625/simply-guacamole/', 'https://www.allrecipes.com/recipe/284069/air-fried-bacon-wrapped-shrimp/', 'https://www.allrecipes.com/recipe/47179/crab-and-lobster-stuffed-mushrooms/']
    LEMON_RECIPES = ["https://www.loveandlemons.com/grilled-sweet-potatoes/", "https://www.loveandlemons.com/forbidden-black-rice", "https://www.loveandlemons.com/pinto-beans-recipe/", 'https://www.loveandlemons.com/black-beans-recipe/', 'https://www.loveandlemons.com/veggie-noodles/', 'https://www.loveandlemons.com/grilled-corn-on-the-cob/', 'https://www.loveandlemons.com/guacamole-recipe/', 'https://www.loveandlemons.com/polenta-recipe/', 'https://www.loveandlemons.com/grilled-vegetables/', 'https://www.loveandlemons.com/corn-salsa/', 'https://www.loveandlemons.com/homemade-salsa-recipe/', 'https://www.loveandlemons.com/chipotle-vinaigrette/', 'https://www.loveandlemons.com/cold-brew-coffee/', 'https://www.loveandlemons.com/gazpacho-recipe/', 'https://www.loveandlemons.com/mojito-recipe/', 'https://www.loveandlemons.com/cold-cucumber-soup/', 'https://www.loveandlemons.com/chickpea-salad-recipe/', 'https://www.loveandlemons.com/grilled-vegetables/', 'https://www.loveandlemons.com/roasted-vegetable-pasta/', 'https://www.loveandlemons.com/stuffed-zucchini-boats/', 'https://www.loveandlemons.com/couscous-salad/', 'https://www.loveandlemons.com/kale-salad/', 'https://www.loveandlemons.com/grilled-sweet-potatoes/', 'https://www.loveandlemons.com/watermelon-juice/', 'https://www.loveandlemons.com/vegan-potato-salad/', 'https://www.loveandlemons.com/cookout-food-ideas/', 'https://www.loveandlemons.com/potato-leek-soup/', 'https://www.loveandlemons.com/asparagus-soup/', 'https://www.loveandlemons.com/cabbage-soup/', 'https://www.loveandlemons.com/cookout-food-ideas/', 'https://www.loveandlemons.com/vegan-quesadilla-recipe/', 'https://www.loveandlemons.com/cannellini-beans-recipe/', 'https://www.loveandlemons.com/cauliflower-soup/', 'https://www.loveandlemons.com/tortellini-soup/', 'https://www.loveandlemons.com/vegan-sushi/', 'https://www.loveandlemons.com/power-bowl-recipe/', 'https://www.loveandlemons.com/kale-recipes/', 'https://www.loveandlemons.com/kale-recipes/', 'https://www.loveandlemons.com/black-bean-soup-recipe/', 'https://www.loveandlemons.com/kale-recipes/', 'https://www.loveandlemons.com/plant-based-recipes/', 'https://www.loveandlemons.com/sweet-potato-salad-recipe/', 'https://www.loveandlemons.com/soup-au-pistou/', 'https://www.loveandlemons.com/roasted-red-pepper-soup/', 'https://www.loveandlemons.com/vegetarian-lasagna/', 'https://www.loveandlemons.com/arugula-salad/', 'https://www.loveandlemons.com/linguine-fennel-winter-greens/', 'https://www.loveandlemons.com/sun-dried-tomato-pasta/', 'https://www.loveandlemons.com/minty-millet-pomegranate-salad/', 'https://www.loveandlemons.com/vegetarian-lasagna/', 'https://www.loveandlemons.com/vegan-pasta-salad/', 'https://www.loveandlemons.com/roasted-vegetable-pasta/', 'https://www.loveandlemons.com/couscous-salad/', 'https://www.loveandlemons.com/vegan-sour-cream-recipe/', 'https://www.loveandlemons.com/broccoli-slaw-recipe/', 'https://www.loveandlemons.com/refried-beans/', 'https://www.loveandlemons.com/how-to-cut-a-mango/', 'https://www.loveandlemons.com/taco-toppings/', 'https://www.loveandlemons.com/pinto-beans-recipe/', 'https://www.loveandlemons.com/cauliflower-tacos/', 'https://www.loveandlemons.com/avocado-sauce/', 'https://www.loveandlemons.com/grilled-onions/', 'https://www.loveandlemons.com/breakfast-cookies/', 'https://www.loveandlemons.com/portobello-mushroom-burger/', 'https://www.loveandlemons.com/almond-butter-recipe/', 'https://www.loveandlemons.com/lemon-butter-sauce/', 'https://www.loveandlemons.com/carrot-cake-cookies/', 'https://www.loveandlemons.com/cauliflower-recipes/', 'https://www.loveandlemons.com/shredded-carrots/', 'https://www.loveandlemons.com/how-to-make-almond-milk/', 'https://www.loveandlemons.com/broccoli-pesto/', 'https://www.loveandlemons.com/potato-leek-soup/', 'https://www.loveandlemons.com/cold-soup-recipes/', 'https://www.loveandlemons.com/cabbage-soup/', 'https://www.loveandlemons.com/cannellini-beans-recipe/']

    save('simply', SIMPLY_RECIPES)
    save('allrecipe', ALLRECIPE_RECIPES)
    save('lemon', LEMON_RECIPES)


if __name__ == '__main__':
    # site = argv[1]
    # urls = argv[2:]
    # save(site, urls)

    SIMPLY_RECIPES = ["https://www,simplyrecipes,com/philly-cheesesteak-recipe-5188498", "https://www,simplyrecipes,com/kentucky-hot-brown-5180178", "https://www,simplyrecipes,com/shakshuka-with-feta-olives-and-peppers-5114919", "https://www,simplyrecipes,com/recipes/steak_salad", "https://www,simplyrecipes,com/tex-mex-chopped-chicken-salad-with-cilantro-lime-dressing-5179994", "https://www,simplyrecipes,com/recipes/classic_rack_of_lamb/", "https://www,simplyrecipes,com/spicy-tofu-stir-fry-recipe-5115374", "https://www,simplyrecipes,com/easy-homemade-grenadine-recipe-5180859", "https://www,simplyrecipes,com/recipes/bread_and_butter_pickles/", "https://www,simplyrecipes,com/nashville-hot-chicken-recipe-5191597", "https://www,simplyrecipes,com/nashville-hot-chicken-recipe-5191597", "https://www,simplyrecipes,com/garden-walk-cocktail-recipe-5180844", "https://www,simplyrecipes,com/frozen-margarita-5192682", "https://www,simplyrecipes,com/pisco-sour-recipe-5192022", "https://www,simplyrecipes,com/recipes/angel_food_cake/", "https://www,simplyrecipes,com/recipes/how_to_make_the_best_detox_smoothie/", "https://www,simplyrecipes,com/recipes/creamy_polenta_with_white_beans_and_roasted_broccoli/", "https://www,simplyrecipes,com/recipes/chicken_and_dumplings/", "https://www,simplyrecipes,com/recipes/pot_roast/", "https://www,simplyrecipes,com/recipes/glazed_oxtails/"]
    LEMON_RECIPES = ['https://www.allrecipes.com/recipe/15985/grandmas-corn-pudding/','https://www.allrecipes.com/recipe/9316/grandmas-five-cup-salad/','https://www.allrecipes.com/recipe/247225/tomato-avocado-sandwich/','https://www.allrecipes.com/recipe/147360/fried-green-tomato-sandwich/','https://www.allrecipes.com/recipe/19163/luscious-slush-punch/','https://www.allrecipes.com/recipe/223400/old-school-mac-n-cheese/',,'https://www.allrecipes.com/recipe/238840/quick-crispy-parmesan-chicken-breasts/','https://www.allrecipes.com/recipe/239930/taco-meat/','https://www.allrecipes.com/recipe/276647/instant-pot-chicken-and-dumplings/','https://www.allrecipes.com/recipe/174517/angel-hair-pasta-with-lemon-and-chicken/','https://www.allrecipes.com/recipe/174525/shrimp-with-garlic-cream-sauce-over-linguine/','https://www.allrecipes.com/recipe/284442/broken-lasagna-pasta/','https://www.loveandlemons.com/black-beans-recipe/','https://www.loveandlemons.com/veggie-noodles/','https://www.loveandlemons.com/grilled-corn-on-the-cob/','https://www.loveandlemons.com/guacamole-recipe/','https://www.loveandlemons.com/polenta-recipe/','https://www.loveandlemons.com/grilled-vegetables/','https://www.loveandlemons.com/corn-salsa/','https://www.loveandlemons.com/homemade-salsa-recipe/']
    ALLRECIPE_RECIPES = ['']

    save('simply', SIMPLY_RECIPES)
