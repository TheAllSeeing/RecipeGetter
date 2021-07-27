from tensorflow.keras.preprocessing.text import Tokenizer
from tensorflow.keras.preprocessing.sequence import pad_sequences
import tensorflow as tf
import numpy as np



# -------- Data Parameters --------
DATASET_FILE = 'dataset.tsv'
TRAINING_SIZE = 60_000
MODEL_PATH = 'Model'
# ----------------


# ======== MODEL CLASSES ========
class ModelSave(tf.keras.callbacks.Callback):
    def on_epoch_end(self, epoch, logs={}):
        if logs.get('val_accuracy') >= 0.99:
            print("\nReached 99% on validation tests. Saving to 'model' directory and exiting. ")
            self.model.save(MODEL_PATH)
            MODEL.save_weights('model_weights')
            self.model.stop_training = True
# ================


# -------- Tokenizing/Embedding parameters --------
VOCABULARY_SIZE = 10_000
EMBEDDING_DIMENSIONS = 16
MAX_INPUT_LENGTH = 600
OOV_TOKEN = "<OOV>"
# ----------------

# -------- Training Parameters --------
MAX_EPOCHS = 10
ACCURACY_THRESHOLD = 0.97
"""If the model passes this threshold in its accuracy on the validation dataset, it is saved and the training ends."""
CALLBACKS = [ModelSave()]
# ----------------
# ================

# ======== MODEL OBJECTS ========
TOKENIZER = Tokenizer(num_words=VOCABULARY_SIZE, oov_token=OOV_TOKEN)
MODEL = tf.keras.Sequential([
    tf.keras.layers.Embedding(VOCABULARY_SIZE, EMBEDDING_DIMENSIONS, input_length=MAX_INPUT_LENGTH),
    tf.keras.layers.GlobalAveragePooling1D(),
    tf.keras.layers.Dense(24, activation='relu'),
    tf.keras.layers.Dense(32, activation='relu'),
    tf.keras.layers.Dense(24, activation='relu'),
    tf.keras.layers.Dense(1, activation='sigmoid')
])


# ================

# ======== DATA FUNCTIONS ========
def unpack_tcv(filepath: str):
    raw_data = []
    labels = []
    with open(filepath) as datafile:
        for item in datafile.readlines():
            cells = item.split('\t')
            raw_data.append(cells[0])
            labels.append(int(cells[1]))
        return raw_data, labels


def preprocess_data(raw_data: list) -> np.ndarray:
    """
    Does preprocessing for textual training data, passing it through a tokenizer (defined in the "Tokenizing/Embedding
    section at the start of this script), padding it
    :param raw_data: A list of raw textual entries the model needs to process
    :return: A 2d array of ints representing the sentences, each inner array being a valid model input
    """
    TOKENIZER.fit_on_texts(raw_data)
    sequences = TOKENIZER.texts_to_sequences(raw_data)
    padded = pad_sequences(sequences, maxlen=MAX_INPUT_LENGTH)
    return np.array(padded)


def preprocess_labels(labels: List[str]) -> np.array:
    """
    Does preprocessing for list labels. Really it just converts them to arrays, but it exists for order for order
    with preprocess
    :param labels: a 2d list of integer labels matching the sentence dataset
    :return: The labels as an numpy array object, which can be used with keras models.
    """
    return np.array(labels)


def get_data() -> Tuple[Tuple[np.ndarray, np.array], Tuple[np.ndarray, np.array]]:
    """

    :return:
    """
    raw_data, labels = unpack_tcv(DATASET_FILE)
    processed_data = preprocess_data(raw_data)
    processed_labels = preprocess_labels(labels)
    training_data, training_labels = processed_data[:TRAINING_SIZE], processed_labels[:TRAINING_SIZE]
    testing_data, testing_labels = processed_data[TRAINING_SIZE:], processed_labels[TRAINING_SIZE:]
    return (training_data, training_labels), (testing_data, testing_labels)


# ================


# ======== MODEL FUNCTIONS ========

def load_model() -> tf.keras.Sequential:
    return tf.keras.models.load_model(MODEL_PATH)


def train_model(verbose: int = 1):
    MODEL.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    training_dataset, testing_dataset = get_data()
    MODEL.fit(*training_dataset, validation_data=testing_dataset, epochs=MAX_EPOCHS, callbacks=CALLBACKS,
              verbose=verbose)


def test_model_dataset(model: tf.keras.Sequential):
    _, (test_data, test_labels) = get_data()

    model.evaluate(test_data, np.array(test_labels))


def test_model_manual_dataset(model: tf.keras.Sequential):
    for filename, label in {'ingredients.txt': [1, 0, 0], 'instructions.txt': [0, 1, 0], 'neither.txt': [0, 0, 1]}.items():
        with open(filename, 'r') as datafile:
            test_data = datafile.readlines()
        test_labels = np.array([label for _ in test_data])
        test_data = preprocess_data(test_data)
        print(filename)
        model.evaluate(test_data, test_labels)


def test_model_new(model: tf.keras.Sequential):
    new_data = [
        '''Place the flour on a clean work surface and make a nest. Add the eggs, olive oil, and salt to the center and use a
            fork to gently break up the eggs, keeping the flour walls intact as best as you can. Use your hands to gently bring the
            flour inward to incorporate. Continue working the dough with your hands to bring it together into a shaggy ball.''',
        '''Set the dough piece onto a countertop or work surface. Fold both short ends in to meet in the center, then fold the
            dough in half to form a rectangle (see photo above).''',
        '2 cups all-purpose flour',
        '½ teaspoon sea salt'
    ]

    new_data = preprocess_data(new_data)

    print("MODEL:")
    print(model.predict(new_data))
    print('\nEXPECTED:')
    print('[1, 1, 0, 0]')

def predict(paragraph: str, load: bool=True) -> float:
    if load:
        model = load_model()
    else:
        model = MODEL
    return model.predict(preprocess_data([paragraph]))
# ================


# ======== RUNNING SCRIPT ========
if __name__ == '__main__':
    # train_model()
    # MODEL.save(MODEL_PATH)
    # print()
    # test_model(MODEL)
    print()
    test_model(tf.keras.models.load_model(MODEL_PATH))
# ================
