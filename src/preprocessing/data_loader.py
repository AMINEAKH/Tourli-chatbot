import json
import os

# Path to the processed data folder
DATA_PATH = os.path.join(os.path.dirname(__file__), '../../data/processed')

# List of all JSON files to load
DATA_FILES = [
    'cleaned_dataset.json',
    'edge_cases_cleaned.json',
    'worldcities.json'
]

def load_json(filename):
    """
    Load a JSON file from the processed data folder.
    """
    file_path = os.path.join(DATA_PATH, filename)
    with open(file_path, 'r', encoding='utf-8') as f:
        return json.load(f)

def load_all_data():
    """
    Load all processed JSON datasets into a dictionary.
    """
    data = {}
    for file_name in DATA_FILES:
        key_name = file_name.replace('.json', '')  # e.g., cleaned_dataset
        data[key_name] = load_json(file_name)
    return data

if __name__ == "__main__":
    all_data = load_all_data()
    print("=== Loaded Datasets Summary ===")
    for k, v in all_data.items():
        print(f"{k}: {len(v)} entries")
