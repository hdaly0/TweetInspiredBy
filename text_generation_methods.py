"""
Ocean HD
Jan 2020

Methods to deal with training text generation models and generating text from the various models
"""
"""===IMPORTS======================================================================================================="""


import os
from itertools import combinations
import markovify
import spacy


from custom_exceptions import NoMatchingDatasetsException


"""===CONSTANTS====================================================================================================="""


DATA_DIRECTORY = "data/clean/"
MODEL_DIRECTORY = "models/"

# Server has limited compute so limit the size of the models by setting an upper limit to size of training data
MAX_NUMBER_TRAINING_LINES_PER_MODEL = 2000

nlp = spacy.load("en_core_web_sm")


"""===SETUP=AND=CONFIG=============================================================================================="""


# Use spaCy
class POSifiedText(markovify.Text):
    def word_split(self, sentence):
        return ["::".join((word.orth_, word.pos_)) for word in nlp(sentence)]

    def word_join(self, words):
        sentence = " ".join(word.split("::")[0] for word in words)
        return sentence


"""===HELPER=FUNCTIONS=============================================================================================="""


def get_file_name_from_full_path(file_path):
    """
    Remove any directory info and file extensions to just get the file name of an inputted path/file with extension
    :param file_path: string path or name of file to be standardised/cleaned, potentially with a file extension
    :return: string of just the file name
    """
    # Remove any preceding path directory info before the file name
    file_path = file_path[file_path.rfind("/") + 1:]

    # Remove any file extensions at the end of the file name (remove everything after the first ".")
    if file_path.find(".") != -1:
        file_path = file_path[:file_path.find(".")]

    return file_path


def get_combined_model_index(model_names):
    """
    Given an iterable of strings (model names) this method provides a consistent way of creating a string index that
    can be used as the key to a dictionary (i.e. it is hashable)
    :param model_names: list, set, or iterable of strings
    :return: string
    """
    return str(sorted(set(model_names)))


# TODO: Add logic to check if all data assets have corresponding models etc. and recreate if not
def get_saved_model_names():
    """
    Checks the MODEL_DIRECTORY to see if any models are saved there
    :return: bool - True if any models are saved, False if no models saved
    """
    return os.listdir(MODEL_DIRECTORY)


# TODO: refactor code to be more consistent - do along wigth todo above to add logic comparing data to models
def get_file_names(directory):
    file_names_with_extensions = os.listdir(directory)
    file_names = {get_file_name_from_full_path(file_name) for file_name in file_names_with_extensions}
    return file_names


def get_full_paths(directory):
    file_names = os.listdir(directory)
    file_paths = [directory + file_name for file_name in file_names]
    return file_paths


MODEL_NAMES = get_file_names(DATA_DIRECTORY)

"""===MODEL=TRAINING=AND=TEXT=GENERATION============================================================================"""


def create_single_model(path):
    """
    Creates a markov text generation model from the text file in the given path
    :param path: path of the text file to train the markov model on
    :return: number of lines used to train model, markovify model
    """
    with open(path, 'r') as f:
        text = f.read()
    # TODO: Sanitisation check?
    text_lines = text.split("\n")
    text_lines_shortened = text_lines[:MAX_NUMBER_TRAINING_LINES_PER_MODEL]
    text = "\n".join(text_lines_shortened)
    model = markovify.NewlineText(text)
    no_lines_in_model = len(text.split("\n"))
    return no_lines_in_model, model


def combine_models(single_models):
    """
    Combine a dictionary containing single trained markovify models as values
    :param single_models: dict {standardised_file_name: tuple(length of training dataset, markovify model) }
    :return:
    """
    # Create combined models from all possible combinations of the different data sources
    NUMBER_OF_MODELS = len(single_models)
    # MODEL_NAMES = set(single_models.keys())

    combined_models = {}
    for number_of_models_to_combine in range(1, NUMBER_OF_MODELS + 1):
        model_name_combinations = combinations(MODEL_NAMES, number_of_models_to_combine)
        for name_combination in model_name_combinations:
            models_to_combine_with_lengths = [single_models[model_name] for model_name in name_combination]
            lengths_of_models, models_to_combine = zip(*models_to_combine_with_lengths)
            # Use lengths of models to normalise model weightings so all models equally weighted in combined model
            min_model_length = min(lengths_of_models)
            model_normalisation_factors = [min_model_length/length for length in lengths_of_models]
            combined_model = markovify.combine(models_to_combine, model_normalisation_factors)
            # Compile for faster text generation later
            combined_model.compile(inplace=True)
            combined_model_index = get_combined_model_index(name_combination)
            combined_models[combined_model_index] = combined_model
            # Save model
            with open(f"{MODEL_DIRECTORY}{combined_model_index}", "w") as f:
                json_model = combined_model.to_json()
                f.write(json_model)

    return combined_models


def create_models():
    # Get list of all files in data directory
    data_file_paths = get_full_paths(DATA_DIRECTORY)

    # Create separate models for each data file
    # create_single_model(...) returns a tuple with (no_lines_model_trained_on, model)
    print("Training single models")
    single_models = {get_file_name_from_full_path(path): create_single_model(path) for path in data_file_paths}
    print("Finished training single models")

    print("Combining models")
    combined_models = combine_models(single_models)
    print("Finished combining and saving models")

    return combined_models


def load_models():
    print("Loading models from directory")
    # Get list of all files in model directory
    model_file_names = os.listdir(MODEL_DIRECTORY)

    # Load models
    combined_models = {}
    for model_name in model_file_names:
        print(f"\tLoading: {model_name}")
        model_path = MODEL_DIRECTORY + model_name
        with open(model_path, "r") as f:
            json_model = f.read()

        combined_model = markovify.Text.from_json(json_model)

        combined_models[model_name] = combined_model

    print("All models loaded")

    return combined_models


# Define some special words from the tweet to ignore
special_tweet_words = ["TweetInspiredBy"]
def match_dataset_names_from_string(text):
    """
    Expects input text to already be sanitised (lower case, special characters removed)
    :param text: string with space separated list of datasets
    :return: set( datasets specified in the text that match loaded datasets )
    """
    words = set(text.split(" "))
    words -= {special_word.lower() for special_word in special_tweet_words}

    matching_datasets = words.intersection(MODEL_NAMES)

    if not matching_datasets:
        raise NoMatchingDatasetsException(", ".join(words))

    return matching_datasets


def generate_text_from_specified_datasets(datasets: str, generated_text_length=263):
    dataset_names = match_dataset_names_from_string(datasets)
    model_index = get_combined_model_index(dataset_names)
    model = combined_models[model_index]
    response_text = model.make_short_sentence(generated_text_length)
    return response_text


# Run this file to generate and test models locally. Call generate_text_from_specified_datasets("dataset1 dataset2")
force_retraining_of_models = False
if get_saved_model_names() and not force_retraining_of_models:
    combined_models = load_models()
else:
    combined_models = create_models()
