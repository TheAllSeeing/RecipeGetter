import tensorflow as tf
import numpy as np
from typing import Type, List, Any
from bs4 import element
from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences

DATAFILES = ['datafiles/' + filename for filename in ['ingredients.txt', 'instructions.txt', 'neither.txt']]


class ModelSaver(tf.keras.callbacks.Callback):
    def __init__(self, accuracy_threshold: float, model_path: str):
        super().__init__()
        self.accuracy_threshold = accuracy_threshold
        self.model_path = model_path

    def on_epoch_end(self, epoch, logs={}):
        if logs.get('val_accuracy') >= self.accuracy_threshold:
            print(f"\nReached {self.accuracy_threshold * 100}% on validation tests. "
                  f"Saving to '{self.model_path}' directory and exiting. ")
            self.model.save(self.model_path)
            self.model.stop_training = True


def save_tokenizer(tokenizer, filepath):
    with open(filepath, 'w+') as tokenizer_file:
        tokenizer_file.write(tokenizer.to_json())


def load_tokenizer(filepath) -> tf.keras.preprocessing.text.Tokenizer:
    with open(filepath, 'r') as tokenizer_file:
        return tf.keras.preprocessing.text.tokenizer_from_json(tokenizer_file.read())


def test_on_scraped(model: tf.keras.Sequential, labels: List[List[int]], tokenizer: Tokenizer, max_input_length: int):
    for filename, label in zip(DATAFILES, labels):
        with open(filename, 'r') as datafile:
            test_data = datafile.readlines()
        test_labels = np.array([label for _ in test_data])
        test_data = preprocess_data(test_data, tokenizer, max_input_length)
        print(filename)
        model.evaluate(test_data, test_labels)
        predictions = model.predict(test_data)
        print('AVERAGE: ' + str(np.mean(predictions, axis=0)))


def preprocess_data(raw_data: List[str], tokenizer: Tokenizer, max_length: int) -> np.ndarray:
    """
    Does preprocessing for textual training data, passing it through a tokenizer (defined in the "Tokenizing/Embedding
    section at the start of this script), padding it
    :param raw_data: A list of raw textual entries the model needs to process
    :param tokenizer: The tokenizer to use for preprocessing
    :param max_length: The maximum length (in words) of a given input to the model
    :return: A 2d array of ints representing the sentences, each inner array being a valid model input
    """
    sequences = tokenizer.texts_to_sequences(raw_data)
    padded = pad_sequences(sequences, maxlen=max_length)
    return np.array(padded)


def preprocess_labels(labels: List[List[int]]) -> np.array:
    """
    Does preprocessing for list labels. Really it just converts them to arrays, but it exists for order for order
    with preprocess
    :param labels: a 2d list of integer labels matching the sentence dataset
    :return: The labels as an numpy array object, which can be used with keras models.
    """
    return np.array(labels)


def _blacklist_filter(line: Any) -> bool:
    """
    A predicate used to filter out irrelevant lines often found in ingredient and instructions
    sections. This will include titles, blank lines and spaces, and all assoetments of HTML/CSS/JS code.

    :param line: a text line found in an WHTML section via bs4
    :return: True if this line seems relevant, False otherwise.
    """
    blacklist_self = ['\n', ' ', '\t', ' ,', 'Ingredients', 'Instructions', 'Method', 'Directions', 'Advertisement']
    if issubclass(type(line), element.PageElement):
        blacklist_parent = ['[document]', 'noscript', 'header', 'html', 'meta', 'head', 'input', 'script', 'style', 'img']
        return str(line) not in blacklist_self and line.parent.name not in blacklist_parent
    return str(line) not in blacklist_self


def _cleaner_map(line: str) -> str:
    return ' '.join(line.split())


def clean_paragraphs(paragraphs: Any) -> List[str]:
    return list(map(_cleaner_map, filter(_blacklist_filter, paragraphs)))

