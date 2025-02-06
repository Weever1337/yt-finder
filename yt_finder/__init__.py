import sys
from typing import Any, Dict, List, Optional

import asyncio
import aiohttp
import urllib.parse
import json

from loguru import logger

from .result import VideoResult

__all__ = ["YoutubeSearch", "VideoResult"]


class YoutubeSearch:
    def __init__(
        self,
        search_terms: str,
        max_results: Optional[int] = None,
        language: Optional[str] = None,
        region: Optional[str] = None,
        sleep_time: Optional[float] = 0.5,
        retry_count: Optional[int] = 5,
    ):
        """
        Initialize a YoutubeSearch object.

        Parameters
        ----------
        search_terms : str
            The search terms to use when searching youtube.
        max_results : Optional[int], optional
            The maximum number of search results to return. Defaults to None.
        language : Optional[str], optional
            The language to use when searching youtube. Defaults to None.
        region : Optional[str], optional
            The region to use when searching youtube. Defaults to None.
        sleep_time : Optional[float], optional
            The time to sleep between retries when making a request. Defaults to 0.5.
        retry_count : Optional[int], optional
            The maximum number of times to retry a request. Defaults to 5.
        """
        self.search_terms = search_terms
        self.max_results = max_results
        self.language = language
        self.region = region

        self._session = None
        self._videos: Optional[List[VideoResult]] = None
        self.BASE_URL = "https://youtube.com"
        self.RETRY_COUNT = retry_count
        self.SLEEP_TIME = sleep_time

        # JSON parsing constants
        self._YT_INITIAL_DATA_MARKER = "ytInitialData"
        self._JSON_END_MARKER = "};"
        self._JSON_START_OFFSET = len(self._YT_INITIAL_DATA_MARKER) + 3

        self.logger = None
        self.setup_logger()

    def setup_logger(self):
        self.logger = logger
        self.logger.add(
            sys.stderr,
            level="DEBUG",
            format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>[YT-Finder]</cyan> - <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        )

    async def __aenter__(self) -> "YoutubeSearch":
        self._async_context_manager = True
        await self._setup_session()
        return self

    async def __aexit__(self, exc_type, exc, tb) -> None:
        if self._session:
            await self.session.close()
            self.session = None
        return

    async def _setup_session(self):
        self.session = aiohttp.ClientSession(cookie_jar=aiohttp.CookieJar())

        language = f"&hl={self.language}" if self.language else ""
        region = f"&gl={self.region}" if self.region else ""

        pref_params = "&".join(filter(None, [language, region]))
        if pref_params:
            self.session.cookie_jar.update_cookies({"PREF": pref_params})

    @property
    def session(self) -> Optional[aiohttp.ClientSession]:
        return self._session

    @session.setter
    def session(self, value: aiohttp.ClientSession):
        self._session = value

    @property
    def videos(self) -> Optional[List[VideoResult]]:
        return self._videos

    @videos.setter
    def videos(self, value: List[VideoResult]):
        self._videos = value

    async def search(self) -> list[VideoResult]:
        """
        Perform the search and return a list of VideoResult objects.

        This method is a coroutine.

        If an aiohttp.ClientSession has not been set up yet (i.e. this instance was not
        created with 'async with YoutubeSearch(...)' or YoutubeSearch._setup_session()
        has not been called yet), it will be set up.

        The search will be performed using the search terms provided when this instance
        was created.

        The list of VideoResult objects found will be stored in the YoutubeSearch.videos
        property.

        If no results are found, an empty list will be returned.
        """
        if not hasattr(self, "_async_context_manager"):
            await self._setup_session()
            session_created = True

        self._videos = await self._search()
        results = self._videos or []

        if (
            not hasattr(self, "_async_context_manager")
            and session_created
            and self._session
        ):
            await self.session.close()
            self.session = None

        return results

    async def _search(self) -> list[VideoResult]:
        encoded_search = urllib.parse.quote_plus(self.search_terms)
        url = (
            f"{self.BASE_URL}/results?search_query={encoded_search}"
            if not self.search_terms.startswith(self.BASE_URL)
            else self.search_terms
        )

        response = await self._get_response_with_retry(url)
        results = await self._parse_html(response)

        if self.max_results and results and len(results) > self.max_results:
            return results[: self.max_results]
        return results

    async def _get_response_with_retry(self, url: str) -> str:
        for attempt in range(self.RETRY_COUNT):
            try:
                async with self.session.get(url) as response:
                    response.raise_for_status()
                    response_text = await response.text()
                    if self._YT_INITIAL_DATA_MARKER in response_text:
                        return response_text
                    await asyncio.sleep(self.SLEEP_TIME)
            except aiohttp.ClientError as e:
                if attempt < self.RETRY_COUNT - 1:
                    self.logger.warning(
                        f"Connection error: {e}. Retrying... ({attempt + 1}/{self.RETRY_COUNT})"
                    )
                    await asyncio.sleep(self.SLEEP_TIME)
                else:
                    self.logger.error(
                        f"Connection error: {e}. Max retries reached. Last error message: {e}"
                    )
                    raise e

        await self.session.close()
        raise Exception(
            f"Could not get ytInitialData from YouTube after {self.RETRY_COUNT} retries"
        )

    def _extract_text_from_runs(self, data: Dict, keys: List[str]) -> Optional[str]:
        runs = data.get(*keys, {}).get("runs", [])

        if runs and runs[0]:
            return runs[0].get("text")

        return None

    def _extract_video_data(self, video_renderer: Dict) -> Optional[Dict[str, Any]]:
        video_id = video_renderer.get("videoId")
        if not video_id:
            return None

        thumbnails = [
            thumb.get("url")
            for thumb in video_renderer.get("thumbnail", {}).get("thumbnails", [])
            if thumb.get("url")
        ]
        title = self._extract_text_from_runs(video_renderer, ["title"])
        long_desc = self._extract_text_from_runs(video_renderer, ["descriptionSnippet"])
        channel = self._extract_text_from_runs(video_renderer, ["longBylineText"])
        duration = video_renderer.get("lengthText", {}).get("simpleText")
        views = video_renderer.get("viewCountText", {}).get("simpleText")
        publish_time = video_renderer.get("publishedTimeText", {}).get("simpleText")

        url_suffix = (
            video_renderer.get("navigationEndpoint", {})
            .get("commandMetadata", {})
            .get("webCommandMetadata", {})
            .get("url")
        )
        yt_url = f"{self.BASE_URL}{url_suffix}" if url_suffix else None

        return {
            "id": video_id,
            "thumbnails": thumbnails,
            "title": title,
            "long_desc": long_desc,
            "channel": channel,
            "duration": duration,
            "views": views,
            "publish_time": publish_time,
            "url_suffix": url_suffix,
            "yt_url": yt_url,
        }

    async def _parse_html(self, response):
        results: List[VideoResult] = []

        try:
            start_index = (
                response.index(self._YT_INITIAL_DATA_MARKER) + self._JSON_START_OFFSET
            )
            end_index = response.index(self._JSON_END_MARKER, start_index) + 1
            json_str = response[start_index:end_index]
            data = json.loads(json_str)
        except ValueError as e:
            self.logger.error(f"Could not find JSON data in response: {e}")
            return results
        except Exception as e:
            self.logger.error(f"Error while parsing JSON: {e}")
            return results

        section_list = (
            data.get("contents", {})
            .get("twoColumnSearchResultsRenderer", {})
            .get("primaryContents", {})
            .get("sectionListRenderer", {})
            .get("contents", [])
        )

        if not section_list:
            return results

        for contents in section_list:
            item_section = contents.get("itemSectionRenderer", {}).get("contents", [])

            if not item_section:
                continue

            for video in item_section:
                video_renderer = video.get("videoRenderer", {})
                if not video_renderer:
                    continue

                if video_data := self._extract_video_data(video_renderer):
                    results.append(VideoResult.from_dict(video_data))

        return results

    def to_dict(self, clear_cache: bool = True) -> Optional[List[Dict[str, Any]]]:
        """
        Convert the list of VideoResult objects to a list of dictionaries.

        Parameters
        ----------
        clear_cache : bool, optional
            If True, clears the cached video results after conversion. Defaults to True.

        Returns
        -------
        Optional[List[Dict[str, Any]]]
            A list of dictionaries representing video results if available;
            otherwise, returns None if no video results exist.
        """

        if not self._videos:
            return None

        result = [video.to_dict() for video in self._videos]

        if clear_cache:
            self._videos = None

        return result

    def to_json(self, clear_cache: bool = True) -> Optional[str]:
        """
        Convert the list of VideoResult objects to a JSON string.

        Parameters
        ----------
        clear_cache : bool, optional
            If True, clears the cached video results after conversion. Defaults to True.

        Returns
        -------
        Optional[str]
            A JSON string representing the video results if available;
            otherwise, returns None if no video results exist.
        """
        if not self._videos:
            return None

        if result := self.to_dict(clear_cache=clear_cache):
            return json.dumps(result)

        return None
