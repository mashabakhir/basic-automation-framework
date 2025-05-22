import json


__all__ = ['load_json', 'LOGIN', 'SELECTORS']

LOGIN = "config/login.json"
SELECTORS = "config/selectors.json"


def load_json(file_path):
    with open(file_path, "r") as file:
        data = json.load(file)
    return data