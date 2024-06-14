# -*- coding: utf-8 -*-

import nltk
import re
import json
import yaml

from nltk.corpus import stopwords
from pathlib import Path

STOPWORDS = stopwords.words("english")

# If we put this here we only have to instantiate it once...
wnl = nltk.WordNetLemmatizer()

# List of terms we want to NOT lemmatize for some reason
KEEP_AS_IS = [
    "accounts",
    "claims",
    "communications",
    "complaints",
    "events",
    "goods",
    "grounds",
    "lettings",
    "loans",
    "operations",
    "relations",
    "sales",
    "services",
    "systems",
    "years",
]


def load_config():
    """parse configuration file

    Returns
    -------
    dict
        dictionary with each section of the yaml file as the key"""
    with open("config.yml", "r") as f:
        config = yaml.safe_load(f)
    return config


config = load_config()
script_dir = Path(config["dirs"]["script_dir"])
parent_dir = Path(config["dirs"]["parent_dir"])
lookup_dir = Path(config["dirs"]["lookup_dir"])

### This needs to be moved into a class
### Add the default of don't do known_only/expand_dict
### Would have suggested just putting into simple_clean() but that works row by row (lots of closing/reopening files).


class Cleaner:
    def __init__(self, scheme=config["user"]["scheme"]):
        """
        set scheme and load known_words json
        Parameters
        ----------
        scheme:str
            string containing scheme
        """

        self.scheme = scheme
        self.advanced = True

        try:
            with open(
                lookup_dir / f"{scheme.lower()}/known_words_dict.json", "r"
            ) as infile:
                self.known_words_dict = json.load(infile)
            with open(lookup_dir / f"{scheme.lower()}/expand_dict.json", "r") as infile:
                self.expand_dict = json.load(infile)
        except FileNotFoundError:
            self.advanced = False

    def lemmatize(self, string):
        """Helper, handles generating lemmas. Uses NLTK's WordNetLemmatizer

        Returns: List of lemmatised tokens for an inputted string
        """
        return [
            wnl.lemmatize(token) if token not in KEEP_AS_IS else token
            for token in string.split()
        ]

    def simple_clean(self, text: str, advanced=None, known_only=True):
        """
        Takes string as input, cleans, lowercases, tokenizes and lemmatises,
        before replacing some known tokens with synonyms and optionally filtering
        to only known (job title) words.

        Keyword arguments:
            text -- String representing human freetext to clean up
            known_only -- Bool, whether to filter to only known job title words
                          (default True)
            advanced -- Bool. Controls whether to apply lemmatisation and known
                          words removal.
        """

        if not advanced:
            advanced = self.advanced

        # Handle unexpected datatypes
        if type(text) is not str:
            raise TypeError("simple_clean expects a string")

        text = re.sub(r"<.*?>", " ", text)  # Clean out any HTML tags
        text = re.sub(r"[^a-z ]", " ", text.lower())  # Keep only letters & spaces
        text = re.sub(" +", " ", text).strip()  # Remove excess whitespace

        # Lemmatise tokens

        if advanced:
            tokens = self.lemmatize(text)
            # Replace some lemmas with known synonyms, if known
            tokens = [self.expand_dict.get(token, token) for token in tokens]

            # Filter out words not present in the vocabulary we're matching to
            if known_only:
                tokens = [
                    token
                    for token in tokens
                    if token in list(self.known_words_dict.keys())
                ]

                # Filter out stopwords
                tokens = [token for token in tokens if token not in STOPWORDS]
            return " ".join(tokens)

        return text
