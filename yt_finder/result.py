from typing import List, Optional, Dict, Any
from dataclasses import dataclass


@dataclass
class VideoResult:
    id: Optional[str]
    thumbnails: List[Optional[str]]
    title: Optional[str]
    long_desc: Optional[str]
    channel: Optional[str]
    duration: Optional[str]
    views: Optional[str]
    publish_time: Optional[str]
    url_suffix: Optional[str]
    yt_url: Optional[str]

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "VideoResult":
        return cls(
            id=data.get("id"),
            thumbnails=data.get("thumbnails", []),
            title=data.get("title"),
            long_desc=data.get("long_desc"),
            channel=data.get("channel"),
            duration=data.get("duration"),
            views=data.get("views"),
            publish_time=data.get("publish_time"),
            url_suffix=data.get("url_suffix"),
            yt_url=data.get("yt_url"),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "id": self.id,
            "thumbnails": self.thumbnails,
            "title": self.title,
            "long_desc": self.long_desc,
            "channel": self.channel,
            "duration": self.duration,
            "views": self.views,
            "publish_time": self.publish_time,
            "url_suffix": self.url_suffix,
            "yt_url": self.yt_url,
        }

    def __eq__(self, other: "VideoResult") -> bool:
        return self.to_dict() == other.to_dict()

    def __ne__(self, other: "VideoResult") -> bool:
        return not self.__eq__(other)

    def __repr__(self) -> str:
        return f"VideoResult({self.to_dict()})"
