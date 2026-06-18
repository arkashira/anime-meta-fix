import pytest
import json
from anime_meta_fix import AnimeMetadata, detect_metadata_errors, correct_metadata_errors, reorder_metadata, integrate_with_jellyfin

def test_detect_metadata_errors():
    metadata = [
        AnimeMetadata("Title1", "Genre1", 10),
        AnimeMetadata("", "Genre2", 20),
        AnimeMetadata("Title3", "", 30),
        AnimeMetadata("Title4", "Genre4", 0)
    ]
    errors = detect_metadata_errors(metadata)
    assert len(errors) == 3
    assert errors[0].title == ""
    assert errors[1].genre == ""
    assert errors[2].episodes == 0

def test_correct_metadata_errors():
    metadata = [
        AnimeMetadata("Title1", "Genre1", 10),
        AnimeMetadata("", "Genre2", 20),
        AnimeMetadata("Title3", "", 30),
        AnimeMetadata("Title4", "Genre4", 0)
    ]
    corrected = correct_metadata_errors(metadata)
    assert corrected[0].title == "Title1"
    assert corrected[1].title == "Unknown"
    assert corrected[2].genre == "Unknown"
    assert corrected[3].episodes == 1

def test_reorder_metadata():
    metadata = [
        AnimeMetadata("Title3", "Genre3", 30),
        AnimeMetadata("Title1", "Genre1", 10),
        AnimeMetadata("Title2", "Genre2", 20)
    ]
    reordered = reorder_metadata(metadata)
    assert reordered[0].title == "Title1"
    assert reordered[1].title == "Title2"
    assert reordered[2].title == "Title3"

def test_integrate_with_jellyfin():
    metadata = [
        AnimeMetadata("Title1", "Genre1", 10),
        AnimeMetadata("Title2", "Genre2", 20)
    ]
    jellyfin_data = integrate_with_jellyfin(metadata)
    assert json.loads(jellyfin_data) == {
        "anime": [
            {"title": "Title1", "genre": "Genre1", "episodes": 10},
            {"title": "Title2", "genre": "Genre2", "episodes": 20}
        ]
    }
