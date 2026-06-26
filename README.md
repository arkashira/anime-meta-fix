# Anime Meta Fix

A tool to pull existing episode metadata from Jellyfin and compare it against an AI model.

## Usage

1. Create an instance of the `AnimeMetaFix` class with a valid API key.
2. Call the `retrieve_metadata` method to retrieve title, episode number, season, and file path for all anime series.
3. Store the metadata in a temporary in-memory cache using the `store_in_cache` method.
4. Retrieve the cached metadata using the `get_cached_metadata` method.

## Testing

Run the tests using `pytest` to ensure the implementation is correct.
