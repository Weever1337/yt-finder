from typing import List, Optional, Dict, Any


class VideoResult:
    def __init__(self, data: Dict[str, Any]):
        self.data: Dict[str, Any] = data

    def get_id(self) -> Optional[str]:
        return self.data.get("id")

    def get_thumbnails(self) -> List[Optional[str]]:
        return self.data.get("thumbnails", [])

    def get_title(self) -> Optional[str]:
        return self.data.get("title")

    def get_long_desc(self) -> Optional[str]:
        return self.data.get("long_desc")

    def get_channel(self) -> Optional[str]:
        return self.data.get("channel")

    def get_duration(self) -> Optional[str]:
        return self.data.get("duration")

    def get_views(self) -> Optional[str]:
        return self.data.get("views")

    def get_publish_time(self) -> Optional[str]:
        return self.data.get("publish_time")

    def get_url_suffix(self) -> Optional[str]:
        return self.data.get("url_suffix")

    def get_yt_url(self) -> Optional[str]:
        return self.data.get("yt_url")

    def to_dict(self) -> Dict[str, Any]:
        return self.data