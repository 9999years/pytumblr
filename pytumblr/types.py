from collections import UserList
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Dict, Any


@dataclass
class Link:
    """
    An objects in a _links hash
    """
    href: str
    type: str


@dataclass
class NavigationLink(Link):
    type = field(default='navigation', repr=False)


@dataclass
class ActionLink(Link):
    method: str
    query_params: Dict[str, Any]
    type = field(default='action', repr=False)


_link_classes = {'navigation': NavigationLink,
                 'action': ActionLink}


@dataclass
class Tag:
    tag: str
    is_tracked: bool
    featured: bool
    thumb_url: str = None


@dataclass
class Blog:
    name: str
    updated: int
    title: str
    description: str
    url: str


@dataclass
class BlogInfo(Blog):
    posts: int
    ask: bool
    ask_anon: bool
    likes: int
    is_blocked_from_primary: bool
    url: None = None


@dataclass
class UserBlogInfo:
    url: str
    title: str
    primary: bool
    followers: int
    tweet: str
    facebook: str
    type: str  # public or private


@dataclass
class UserInfo:
    following: int
    default_post_format: str
    name: str
    likes: int
    blogs: List[UserBlogInfo]


@dataclass
class Avatar:
    avatar_url: str


@dataclass(eq=False)
class Post:
    id: int
    type: str
    blog: BlogInfo
    blog_name: str
    post_url: str
    timestamp: int
    date: datetime
    format: str  # html or markdown
    reblog_key: str
    tags: List[str]
    total_posts: int
    bookmarks: bool = False
    mobile: bool = False
    source_url: str = None
    source_title: str = None
    liked: bool = None
    state: str = None
    is_blocks_post_format: bool = False


@dataclass
class DashboardPost(Post):
    blog: None = None

@dataclass
class Submission(Post):
    slug: str
    timestamp: int
    short_url: str
    post_author: str = None
    is_submission: bool = True
    anonymous_name: str = None
    anonymous_email: str = None
    state: str = 'submission'

@dataclass
class LegacyTextPost(Post):
    title: str = ''
    body: str = ''


@dataclass
class ImageSize:
    width: int
    height: int
    url: str


@dataclass
class Photo:
    caption: str
    alt_sizes: List[ImageSize]


@dataclass
class VerbosePhoto(Photo):
    original_size: ImageSize
    width: int
    height: int
    url: str


@dataclass
class LegacyPhotoPost(Post):
    """
    A photo or photoset post
    """
    caption: str = ''
    width: int = 0
    height: int = 0
    photos: List[Photo] = field(default_factory=list)


@dataclass
class LegacyQuotePost(Post):
    text: str = ''
    # HTML source
    source: str = str


@dataclass
class LegacyLinkPost(Post):
    title: str = ''
    description: str = ''
    url: str = ''
    author: str = ''
    excerpt: str = ''
    publisher: str = ''
    photos: List[VerbosePhoto] = field(default_factory=list)


@dataclass
class ChatLine:
    name: str
    label: str
    phrase: str


@dataclass
class LegacyChatPost(Post):
    title: str = ''
    body: str = ''
    dialogue: List[ChatLine] = field(default_factory=list)


@dataclass
class LegacyAudioPost(Post):
    caption: str = ''
    player: str = ''
    plays: int = 0
    album_art: str = ''
    artist: str = ''
    album: str = ''
    track_name: str = ''
    track_number: int = 0
    year: int = 0


@dataclass
class VideoPlayer:
    width: int
    embed_code: str


@dataclass
class LegacyVideoPost(Post):
    caption: str = None
    player: List[Any] = field(default_factory=[])


@dataclass
class LegacyAnswerPost(Post):
    asking_name: str = ''
    asking_url: str = ''
    question: str = ''
    answer: str = ''


@dataclass
class Likes:
    liked_posts: List[Post]
    liked_count: int


@dataclass
class Following:
    blogs: List[BlogInfo]
    total_blogs: int


@dataclass
class Follower:
    name: str
    following: bool
    url: str
    updated: int


@dataclass(init=False)
class Followers(UserList):
    total_users: int
    users: List[Follower]

    def __init__(self, initlist=None):
        super().__init__(initlist)


@dataclass
class Reblog:
    comment: str
    tree_html: str


@dataclass
class Dashboard:
    posts: List[DashboardPost]


@dataclass
class Posts:
    posts: List[Post]

@dataclass
class BlogPosts(Posts):
    blog: BlogInfo
