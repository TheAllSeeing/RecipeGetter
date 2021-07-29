import nlp_utils as utils
import tensorflow as tf
import numpy as np
from tensorflow import keras
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing.text import Tokenizer
from typing import Tuple, List
from nlp_utils import ModelSaver

# -------- Data Parameters --------
DATASET_FILE = 'datafiles/dataset.tsv'
TRAINING_SIZE = 100_000
MODEL_PATH = 'savefiles/Classifier'
TOKENIZER_PATH = 'savefiles/classifier_tokenizer.json'
# ----------------


# ======== MODEL CLASSES ========
# ================


# -------- Tokenizing/Embedding parameters --------
VOCABULARY_SIZE = 10_000
EMBEDDING_DIMENSIONS = 16
MAX_INPUT_LENGTH = 600
OOV_TOKEN = "<OOV>"
# ----------------

# -------- Training Parameters --------
MAX_EPOCHS = 5
ACCURACY_THRESHOLD = 0.99
"""If the model passes this threshold in its accuracy on the validation dataset, it is saved and the training ends."""
CALLBACKS = [ModelSaver(ACCURACY_THRESHOLD, MODEL_PATH)]
# ----------------
# ================

# ======== MODEL OBJECTS ========
TOKENIZER = Tokenizer(num_words=VOCABULARY_SIZE, oov_token=OOV_TOKEN)
MODEL = tf.keras.Sequential([
    tf.keras.layers.Embedding(VOCABULARY_SIZE, EMBEDDING_DIMENSIONS, input_length=MAX_INPUT_LENGTH),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(24, activation='selu'),
    tf.keras.layers.Dense(32, activation='selu'),
    tf.keras.layers.Dense(32, activation='selu'),
    tf.keras.layers.Dense(24, activation='selu'),
    tf.keras.layers.Dense(2, activation='sigmoid')
])
# ================


# ======== DATA FUNCTIONS ========
def unpack_tsv(filepath: str) -> Tuple[List[str], List[List[int]]]:
    """
    Unpacks the dataset TSV generated by assemble_data.py into the list of paragraphs and the list of their corresponding
    label vectors

    :param filepath: the path the TSV file was generated to
    :return: A tuple of the list of training paragraphs and the list of their corresponding label vectors
    """
    raw_data = []
    labels = []
    with open(filepath) as tsvfile:
        for i, item in enumerate(tsvfile.readlines()):
            cells = item.split('\t')
            raw_data.append(cells[0])
            label = cells[1].split(',')
            label = [int(i) for i in label]
            labels.append(label)

        return raw_data, labels


def get_data() -> Tuple[Tuple[np.ndarray, np.array], Tuple[np.ndarray, np.array]]:
    """

    :return:
    """
    raw_data, labels = unpack_tsv(DATASET_FILE)

    TOKENIZER.fit_on_texts(raw_data[:TRAINING_SIZE])
    utils.save_tokenizer(TOKENIZER, TOKENIZER_PATH)

    processed_data = preprocess_data(raw_data)
    processed_labels = utils.preprocess_labels(labels)

    training_data, training_labels = processed_data[:TRAINING_SIZE], processed_labels[:TRAINING_SIZE]
    testing_data, testing_labels = processed_data[TRAINING_SIZE:], processed_labels[TRAINING_SIZE:]
    return (training_data, training_labels), (testing_data, testing_labels)


def preprocess_data(raw_data: List[str]):
    return utils.preprocess_data(raw_data, utils.load_tokenizer(TOKENIZER_PATH), MAX_INPUT_LENGTH)


def predict(raw_data: List[str], load=True) -> List[List[float]]:
    if load:
        model = load_model(MODEL_PATH)
    else:
        model = MODEL
    return model.predict(preprocess_data(raw_data))
# ================


# ======== MODEL FUNCTIONS ========
def train_model(verbose: int = 1):
    MODEL.compile(loss=keras.losses.mean_squared_error, optimizer='adam', metrics=['accuracy'])
    training_dataset, testing_dataset = get_data()
    MODEL.fit(*training_dataset, validation_data=testing_dataset, epochs=MAX_EPOCHS, callbacks=CALLBACKS,
              verbose=verbose)

def test_on_json(model: tf.keras.Sequential):
    _, (test_data, test_labels) = get_data()
    model.evaluate(test_data, np.array(test_labels))


def test_on_scraped(model: tf.keras.Sequential):
    utils.test_on_scraped(model, [[1, 0], [0, 1], [0, 0]], TOKENIZER, MAX_INPUT_LENGTH)

# ================


# ======== RUNNING SCRIPT ========
if __name__ == '__main__':
    train_model()
    MODEL.save(MODEL_PATH)
    # print()
    # test_model(MODEL)
    # print()

    model = load_model(MODEL_PATH)
    test_on_json(model)
    test_on_scraped(model)
    # test_model(tf.keras.models.load_model(MODEL_PATH))
    # test_model(tf.keras.models.load_model(MODEL_PATH))
    # test_model(tf.keras.models.load_model(MODEL_PATH))
# ================
