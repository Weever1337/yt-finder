from yt_finder import YoutubeSearch


async def main():
    search = YoutubeSearch("python", max_results=5)
    results = search.search()
    print(results)

    for video in results:
        print("=" * 20)
        print(f"Title: {video.title}")
        print(f"URL: {video.yt_url}")
        print("=" * 20)


if __name__ == "__main__":
    import asyncio

    asyncio.run(main())
