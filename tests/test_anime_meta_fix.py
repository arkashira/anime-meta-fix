import json
import os
import tempfile
from anime_meta_fix import load_metadata, correct_metadata, save_metadata, AnimeMetadata

def test_load_metadata():
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, 'metadata.json')
        with open(file_path, 'w') as file:
            json.dump({'title': 'test', 'genre': 'action', 'episodes': 12}, file)
        metadata = load_metadata(file_path)
        assert metadata.title == 'test'
        assert metadata.genre == 'action'
        assert metadata.episodes == 12

def test_correct_metadata():
    metadata = AnimeMetadata('test', 'action', 12)
    corrected_metadata = correct_metadata(metadata)
    assert corrected_metadata.title == 'Test'
    assert corrected_metadata.genre == 'Action'
    assert corrected_metadata.episodes == 12

def test_save_metadata():
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, 'metadata.json')
        metadata = AnimeMetadata('Test', 'Action', 12)
        save_metadata(file_path, metadata)
        with open(file_path, 'r') as file:
            data = json.load(file)
            assert data['title'] == 'Test'
            assert data['genre'] == 'Action'
            assert data['episodes'] == 12

def test_main():
    with tempfile.TemporaryDirectory() as tmp_dir:
        file_path = os.path.join(tmp_dir, 'metadata.json')
        with open(file_path, 'w') as file:
            json.dump({'title': 'test', 'genre': 'action', 'episodes': 12}, file)
        import sys
        sys.argv = ['main.py', '--path', tmp_dir]
        from anime_meta_fix import main
        main()
        with open(file_path, 'r') as file:
            data = json.load(file)
            assert data['title'] == 'Test'
            assert data['genre'] == 'Action'
            assert data['episodes'] == 12
