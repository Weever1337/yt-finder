# yt_search - Fork of youtube-search

Python function for searching for youtube videos to avoid using their heavily rate-limited API

To avoid using the API, this uses the form on the youtube homepage and scrapes the resulting page.

## Example Usage

For a basic search (and all of the current functionality), you can use the search tool as follows:

```pip install yt-search```

```python
from yt_search import YoutubeSearch
import asyncio

async def main():
    search = YoutubeSearch("python", max_results=5, language="en", region="US")
    videos = await search.search()
    for video in videos:
        print("=" * 20)
        print(f"Title: {video['title']}")
        print(f"URL: {video['yt_url']}")
        print("=" * 20)

if __name__ == "__main__":
    asyncio.run(main())
```
