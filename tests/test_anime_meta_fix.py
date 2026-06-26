from anime_meta_fix import AnimeMetaFix, AnimeEpisode

def test_authenticate_valid_api_key():
    anime_meta_fix = AnimeMetaFix("valid_api_key")
    assert anime_meta_fix.authenticate() == True

def test_authenticate_invalid_api_key():
    anime_meta_fix = AnimeMetaFix("invalid_api_key")
    assert anime_meta_fix.authenticate() == False

def test_retrieve_metadata_authenticated():
    anime_meta_fix = AnimeMetaFix("valid_api_key")
    metadata = anime_meta_fix.retrieve_metadata()
    assert len(metadata) == 2
    assert isinstance(metadata[0], AnimeEpisode)

def test_retrieve_metadata_unauthenticated():
    anime_meta_fix = AnimeMetaFix("invalid_api_key")
    metadata = anime_meta_fix.retrieve_metadata()
    assert len(metadata) == 0

def test_store_in_cache():
    anime_meta_fix = AnimeMetaFix("valid_api_key")
    metadata = [
        AnimeEpisode("Anime 1", 1, 1, "/path/to/anime1/episode1"),
        AnimeEpisode("Anime 2", 2, 1, "/path/to/anime2/episode2"),
    ]
    anime_meta_fix.store_in_cache(metadata)
    cached_metadata = anime_meta_fix.get_cached_metadata()
    assert len(cached_metadata) == 2
    assert isinstance(cached_metadata[0], AnimeEpisode)

def test_get_cached_metadata_empty_cache():
    anime_meta_fix = AnimeMetaFix("valid_api_key")
    cached_metadata = anime_meta_fix.get_cached_metadata()
    assert cached_metadata == []
