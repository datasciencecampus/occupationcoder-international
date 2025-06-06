from setuptools import setup, find_packages
import nltk

setup(name="occupationcoder", version="0.3.0", packages=find_packages())

nltk.download("stopwords")
nltk.download("wordnet")
