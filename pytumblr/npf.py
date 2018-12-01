from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Any, Dict

from . import types


@dataclass
class ShortBlogInfo(types.BlogInfo):
    """
    A blog which is only guaranteed to have a uuid
    """
    uuid: str

    title: str = None
    posts: int = None
    name: str = None
    updated: int = None
    description: str = None
    ask: bool = None
    ask_anon: bool = None
    likes: int = None
    is_blocked_from_primary: bool = None


@dataclass(eq=False)
class PostInfo(types.Post):
    """
    A Post which is only guaranteed to have an id
    """
    type: str = None
    blog_name: str = None
    post_url: str = None
    timestamp: int = None
    date: datetime = None
    format: str = None
    reblog_key: str = None
    tags: List[str] = None
    total_posts: int = None


@dataclass
class NeueObject:
    type: str


@dataclass
class ContentFormat(NeueObject):
    start: int
    end: int


@dataclass
class LinkFormat(ContentFormat):
    url: str


@dataclass
class MentionFormat(ContentFormat):
    blog: ShortBlogInfo


@dataclass
class ColorFormat(ContentFormat):
    hex: str


class ContentBlock(NeueObject):
    pass


@dataclass
class TextBlock(ContentBlock):
    text: str
    subtype: str = ''


@dataclass
class Media(NeueObject):
    url: str
    width: int = 0
    height: int = 0
    original_dimensions_missing: bool = None


class Attribution(NeueObject):
    pass


@dataclass
class PostAttribution(Attribution):
    url: str
    post: PostInfo
    blog: ShortBlogInfo


@dataclass
class BlogAttribution(Attribution):
    blog: ShortBlogInfo


@dataclass
class LinkAttribution(Attribution):
    url: str


@dataclass
class AppAttribution(Attribution):
    url: str
    app_name: str = None
    display_text: str = None
    logo: Media = None


@dataclass
class ImageBlock(ContentBlock):
    media: List[Media]
    colors: Dict[str, str] = field(default_factory=dict)
    feedback_token: str = ''
    poster: Media = None
    attribution: Attribution = None


@dataclass
class LinkBlock(ContentBlock):
    url: str
    title: str = None
    description: str = None
    author: str = None
    site_name: str = None
    display_url: str = None
    poster: Media = None


@dataclass
class MediaBlock(ContentBlock):
    """
    An embedded media block
    """
    provider: str
    url: str = None
    media: Media = None
    poster: List[Media] = None
    embed_html: str = None
    embed_url: str = None
    metadata: Dict[str, Any] = None
    attribution: Attribution = None


@dataclass
class AudioBlock(MediaBlock):
    title: str = None
    artist: str = None
    album: str = None


@dataclass
class VideoBlock(MediaBlock):
    can_autoplay_on_cellular: bool = None


class LayoutBlock(NeueObject):
    pass


IndexList = List[int]


@dataclass
class Display:
    blocks: IndexList
    mode: NeueObject


@dataclass
class RowsLayout(LayoutBlock):
    rows: List[IndexList]
    type: str = field(default='rows', init=False)
    display: List[dict] = None


@dataclass
class CondensedLayout(LayoutBlock):
    blocks: IndexList
    type: str = field(default='condensed', init=False)


@dataclass
class AskLayout(LayoutBlock):
    blocks: IndexList
    attribution: Attribution
    blog: ShortBlogInfo = None


@dataclass
class BrokenBlog:
    name: str
    avatar: types.Avatar


@dataclass
class Trail:
    content: List[ContentBlock]
    layout: List[LayoutBlock]

    broken_blog: BrokenBlog
    post: PostInfo = None
    blog: ShortBlogInfo = None


@dataclass
class NeuePostInfo:
    id: str


@dataclass
class NeuePost(NeuePostInfo):
    tumblelog_uuid: str
    content: List[ContentBlock]
    layout: List[LayoutBlock]

    parent_post_id: str = None
    parent_tumblelog_uuid: str = None
    reblog_key: str = None

    trail: List[Trail] = None
