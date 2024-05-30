import os
import random
from torchbot.prediction import predict
from utils.load import yml

__basedir = os.path.dirname(os.path.abspath(__file__))
intents = yml(os.path.join(__basedir, 'intents.yml'))['intents']

print("Let's chat! (type '/stop' to exit)")
while True:
    # sentence = "do you use credit cards?"
    sentence = input('You: ')
    if sentence.lower() == '/stop':
        break
    prob, tag = predict(sentence)
    print("prob:", prob.item(), "tag:", tag)
    if prob.item() > 0.9:
        for intent in intents:
            if tag == intent['tag']:
                print(f'Bot:', random.choice(intent['responses']))
                break
    else:
        print(f'Bot: Tôi không hiểu...')
