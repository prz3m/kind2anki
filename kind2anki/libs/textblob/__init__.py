import os

__version__ = '0.11.1'
__license__ = 'MIT'
__author__ = 'Steven Loria'

PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))

# from .blob import TextBlob, Word, Sentence, Blobber, WordList
from .blob import TextBlob

__all__ = [
    'TextBlob',
    'Word',
    'Sentence',
    'Blobber',
    'WordList',
]
