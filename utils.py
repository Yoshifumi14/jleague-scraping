import yaml


def load_config(filename):
    with open(filename) as f:
        return yaml.safe_load(f)
