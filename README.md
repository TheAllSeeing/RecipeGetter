# RecipeGetter
An assignment in NLP and basic web scraping, to create a program that extracts ingredients and directions front recipe 
from a webpage, and output a JSON containing them, to parse.

  * [Usage](#usage)
  * [How the program works](#how-the-program-works)
  * [Project Structure](#project-structure)
    * [The Model](#the-model)
    * [The Dataset](#the-dataset)
      * [Epicurious Dataset](#epicurious-dataset)
      * [Scraping](#scraping)
      * [Assembling the data](#assembling-the-data)
    * [Prepare Script](#prepare-script)
    * [Main & Run scripts](#main-&-run-scripts)
  * [Packages](#packages)
  * [Time Complexity](#time-complexity)
  * [Space Complexity](#space-complexity)
  * [Program Limitations](#program-limitations)
  * [Bugs](#bugs)

## Usage
```bash
./run.sh "https://www.allrecipes.com/recipe/245899/savory-parmesan-french-toast/"

```

```
{

	ingredients: [
		⅓ cup grated Parmesan cheese,
		ground black pepper to taste,
		1 tablespoon butter, plus more as needed,
		4 slices whole wheat bread
	]

	instructions: "Step 1

		Whisk eggs, Parmesan cheese, milk, and black pepper in a shallow bowl until light and fluffy, about 1 minute.

		Step 2

		Melt butter in a large skillet over medium heat.

		Step 3

		Dip both sides of each slice of bread in the egg mixture and place in the skillet. Cook until golden brown, 2 to 3 minutes per side. Transfer to a warmed plate and dot with butter to serve."
}
```
\
To regenerate the data files and models, run
```bash
./prepare
```

## How the program works
1. requests package is used to extract the HTML code from the URL
2. beautiful soup is used to extract plain text from the page
3. A neural network classifier than calculates probability of each line, 
   with some common phrases (e.g "Step 3") detected automatically prior.
4. From the generated ingredient and instruction list, a JSON is created.

## Project Structure

### The Model
```python

    model = tf.keras.Sequential([
        tf.keras.layers.Embedding(10_000, 16, input_length=600),
        tf.keras.layers.GlobalAveragePooling1D(),
        tf.keras.layers.Dense(24, activation='selu'),
        tf.keras.layers.Dense(32, activation='selu'),
        tf.keras.layers.Dense(32, activation='selu'),
        tf.keras.layers.Dense(24, activation='selu'),
        tf.keras.layers.Dense(2, activation='sigmoid')
    ])

    model.compile(loss=keras.losses.mean_squared_error, optimizer='adam', metrics=['accuracy'])
```
The model used to classify paragraphs has 7 layers — without significant opening/closing and in a similar enough style
   to actual instructions (such that it could have also been a valid paragraph)
1. An input embedding layer, which vectorizes each word into its semantic components. 
   Input size is determined as 600; paragraphs to classify are sequenced by a tokenizer 
   and padded accordingly. This results in matrix, which is a list of each word vector.
1. A global average over one dimension. This reduces each word to its average value across 
   the semantic components.
1. 4 layers of a "basic" neural network, selu-activated, which should (after training) map 
   from the embedding feature maps into classification probabilities.
1. An output sigmoid-activated layer, with 2 neurons representing the probability of the input being 
   either an ingredient or an instruction. 
   
   While SoftMax activation is often used for classification 
   into exclusive categories (like ingredient and instruction.), this model 
   also needs to classify inputs that fit none of the categories
   
The model's loss function is MSE. Similarly to the output activation, here MSE is 
chosen over the common cross-entropy classification loss, because cross entropy's 
use of log probability and one-hot encoding means that it cannot be used to train 
all-0 labels.

The model uses the mostly standard optimizer Adam.

The model is defined, trained, and tested in the `classifier.py` script.

The model itself and the tokenizer used to preprocess its input are both saved 
under the **savefiles** direcory, in **classifier** and **classifier_tokenizer**, respectively.

### The Dataset
The dataset used for training and testing composed of two main sources: 
 - *Epicurious - Recipes with Rating and Nutrition* open dataset by Hugo 
  Darwood on Kraggle, found [here](https://www.kaggle.com/hugodarwood/epirecipes?select=full_format_recipes.json).
 - Ingredient and instruction data I scraped from 255 pages from  allrecipe.com, 

#### Epicurious Dataset
*Epicurious - Recipes with Rating and Nutrition* is a public dataset containing 
a list of over 20 thousand recipes from the website www.epicurious.com/. Each 
recipe contains directions, fat, upload date, categories, calories, description, 
protein, rating and title, all in a JSON format.

In total, the Epicurious dataset contains **199,030** ingredients with **83,465** unique
values and **69,458**  instructions with **61,580** unique values.

The epicurious dataset is saved under the **datafiles** directory, in the file
**dataset.json**.

#### Scraping
The Epicurious dataset had two significant downsides: first, it only contains 
data from one website, so its ability to generalize is to all sites is not
very high. Secondly, it does *not* contain any of the non-recipe data that is 
contained on every webpage (such as comments and links), which would be a significant 
part of the text I would need to classify.

For this purpose, the `scrape_data.py` script is used to parse recipe webpages 
into their ingredients and instructions and write it into additional data files.

I wrote custom functions for the sites https://www.allrecipes.com/, 
https://www.simplyrecipes.com/, https://www.loveandlemons.com/ and 
https://www.foodnetwork.com/; each processed a page's HTML and retrieves
the ingredient and instructions sections. Then, data is written into 
**ingredients.txt, instructions.txt** and **neither.txt** under the **datafiles** 
directory. *neither.txt* contains all of the page data that was classified as 
neither ingredient nor instruction.

The list of URLs from each site used to generate the training data for the current version of 
the model is saved under the **scrapeurls** directory, in **simply.txt**, **allrecipes.txt,** 
**lemon.txt** and **network.txt** for *simplyrecipes.com, allrecipes.com, loveandlemons.com* and 
*foodnetwork.com,* respectively.

#### Assembling the data
The `assemble_data.py` script is used to join the data from the different sources into a single 
table containing all of the ingredient and instruction data, kept in a TSV file.

The file read from the TXT file and parses the JSON file (using python 
`eval` rather than the `json` package), and then writes it all together 
with appropriate labels as a tab-separated table, into **dataset.tsv** under 
the **datafiles** directory

In order to keep an equal amount of each class, the assembling script uses 
only 60,000 values for each class. It also removed duplicates prior, such 
that the model will face more different values and be able to generalize better.

Due to previous iterations of the model, irrelevant (neither) data is parsed 
separately during training.

### Prepare Script
The main program of this project actually comprises a rather small part of it. 
The large chunk of code here is trains and saves the model which the main 
program uses to classify input, and generates the data used to train that model.

The `./run.sh` script only runs this main function, which reliaes on the model 
and data. While the model and data are saved in the repository, 

`prepare.sh` is a script which gives the user a more direct access to the generation of the model and the data, in
case they are corrupted or lost. Basically it runs scrape_data.py, 
assemble_data.py and classifier.py in sequence. Scraping data, assembling it and 
generating the model.

### Main & Run scripts
The `main.py` script contains the main body of the program, as detailed 
in the [How the program works](##how-the-program-works) section.

The script `run.sh` is a bash script which wraps `main.py` to allow it to be 
ran more easily from terminal. It simply runs the apropriate function from main.py,
redirects stderr to a tempfile and reports errors if they come up.

## Packages
- **requests**
  - retrieving HTML code from webpages to process, in the main program 
    and in scraping.
- **bs4**
  - Preprocessing webpage in main program to get plain text
  - Scraping recipe pages to get training data.
- **tensorflow**
   - Constructing the neural network model, training and saving it.
- **numpy**
   - Constructing model input as numpy arrays
   - Calculating average prediction for each class in testing
- **typing**
   - Creating more detailed type hints for lists, dictionaries and tuples

The assignment was restricted to *pandas, numpy, pytorch, tensorflow* and *bs4*, with 
additional packages requiring approval. As detailed above, I also  used requests to get 
webpage data and typing for better documentation.

## Time Complexity
1. Downloading the webpage is **O(n)**
1. Soup's `find_all` is a tree traversal with, **O(n)**, 
  with **O(1)** condtional checks at each point. **O(n\*1) = O(n)**
1. Checking paragraph against a constant blacklist is **O(1)**, so doing 
  it for every paragraph is **O(1\*n)** = **O(n)**
1. Tokenizing each word is done with a hashmap so it's **O(1)**. Thus, 
  tokenizing the entire contents is **O(1\*n)** = **O(n)**
1. Model predictions are done via constant mathematical calculation for 
  identically1.sized inputs. so it's **O(1)**. Predicting each paragraph, 
  then, is **O(1\*n)** = **O(n)**.
1. Checking classification (conditionals against prediction value) is 
  **O(1)**, so checking classification for each paragraph is **O(1\*n)** = **O(n)**
1. Building the JSON iterates over the list so it's **O(n)** 

**O(n) + O(n) + O(n) + O(n) + O(n) + O(n) = O(n)**

**Time Complexity is O(n)**

## Space Complexity
The program keeps the contents of thw webpage at O(n) and the classifications 
for each of its paragraphs, also at O(n).

**O(n) + O(n) = O(n)**

**Space Complexity is O(n)**

## Program Limitations
 - Some sites block automated requests. These sites can thus not be processed and will return an empty 
   ingredient list and empty instructions.
   
   ##### Known Affected Sites
    - www.tasteofhome.com
    
    
 - The program judges each paragraph in the page independent of its context. 
   Thus, if a comment or review present in the page quotes the instructions
   without significant additions, or adds its own instructions for modifying 
   the recipe in such a way that the comment could be a valid paragraph in 
   the instructions, it could be misidentified. 
   
   This happens quite rarely, 
   as the vast majority of comments, when containing instructions,
   also contain enough additional notes, explanation and review of the recipe 
   to be classified them as invalid for instructions.
   
   This does not generally happen with ingredients, as they have a much 
   less flexible structure and are also simply shorter, such that even 1-word 
   are quite noticeable.

## Bugs
 - Due to the way some sites format links and ingredient amounts, parts of each ingredient
   might be split of in the HTML pre-processing. Thus, _"5-pound ripe tomatoes"_ might be divided into `"5",
   "pound", "ripe tomatoes"`. Then usually the unit and the ingredient itself are detected, but the 
   amount is classified as junk. This results in the ingredients `"pound", "ripe tomatoes"`.
   
   This bug occurs fairly rarely (usually outside the first page of google results)
   
   ##### Known Affected Sites
    - www.loveandlemons.com
    - www.yummly.com
   
