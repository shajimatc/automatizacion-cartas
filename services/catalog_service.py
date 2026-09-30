import json
from pathlib import Path


DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def load_json_file(filename):
    file_path = DATA_DIR / filename

    with file_path.open("r", encoding="utf-8") as file:
        return json.load(file)


def load_companies():
    return load_json_file("companies.json")


def load_areas():
    return load_json_file("areas.json")