import asyncio
import aiohttp
import urllib.parse
import json
from .result import VideoResult


class YoutubeSearch:
    def __init__(self, search_terms: str, max_results=None, language=None, region=None):
        self.search_terms = search_terms
        self.max_results = max_results
        self.language = language
        self.region = region
        self.session = None
        self.videos = None

    async def _setup_session(self):
        self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar())
        if self.language:
            language = f"&hl={self.language}"
        else:
            language = ""
        if self.region:
            region = f"&gl={self.region}"
        else:
            region = ""
        pref = "&".join(filter(None, [language, region]))
        self.session.cookie_jar.update_cookies({"PREF": pref})

    async def search(self) -> list[VideoResult]:
        await self._setup_session()
        self.videos = await self._search()
        await self.session.close()
        return self.videos

    async def _search(self) -> list[VideoResult]:
        BASE_URL = "https://youtube.com"
        if self.search_terms.startswith(BASE_URL):
            url = self.search_terms
        else:
            encoded_search = urllib.parse.quote_plus(self.search_terms)
            url = f"{BASE_URL}/results?search_query={encoded_search}"
        response = await self._get_response_with_retry(url)
        results = await self._parse_html(response)
        if self.max_results is not None and len(results) > self.max_results:
            return results[: self.max_results]
        return results

    async def _get_response_with_retry(self, url):
        while True:
            async with self.session.get(url) as response:
                response_text = await response.text()
                if "ytInitialData" in response_text:
                    return response_text
                await asyncio.sleep(0.1)


    async def _parse_html(self, response):
        results = []
        start = response.index("ytInitialData") + len("ytInitialData") + 3
        end = response.index("};", start) + 1
        json_str = response[start:end]
        data = json.loads(json_str)

        for contents in data["contents"]["twoColumnSearchResultsRenderer"][
            "primaryContents"
        ]["sectionListRenderer"]["contents"]:
            for video in contents["itemSectionRenderer"]["contents"]:
                res = {}
                if "videoRenderer" in video.keys():
                    video_data = video.get("videoRenderer", {})
                    res["id"] = video_data.get("videoId", None)
                    res["thumbnails"] = [
                        thumb.get("url", None)
                        for thumb in video_data.get("thumbnail", {}).get(
                            "thumbnails", [{}]
                        )
                    ]
                    res["title"] = (
                        video_data.get("title", {})
                        .get("runs", [[{}]])[0]
                        .get("text", None)
                    )
                    res["long_desc"] = (
                        video_data.get("descriptionSnippet", {})
                        .get("runs", [{}])[0]
                        .get("text", None)
                    )
                    res["channel"] = (
                        video_data.get("longBylineText", {})
                        .get("runs", [[{}]])[0]
                        .get("text", None)
                    )
                    res["duration"] = video_data.get("lengthText", {}).get(
                        "simpleText", 0
                    )
                    res["views"] = video_data.get("viewCountText", {}).get(
                        "simpleText", 0
                    )
                    res["publish_time"] = video_data.get("publishedTimeText", {}).get(
                        "simpleText", 0
                    )
                    res["url_suffix"] = (
                        video_data.get("navigationEndpoint", {})
                        .get("commandMetadata", {})
                        .get("webCommandMetadata", {})
                        .get("url", None)
                    )
                    res["yt_url"] = f"https://youtube.com{res['url_suffix']}"
                    results.append(VideoResult(res))

            if results:
                return results
        return results

    def to_dict(self, clear_cache=True):
        if self.videos is None:
            return None
        result = [video.to_dict() for video in self.videos]
        if clear_cache:
            self.videos = None
        return result

    def to_json(self, clear_cache=True):
       if self.videos is None:
            return None
       result = json.dumps({"videos": [video.to_dict() for video in self.videos]})
       if clear_cache:
           self.videos = None
       return result