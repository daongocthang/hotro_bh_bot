import os
from . import ROOT_DIR

from torchbot.utils import load_yml

credentials = load_yml(os.path.join(ROOT_DIR, 'credentials.yml'))
