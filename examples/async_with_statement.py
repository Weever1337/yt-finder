from yt_finder import YoutubeSearch


async def test_search():
    async with YoutubeSearch("python", max_results=10) as search:
        videos = await search.search()
        for video in videos:
            print("=" * 20)
            print(f"Title: {video.title}")
            print(f"URL: {video.yt_url}")
            print("=" * 20)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_search())
