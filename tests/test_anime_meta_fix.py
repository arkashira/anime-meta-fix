from anime_meta_fix import AnimeMetadata, AnimeMetaFix
import pytest

@pytest.fixture
def metadata():
    return [
        AnimeMetadata("Title 1", "Genre 1", "Description 1"),
        AnimeMetadata("", "Genre 2", "Description 2"),
        AnimeMetadata("Title 3", "", "Description 3"),
        AnimeMetadata("Title 4", "Genre 4", "")
    ]

def test_detect_incorrect_metadata(metadata):
    anime_meta_fix = AnimeMetaFix(metadata)
    incorrect_metadata = anime_meta_fix.detect_incorrect_metadata()
    assert len(incorrect_metadata) == 3

def test_suggest_corrections(metadata):
    anime_meta_fix = AnimeMetaFix(metadata)
    incorrect_metadata = anime_meta_fix.detect_incorrect_metadata()
    corrections = anime_meta_fix.suggest_corrections(incorrect_metadata)
    assert len(corrections) == 3

def test_apply_corrections(metadata):
    anime_meta_fix = AnimeMetaFix(metadata)
    incorrect_metadata = anime_meta_fix.detect_incorrect_metadata()
    corrections = anime_meta_fix.suggest_corrections(incorrect_metadata)
    corrected_metadata = anime_meta_fix.apply_corrections(corrections)
    assert len(corrected_metadata) == 3

def test_accuracy():
    metadata = [
        AnimeMetadata("Title 1", "Genre 1", "Description 1"),
        AnimeMetadata("", "Genre 2", "Description 2"),
        AnimeMetadata("Title 3", "", "Description 3"),
        AnimeMetadata("Title 4", "Genre 4", "")
    ]
    anime_meta_fix = AnimeMetaFix(metadata)
    incorrect_metadata = anime_meta_fix.detect_incorrect_metadata()
    corrections = anime_meta_fix.suggest_corrections(incorrect_metadata)
    corrected_metadata = anime_meta_fix.apply_corrections(corrections)
    assert len(incorrect_metadata) / len(metadata) >= 0.5
    assert len(corrections) / len(incorrect_metadata) == 1
