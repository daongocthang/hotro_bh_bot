import os
from utils import ROOT_DIR

from utils import load

credentials = load.yml(os.path.join(ROOT_DIR, 'credentials.yml'))
