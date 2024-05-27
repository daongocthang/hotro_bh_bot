from underthesea import word_tokenize
import numpy as np


def tokenize(sentence):
    return word_tokenize(sentence)


def bag_of_words(tokenized_sentence, words):
    bag = np.zeros(len(words), dtype=np.float32)
    for i, w in enumerate(words):
        if w in tokenized_sentence:
            bag[i] = 1

    return bag
