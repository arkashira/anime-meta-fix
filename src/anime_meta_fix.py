import argparse
import json
import os
from dataclasses import dataclass

@dataclass
class AnimeMetadata:
    title: str
    genre: str
    episodes: int

def load_metadata(file_path):
    with open(file_path, 'r') as file:
        data = json.load(file)
        return AnimeMetadata(data['title'], data['genre'], data['episodes'])

def correct_metadata(metadata):
    # Simple correction logic: capitalize title and genre
    return AnimeMetadata(metadata.title.capitalize(), metadata.genre.capitalize(), metadata.episodes)

def save_metadata(file_path, metadata):
    with open(file_path, 'w') as file:
        json.dump({'title': metadata.title, 'genre': metadata.genre, 'episodes': metadata.episodes}, file)

def main():
    parser = argparse.ArgumentParser(description='Anime Meta Fix')
    parser.add_argument('--path', help='Media server directory path')
    args = parser.parse_args()

    for root, dirs, files in os.walk(args.path):
        for file in files:
            if file.endswith('.json'):
                file_path = os.path.join(root, file)
                metadata = load_metadata(file_path)
                corrected_metadata = correct_metadata(metadata)
                save_metadata(file_path, corrected_metadata)

if __name__ == '__main__':
    main()
