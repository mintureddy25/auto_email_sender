import json
import os


def load_json(filepath):
    if not os.path.exists(filepath):
        return []
    try:
        with open(filepath, "r") as f:
            content = f.read()
        if not content.strip():
            return []
        return json.loads(content)
    except json.JSONDecodeError:
        return []


def save_json(filepath, data):
    os.makedirs(os.path.dirname(filepath), exist_ok=True)
    with open(filepath, "w") as f:
        json.dump(data, f, indent=2)


def append_to_json(filepath, entry):
    data = load_json(filepath)
    data.append(entry)
    save_json(filepath, data)
