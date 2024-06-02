import json
import os
from utils import ROOT_DIR

from utils import loader

credentials = loader.load_yml(os.path.join(ROOT_DIR, 'credentials.yml'))

f = open(os.path.join(ROOT_DIR, 'firebase.json'), 'r')
fb_config = json.load(f)
f.close()
