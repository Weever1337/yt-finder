from yt_finder import YoutubeSearch


async def test_search():
    search = YoutubeSearch(
        "test",  # search query
        max_results=10,  # max results of the search
        language="en",  # video language
        region="US",  # Youtube region
        sleep_time=0.5,  # time to sleep between requests
        retry_count=3,  # number of retries per failed request
    )
    await search.search()

    # Print the results
    for video in search:
        print("=" * 20)
        # All the attributes of the VideoResult object
        print(f"Title: {video.title}")
        print(f"URL: {video.yt_url}")
        print(f"Channel: {video.channel}")
        print(f"Duration: {video.duration}")
        print(f"Views: {video.views}")
        print(f"Publish Time: {video.publish_time}")
        print(f"URL Suffix: {video.url_suffix}")
        print(f"ID: {video.id}")
        print(f"Thumbnails: {video.thumbnails}")
        print(f"Long Description: {video.long_desc}")
        print("=" * 20)

    # Convert the search object to a dictionary
    print(search.to_dict())

    # Convert the search object to a JSON string
    print(search.to_json())

    # Get the language of the search
    print(search.language)

    # Get the region of the search
    print(search.region)


if __name__ == "__main__":
    import asyncio

    asyncio.run(test_search())
