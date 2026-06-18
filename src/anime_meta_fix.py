import json
from dataclasses import dataclass
from typing import List

@dataclass
class AnimeMetadata:
    title: str
    genre: str
    episodes: int

def detect_metadata_errors(metadata: List[AnimeMetadata]) -> List[AnimeMetadata]:
    errors = []
    for meta in metadata:
        if not meta.title or not meta.genre or meta.episodes <= 0:
            errors.append(meta)
    return errors

def correct_metadata_errors(metadata: List[AnimeMetadata]) -> List[AnimeMetadata]:
    corrected = []
    for meta in metadata:
        if not meta.title:
            meta.title = "Unknown"
        if not meta.genre:
            meta.genre = "Unknown"
        if meta.episodes <= 0:
            meta.episodes = 1
        corrected.append(meta)
    return corrected

def reorder_metadata(metadata: List[AnimeMetadata]) -> List[AnimeMetadata]:
    return sorted(metadata, key=lambda x: x.title)

def integrate_with_jellyfin(metadata: List[AnimeMetadata]) -> str:
    jellyfin_data = {"anime": []}
    for meta in metadata:
        jellyfin_data["anime"].append({
            "title": meta.title,
            "genre": meta.genre,
            "episodes": meta.episodes
        })
    return json.dumps(jellyfin_data)
