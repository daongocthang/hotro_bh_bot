import os
from . import ROOT_DIR
import torch
from torchbot.model import NeuralNet
from torchbot.nltk_vi import tokenize, bag_of_words

device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
FILE = 'data/data.pth'

data = torch.load(os.path.join(ROOT_DIR, FILE))

input_size = data['input_size']
hidden_size = data['hidden_size']
output_size = data['output_size']
all_words = data['all_words']
tags = data['tags']
model_state = data['model_state']

model = NeuralNet(
    input_size,
    hidden_size,
    output_size
).to(device)
model.load_state_dict(model_state)
model.eval()


def predict(sentence):
    sentence = tokenize(sentence)
    x = bag_of_words(sentence, all_words)
    x = x.reshape(1, x.shape[0])
    x = torch.from_numpy(x).to(device)

    output = model(x)
    _, predicted = torch.max(output, dim=1)

    tag = tags[predicted.item()]

    probabilities = torch.softmax(output, dim=1)
    prob = probabilities[0][predicted.item()]

    return prob, tag
