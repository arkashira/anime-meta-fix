import json
from dataclasses import dataclass
from typing import List, Dict

@dataclass
class AnimeMetadata:
    title: str
    genre: str
    description: str

class AnimeMetaFix:
    def __init__(self, metadata: List[AnimeMetadata]):
        self.metadata = metadata

    def detect_incorrect_metadata(self) -> List[AnimeMetadata]:
        incorrect_metadata = []
        for metadata in self.metadata:
            if not metadata.title or not metadata.genre or not metadata.description:
                incorrect_metadata.append(metadata)
        return incorrect_metadata

    def suggest_corrections(self, incorrect_metadata: List[AnimeMetadata]) -> List[AnimeMetadata]:
        corrections = []
        for metadata in incorrect_metadata:
            corrected_metadata = AnimeMetadata(
                title=metadata.title if metadata.title else "Unknown Title",
                genre=metadata.genre if metadata.genre else "Unknown Genre",
                description=metadata.description if metadata.description else "Unknown Description"
            )
            corrections.append((metadata, corrected_metadata))
        return corrections

    def apply_corrections(self, corrections: List[tuple]) -> List[AnimeMetadata]:
        corrected_metadata = []
        for metadata, corrected_metadata_item in corrections:
            corrected_metadata.append(corrected_metadata_item)
        return corrected_metadata
