import yaml


def load_yml(file):
    with open(file, 'r', encoding='utf-8') as f:
        try:
            return yaml.safe_load(f)
        except yaml.YAMLError as e:
            print(e)


def load_txt(file):
    with open(file, 'r', encoding='utf-8') as f:
        return f.read().splitlines()
