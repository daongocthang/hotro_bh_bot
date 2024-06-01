import json
import os
from utils import ROOT_DIR

from utils import load

credentials = load.yml(os.path.join(ROOT_DIR, 'credentials.yml'))

f = open(os.path.join(ROOT_DIR, 'firebase.json'), 'r')
fb_config = json.load(f)
f.close()
